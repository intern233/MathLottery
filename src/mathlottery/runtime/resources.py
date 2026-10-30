"""Workspace-wide FIFO admission with crash-safe leases and sampled memory guardrails.

Locks, not PID files, own capacity. Queue records survive server restarts; a dead
owner is removed on the next inspection. Memory limits are cooperative and only
request cancellation of the owning run; they are not hard kernel quotas.
"""

from __future__ import annotations

import fcntl
import json
import math
import os
import threading
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from mathlottery.models import now
from mathlottery.storage.core import atomic_write, json_text, safe_path
from mathlottery.telemetry.archive import append_public_record


def available_memory_mb():
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemAvailable:"):
                return round(int(line.split()[1]) / 1024, 1)
    except (OSError, ValueError):
        pass
    return None


def process_tree_memory(pid):
    """Sum RSS of a process and current descendants (shared pages may be counted twice)."""
    processes = {}
    try:
        for entry in Path("/proc").iterdir():
            if not entry.name.isdigit():
                continue
            try:
                fields = (entry / "stat").read_text().rsplit(") ", 1)[1].split()
                if fields[0] != "Z":
                    processes[int(entry.name)] = (int(fields[1]), int(fields[21]))
            except (OSError, ValueError, IndexError):
                continue
        if pid not in processes:
            return None
        descendants = {pid}
        while True:
            children = {child for child, (parent, _) in processes.items() if parent in descendants}
            expanded = descendants | children
            if expanded == descendants:
                break
            descendants = expanded
        pages = sum(processes[child][1] for child in descendants)
        return round(pages * os.sysconf("SC_PAGE_SIZE") / 1024**2, 1)
    except (OSError, ValueError):
        return None


def _read(path, default):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return default


STATES = {"queued", "running", "released", "cancelled", "interrupted"}
REASONS = {"capacity", "low_available_memory",
           "Worker exited; resume the preserved checkpoint",
           "Sampled local process-tree RSS exceeded the configured soft limit",
           "Queue wait cancelled; no model call was started"}


def _number(value, default=None):
    return round(float(value), 3) if isinstance(value, (int, float)) and not isinstance(value, bool) \
        and math.isfinite(value) and value >= 0 else default


def _date(value):
    if not isinstance(value, str) or len(value) > 40:
        return None
    try:
        return value if datetime.fromisoformat(value).tzinfo is not None else None
    except ValueError:
        return None


