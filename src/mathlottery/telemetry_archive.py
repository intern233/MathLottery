"""Append-only public telemetry archives; bounded polling uses separate projections."""

from __future__ import annotations

import fcntl
import json
import os
import stat
from pathlib import Path

from mathlottery.models import now

MAX_EXPORT_BYTES = 64 * 1024 * 1024
MAX_RECORD_BYTES = 8192


def _line(value):
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n").encode()


def _write(fd, data):
    while data:
        written = os.write(fd, data)
        if written <= 0:
            raise OSError("Unable to append telemetry record")
        data = data[written:]


def append_public_record(path, record, *, earlier_history=False, attempt_number=None):
    """Append a caller-sanitized record, serialized across writers without rewriting.

    The final execution record may be replayed during crash recovery. Its local
    attempt number makes that final append idempotent without scanning the file.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = _line(record)
    if len(encoded) > MAX_RECORD_BYTES:
        raise ValueError("Telemetry record exceeds its size limit")
    fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError("Telemetry archive must be a regular private file")
        if info.st_size:
            os.lseek(fd, max(0, info.st_size - MAX_RECORD_BYTES), os.SEEK_SET)
            tail = os.read(fd, MAX_RECORD_BYTES)
            if attempt_number is not None and tail.endswith(b"\n"):
                try:
                    previous = json.loads(tail.rstrip(b"\n").rsplit(b"\n", 1)[-1])
                    if previous.get("record_type") == "resource_attempt" and previous.get("attempt", {}).get("number") == attempt_number:
                        return
                except (ValueError, AttributeError, TypeError):
                    pass
            # Keep a torn record visible to the exporter as an invalid line;
            # never truncate historical bytes or merge a new event into it.
            if not tail.endswith(b"\n"):
                _write(fd, b"\n")
        else:
            _write(fd, _line({"record_type": "archive_start", "schema": "mathlottery.telemetry.v1",
                              "recorded_at": now(), "earlier_history": "unavailable" if earlier_history else "none_observed"}))
        _write(fd, encoded)
        os.fsync(fd)
    finally:
        os.close(fd)


def _sanitize(raw, scope):
    from mathlottery.activity import KINDS, STATUSES, _controller_event, _timestamp
    from mathlottery.resources import _attempt, _projection

    if not isinstance(raw, dict):
        return None
    if raw.get("record_type") == "archive_start":
        stamp = _timestamp(raw.get("recorded_at"))
        history = raw.get("earlier_history")
        if stamp and history in {"unavailable", "none_observed"}:
            return {"record_type": "archive_start", "schema": "mathlottery.telemetry.v1",
                    "recorded_at": stamp, "earlier_history": history}
        return None
    if scope == "controller":
        event = _controller_event(raw)
        return {"record_type": "activity", **event} if event else None
    if scope == "agent":
        kind, status = raw.get("kind"), raw.get("status")
        if isinstance(kind, str) and kind in KINDS and isinstance(status, str) and status in STATUSES \
                and _timestamp(raw.get("time")):
            return {"record_type": "activity", "kind": kind, "status": status, "time": raw["time"]}
    if scope in {"run_resources", "formal_resources"} and raw.get("record_type") == "resource_attempt":
        attempt = _attempt(raw.get("attempt"))
        if attempt and attempt["number"] > 0:
            value = _projection({"cumulative": raw.get("cumulative", {})})
            return {"record_type": "resource_attempt", "attempt": attempt, "cumulative": value["cumulative"]}
    return None


def export_activity_archive(directory, attempt_directories=(), *, max_bytes=16 * 1024 * 1024):
    """Return sanitized JSONL, or fail explicitly if input/output exceeds the cap.

    Pass every authoritative attempt directory, not just those in the polling
    window. Records are grouped by stream; timestamps retain their original order
    within each append-only stream. Old raw provider logs are never reconstructed.
    No path, provider identifier, command, URL or exception text is exported.
    """
    if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or not 1 <= max_bytes <= MAX_EXPORT_BYTES:
        raise ValueError("Telemetry export limit must be between 1 byte and 64 MiB")
    directory = Path(directory).resolve()
    sources = [(directory / "controller-activity-events.jsonl", "controller"),
               (directory / "resource-attempts.jsonl", "run_resources"),
               (directory / "formal-resource-attempts.jsonl", "formal_resources")]
    seen = set()
    for attempt in attempt_directories:
        path = Path(attempt).resolve()
        if not path.is_relative_to(directory):
            raise ValueError("Telemetry attempt must belong to this run")
        if path not in seen:
            seen.add(path)
            sources.append((path / "activity-events.jsonl", "agent"))
    parts, streams = [], []
    read_bytes = 0
    output_bytes = 0
    invalid = 0
    for index, (path, scope) in enumerate(sources):
        if not path.is_file():
            streams.append({"stream": index, "scope": scope, "available": False})
            continue
        if path.is_symlink() or not path.resolve().is_relative_to(directory):
            raise ValueError("Unsafe telemetry archive")
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        count = 0
        earlier_history = "unknown"
        with os.fdopen(fd, "rb") as source:
            fcntl.flock(source, fcntl.LOCK_SH)
            info = os.fstat(source.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise ValueError("Unsafe telemetry archive")
            if read_bytes + info.st_size > max_bytes:
                raise ValueError("Telemetry archive exceeds the download size limit")
            while line := source.readline(MAX_RECORD_BYTES + 1):
                read_bytes += len(line)
                if len(line) > MAX_RECORD_BYTES or read_bytes > max_bytes:
                    raise ValueError("Telemetry archive exceeds the download size limit")
                try:
                    event = _sanitize(json.loads(line), scope)
                except (ValueError, TypeError, OverflowError):
                    event = None
                if event is None:
                    invalid += 1
                    continue
                if event["record_type"] == "archive_start":
                    earlier_history = event["earlier_history"]
                else:
                    count += 1
                encoded = _line({"stream": index, "scope": scope, **event})
                output_bytes += len(encoded)
                if output_bytes > max_bytes:
                    raise ValueError("Telemetry archive exceeds the download size limit")
                parts.append(encoded)
        streams.append({"stream": index, "scope": scope, "available": True, "records": count,
                        "earlier_history": earlier_history})
    metadata = _line({"record_type": "export_metadata", "schema": "mathlottery.telemetry.v1",
                      "coverage": "recorded_valid_events_only", "legacy_history_reconstructed": False,
                      "heartbeats_archived": False, "invalid_records_omitted": invalid, "streams": streams})
    if output_bytes + len(metadata) > max_bytes:
        raise ValueError("Telemetry archive exceeds the download size limit")
    return metadata + b"".join(parts)