def _elapsed(start, end):
    if not _date(start) or not _date(end):
        return 0.0
    return round(max(0, (datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds()), 3)


def _memory(value):
    if not isinstance(value, dict):
        return None
    return {"available": value.get("available") is True,
            **{key: _number(value.get(key)) for key in ("rss_mb", "peak_rss_mb", "available_mb")},
            "sampled_at": _date(value.get("sampled_at")), "scope": "local_process_tree"}


def _attempt(value):
    if not isinstance(value, dict):
        return None
    state = value.get("state")
    return {"number": int(_number(value.get("number"), 0)),
            "queue_seconds": _number(value.get("queue_seconds"), 0.0),
            "active_seconds": _number(value.get("active_seconds"), 0.0),
            "peak_rss_mb": _number(value.get("peak_rss_mb")),
            "state": state if isinstance(state, str) and state in STATES else "interrupted",
            **{key: _date(value.get(key)) for key in ("queued_at", "started_at", "updated_at")}}


def _projection(value):
    """Sanitize both legacy and current snapshots; never expose arbitrary persisted fields."""
    if not isinstance(value, dict):
        return None
    state = value.get("state")
    state = state if isinstance(state, str) and state in STATES else "interrupted"
    result = {"state": state, **{key: _date(value.get(key)) for key in ("queued_at", "started_at", "updated_at")},
              "queue_position": _number(value.get("queue_position")),
              "reason": value.get("reason") if isinstance(value.get("reason"), str) and value["reason"] in REASONS else None,
              "memory": _memory(value.get("memory"))}
    cumulative = value.get("cumulative")
    if not isinstance(cumulative, dict):
        # Old versions kept only the latest execution. Recover its observed time
        # and peak, but explicitly mark older resume history as unknown.
        started, updated, queued = result["started_at"], result["updated_at"], result["queued_at"]
        peak = (result["memory"] or {}).get("peak_rss_mb")
        attempt = {"number": 1, "state": state, "queued_at": queued, "started_at": started, "updated_at": updated,
                   "queue_seconds": _elapsed(queued, started or updated),
                   "active_seconds": _elapsed(started, updated), "peak_rss_mb": peak}
        result.update(attempt=attempt, recent_attempts=[attempt] if state not in {"queued", "running"} else [],
                      cumulative={"attempts": 1, "queue_seconds": attempt["queue_seconds"],
                                  "active_seconds": attempt["active_seconds"], "peak_rss_mb": peak,
                                  "history_complete": False, "timing_basis": "legacy_snapshot"})
        return result
    basis = cumulative.get("timing_basis")
    result["cumulative"] = {
        "attempts": int(_number(cumulative.get("attempts"), 0)),
        "queue_seconds": _number(cumulative.get("queue_seconds"), 0.0),
        "active_seconds": _number(cumulative.get("active_seconds"), 0.0),
        "peak_rss_mb": _number(cumulative.get("peak_rss_mb")),
        "history_complete": cumulative.get("history_complete") is True,
        "timing_basis": basis if isinstance(basis, str) and basis in {
            "monotonic", "legacy_snapshot", "legacy_snapshot_and_monotonic"} else "legacy_snapshot",
    }
    result["attempt"] = _attempt(value.get("attempt"))
    history = value.get("recent_attempts", [])
    result["recent_attempts"] = [item for raw in history[-20:] if (item := _attempt(raw))] if isinstance(history, list) else []
    return result


def _interrupt_snapshot(value):
    value = _projection(value)
    if value is None:
        return None
    # Do not advance elapsed time to discovery time: the worker may have died
    # hours ago. Last completed sample is the only observed lower bound.
    value.update(state="interrupted", queue_position=None,
                 reason="Worker exited; resume the preserved checkpoint")
    if value["attempt"]:
        value["attempt"]["state"] = "interrupted"
        history = [item for item in value["recent_attempts"] if item["number"] != value["attempt"]["number"]]
        value["recent_attempts"] = (history + [value["attempt"]])[-20:]
    return value


def _stop_requested(store, run_id):
    directory = store.run_dir(run_id)
    if (directory / "stop.requested").exists():
        return True
    # A resume clears the core marker. The browser worker's separate marker must
    # still cancel admission during that narrow window, without blocking later CLI resumes.
    if (directory / "web/stop.requested").exists() and (directory / "web/worker.lock").exists():
        with (directory / "web/worker.lock").open("a") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return True
    return False


class Coordinator:
    def __init__(self, store):
        self.store = store
        self.folder = store.internal / "resources"
        self.folder.mkdir(parents=True, exist_ok=True)

    def snapshot_path(self, run_id, kind="run"):
        return self.store.run_dir(run_id) / ("resources.json" if kind == "run" else "formal-resources.json")

    def archive_attempt(self, run_id, kind, value):
        if not value.get("attempt"):
            return
        name = "resource-attempts.jsonl" if kind == "run" else "formal-resource-attempts.jsonl"
        append_public_record(self.store.run_dir(run_id) / name,
                             {"record_type": "resource_attempt", "attempt": value["attempt"],
                              "cumulative": value["cumulative"]},
                             earlier_history=value["attempt"]["number"] > 1 or not value["cumulative"]["history_complete"],
                             attempt_number=value["attempt"]["number"])

    def stop_identified_orphan(self, entry):
        if entry["kind"] != "run":
            return
        try:
            run = self.store.load(entry["run_id"])
        except ValueError:
            return
        if run.mode in {"codex", "work"} and run.native.active_attempt:
            from mathlottery.providers.codex import NativeWorkBackend

            # PID start time, command output path and private process-group checks
            # must all succeed; never signal a process based only on its PID.
            NativeWorkBackend.stop_orphan(safe_path(self.store.run_dir(run.id), run.native.active_attempt))

    @contextmanager
    def transaction(self):
        with (self.folder / "queue.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            entries = _read(self.folder / "queue.json", [])
            live = []
            for entry in entries:
                with (self.folder / f"{entry['ticket']}.lease").open("a") as handle:
                    try:
                        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    except BlockingIOError:
                        live.append(entry)
                        continue
                snapshot = self.snapshot_path(entry["run_id"], entry["kind"])
                self.stop_identified_orphan(entry)
                value = _interrupt_snapshot(_read(snapshot, {}))
                if value:
                    self.archive_attempt(entry["run_id"], entry["kind"], value)
                    atomic_write(snapshot, json_text(value))
                if entry["kind"] == "run":
                    from mathlottery.telemetry.activity import interrupt_controller_activity

                    interrupt_controller_activity(self.store.run_dir(entry["run_id"]))
                (self.folder / f"{entry['ticket']}.lease").unlink(missing_ok=True)
            try:
                yield live
            finally:
                atomic_write(self.folder / "queue.json", json_text(live))
                fcntl.flock(lock, fcntl.LOCK_UN)

    def snapshot(self, run_id, kind="run"):
        # Reconcile crashed owners before exposing status. No model call is restarted.
        with self.transaction():
            pass
        return _projection(_read(self.snapshot_path(run_id, kind), None))

    @contextmanager
    def admission(self, run, config, kind="run", cancelled=None):
        settings = config.resources
        limit = settings.max_concurrent_runs if kind == "run" else settings.max_concurrent_formal
        cancelled = cancelled or (lambda: _stop_requested(self.store, run.id))
        ticket = uuid4().hex
        lease_path = self.folder / f"{ticket}.lease"
        path = self.snapshot_path(run.id, kind)
        previous = _projection(_read(path, None))
        totals = previous["cumulative"] if previous else {
            "attempts": 0, "queue_seconds": 0.0, "active_seconds": 0.0, "peak_rss_mb": None,
            "history_complete": True, "timing_basis": "monotonic",
        }
        history = previous["recent_attempts"] if previous else []
        if previous and previous["state"] in {"queued", "running"}:
            # Admission is normally entered after stale leases are reconciled.
            # Preserve a surviving last sample even if the queue file was lost.
            prior_attempt = dict(previous["attempt"] or {})
            prior_attempt["state"] = "interrupted"
            history = (history + [prior_attempt])[-20:]
            self.archive_attempt(run.id, kind, {**previous, "attempt": prior_attempt})
        initial = now()
        value = {"state": "queued", "queued_at": initial, "started_at": None,
                 "updated_at": initial, "queue_position": None, "reason": "capacity", "memory": None,
                 "recent_attempts": history, "attempt": None, "cumulative": None}
        done = threading.Event()
        monitor = None
        acquired = False
        memory_reason = None
        value_lock = threading.RLock()
        queued_clock = time.monotonic()
        started_clock = None

        def write(*, terminal=False):
            with value_lock:
                value["updated_at"] = now()
                clock = time.monotonic()
                queue_seconds = max(0, (started_clock if started_clock is not None else clock) - queued_clock)
                active_seconds = max(0, clock - started_clock) if started_clock is not None else 0.0
                peak = (value["memory"] or {}).get("peak_rss_mb")
                value["attempt"] = {"number": totals["attempts"] + 1,
                                    "queue_seconds": round(queue_seconds, 3), "active_seconds": round(active_seconds, 3),
                                    "peak_rss_mb": peak, "state": value["state"],
                                    **{key: value[key] for key in ("queued_at", "started_at", "updated_at")}}
                peaks = [item for item in (peak, totals["peak_rss_mb"]) if item is not None]
                value["cumulative"] = {"attempts": totals["attempts"] + 1,
                                       "queue_seconds": round(totals["queue_seconds"] + queue_seconds, 3),
                                       "active_seconds": round(totals["active_seconds"] + active_seconds, 3),
                                       "peak_rss_mb": max(peaks) if peaks else None,
                                       "history_complete": totals["history_complete"],
                                       "timing_basis": "monotonic" if totals["timing_basis"] == "monotonic"
                                       else "legacy_snapshot_and_monotonic"}
                if terminal:
                    value["recent_attempts"] = (history + [value["attempt"]])[-20:]
                    self.archive_attempt(run.id, kind, value)
                atomic_write(path, json_text(value))

        def observe():
            nonlocal memory_reason
            peak = 0.0
            while not done.is_set():
                rss = process_tree_memory(os.getpid())
                if rss is not None:
                    peak = max(peak, rss)
                with value_lock:
                    if done.is_set():
                        break
                    value["memory"] = {"available": rss is not None, "rss_mb": rss,
                                       "peak_rss_mb": peak or None,
                                       "available_mb": available_memory_mb(), "sampled_at": now(),
                                       "scope": "local_process_tree"}
                    if settings.memory_soft_limit_mb is not None and rss is not None and rss > settings.memory_soft_limit_mb:
                        memory_reason = "Sampled local process-tree RSS exceeded the configured soft limit"
                        value["reason"] = memory_reason
                        atomic_write(self.store.run_dir(run.id) / "stop.requested", now())
                    write()
                done.wait(settings.sample_interval_seconds)

        with lease_path.open("a") as lease:
            fcntl.flock(lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
            try:
                with self.transaction() as entries:
                    entries.append({"ticket": ticket, "run_id": run.id, "kind": kind,
                                    "state": "queued", "limit": limit})
                    write()
                while not cancelled():
                    free_memory = available_memory_mb()
                    memory_ok = free_memory is None or free_memory >= settings.min_available_memory_mb
                    with self.transaction() as entries:
                        relevant = [item for item in entries if item["kind"] == kind]
                        effective_limit = min(item["limit"] for item in relevant)
                        active = sum(item["state"] == "running" for item in relevant)
                        waiting = [item for item in relevant if item["state"] == "queued"]
                        position = next(i for i, item in enumerate(waiting) if item["ticket"] == ticket)
                        value["queue_position"] = position + 1
                        value["reason"] = "capacity" if memory_ok else "low_available_memory"
                        if memory_ok and position == 0 and active < effective_limit:
                            next(item for item in entries if item["ticket"] == ticket)["state"] = "running"
                            acquired = True
                            started_clock = time.monotonic()
                            value.update(state="running", started_at=now(), queue_position=None, reason=None)
                        write()
                    if acquired:
                        if kind == "run":
                            monitor = threading.Thread(target=observe, daemon=True)
                            monitor.start()
                        break
                    done.wait(min(settings.sample_interval_seconds, 0.25))
                yield acquired
            finally:
                done.set()
                if monitor:
                    monitor.join(timeout=5)
                with self.transaction() as entries:
                    entries[:] = [item for item in entries if item["ticket"] != ticket]
                    value.update(state="released" if acquired else "cancelled", queue_position=None)
                    if memory_reason:
                        value["reason"] = memory_reason
                    elif not acquired:
                        value["reason"] = "Queue wait cancelled; no model call was started"
                    write(terminal=True)
                fcntl.flock(lease, fcntl.LOCK_UN)
                lease_path.unlink(missing_ok=True)


@contextmanager
def run_admission(store, run, config):
    with Coordinator(store).admission(run, config) as admitted:
        yield admitted


@contextmanager
def formal_admission(store, run, config, cancelled=None):
    with Coordinator(store).admission(run, config, "formal", cancelled) as admitted:
        yield admitted
