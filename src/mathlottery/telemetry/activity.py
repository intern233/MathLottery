"""Bounded public projections of real transport events, without tool payloads."""

from __future__ import annotations

import fcntl
import json
import math
import threading
import time
from collections import deque
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from mathlottery.models import now
from mathlottery.storage.core import atomic_write, json_text
from mathlottery.telemetry.archive import append_public_record
from mathlottery.telemetry.archive import export_activity_archive as export_activity_archive

KINDS = {"session", "model", "reasoning", "message", "search", "command", "file", "tool", "computation"}
STATUSES = {"running", "completed", "failed", "queued", "cancelled", "incomplete"}
CONTROLLER_STAGES = {
    "sources", "formal_compile", "formal_replay", "formal_inspect", "report_render",
    "report_bundle", "organize_materials", "checkpoint",
}


class ActivityReporter:
    def __init__(self, directory):
        self.path = directory / "activity.json"
        self.events = deque(read_activity(self.path)["recent"], maxlen=30)
        self.seen = deque(maxlen=512)

    def record(self, kind, status, identifier=""):
        if not isinstance(kind, str) or not isinstance(status, str) or kind not in KINDS or status not in STATUSES:
            return
        key = (kind, status, str(identifier)[:256])
        if key in self.seen:
            return
        self.seen.append(key)
        event = {"kind": kind, "status": status, "time": now()}
        append_public_record(self.path.parent / "activity-events.jsonl", {"record_type": "activity", **event},
                             earlier_history=self.path.exists())
        self.events.append(event)
        atomic_write(self.path, json_text({"available": True, "last_active_at": event["time"],
                                          "current": event, "recent": list(self.events)}))

    def codex(self, event):
        event_type = event.get("type")
        if not isinstance(event_type, str):
            return
        if event_type in {"thread.started", "turn.started", "turn.completed", "turn.failed", "error"}:
            status = "completed" if event_type == "turn.completed" else (
                "failed" if event_type in {"error", "turn.failed"} else "running")
            self.record("session" if event_type == "thread.started" else "model", status, event_type)
        item = event.get("item")
        if not isinstance(item, dict) or event_type not in {"item.started", "item.updated", "item.completed"}:
            return
        item_type = item.get("type")
        if not isinstance(item_type, str):
            return
        kind = {"agent_message": "message", "reasoning": "reasoning", "web_search": "search",
                "command_execution": "command", "file_change": "file", "mcp_tool_call": "tool",
                "collab_tool_call": "tool"}.get(item_type)
        if kind:
            status = "completed" if event_type == "item.completed" else "running"
            if item.get("status") in ("failed", "cancelled"):
                status = item["status"]
            self.record(kind, status, item.get("id", event_type))

    def response(self, response):
        status = response.get("status")
        status = "running" if status == "in_progress" else status
        self.record("model", status, response.get("id", ""))
        output = response.get("output")
        for item in output if isinstance(output, list) else []:
            if not isinstance(item, dict):
                continue
            item_type = item.get("type")
            if not isinstance(item_type, str):
                continue
            kind = {"web_search_call": "search", "code_interpreter_call": "computation",
                    "file_search_call": "search", "function_call": "tool", "mcp_call": "tool",
                    "reasoning": "reasoning", "message": "message"}.get(item_type)
            item_status = item.get("status") or response.get("status")
            if kind:
                self.record(kind, "running" if item_status == "in_progress" else item_status, item.get("id", ""))


def read_activity(path):
    """Read only the projection's public schema, including for old or malformed files."""
    empty = {"available": False, "last_active_at": None, "current": None, "recent": []}
    try:
        if path.stat().st_size > 32000:
            return empty
        data = json.loads(path.read_text())
        recent = [{"kind": item["kind"], "status": item["status"], "time": item["time"]}
                  for item in data.get("recent", [])[-30:]
                  if isinstance(item, dict) and item.get("kind") in KINDS
                  and item.get("status") in STATUSES and _timestamp(item.get("time"))]
        return {"available": bool(recent), "last_active_at": recent[-1]["time"] if recent else None,
                "current": recent[-1] if recent else None, "recent": recent}
    except (OSError, ValueError, TypeError, AttributeError):
        return empty


def _timestamp(value):
    if not isinstance(value, str) or len(value) > 40:
        return None
    try:
        parsed = datetime.fromisoformat(value)
        return value if parsed.tzinfo is not None else None
    except ValueError:
        return None


def _duration(value):
    return round(value, 3) if isinstance(value, (float, int)) and not isinstance(value, bool) \
        and math.isfinite(value) and value >= 0 else 0.0


def _controller_event(value):
    if not isinstance(value, dict) or value.get("stage") not in CONTROLLER_STAGES \
            or value.get("status") not in STATUSES or not _timestamp(value.get("time")):
        return None
    result = {"kind": "controller", "stage": value["stage"], "status": value["status"],
              "time": value["time"], "duration_seconds": _duration(value.get("duration_seconds"))}
    for key in ("started_at", "heartbeat_at"):
        if _timestamp(value.get(key)):
            result[key] = value[key]
    return result


def _controller_state(path):
    try:
        if path.stat().st_size > 64000:
            return {"recent": [], "active": {}}
        data = json.loads(path.read_text())
        recent = [event for item in data.get("recent", [])[-30:] if (event := _controller_event(item))]
        active = {key: event for key, item in list(data.get("active", {}).items())[-16:]
                  if isinstance(key, str) and len(key) == 32 and all(c in "0123456789abcdef" for c in key)
                  and (event := _controller_event(item)) and event["status"] == "running"}
        return {"recent": recent, "active": active}
    except (OSError, ValueError, TypeError, AttributeError):
        return {"recent": [], "active": {}}


class ControllerOperation:
    """An observed local operation; heartbeat means liveness, never model progress."""

    def __init__(self, directory, stage, heartbeat_seconds):
        if stage not in CONTROLLER_STAGES:
            raise ValueError("Unknown controller activity stage")
        self.path = Path(directory) / "controller-activity.json"
        self.lock_path = self.path.with_suffix(".lock")
        self.identifier = uuid4().hex
        self.stage = stage
        self.started_at = now()
        self.started = time.monotonic()
        self.status = "completed"
        self.done = threading.Event()
        self.interval = max(0.05, float(heartbeat_seconds))
        self.thread = None

    def set_status(self, status):
        if status not in {"completed", "failed", "cancelled", "incomplete"}:
            raise ValueError("Invalid terminal controller activity status")
        self.status = status

    def _write(self, status, *, heartbeat=False):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.lock_path.open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            if heartbeat and self.done.is_set():
                return
            data = _controller_state(self.path)
            event = {"kind": "controller", "stage": self.stage, "status": status,
                     "time": self.started_at if heartbeat else now(), "started_at": self.started_at,
                     "heartbeat_at": now(), "duration_seconds": round(max(0, time.monotonic() - self.started), 3)}
            if status == "running":
                data["active"][self.identifier] = event
                data["active"] = dict(list(data["active"].items())[-16:])
            else:
                data["active"].pop(self.identifier, None)
            if not heartbeat:
                append_public_record(self.path.parent / "controller-activity-events.jsonl",
                                     {"record_type": "activity", **event}, earlier_history=self.path.exists())
                data["recent"] = (data["recent"] + [event])[-30:]
            atomic_write(self.path, json_text(data))

    def _heartbeat(self):
        while not self.done.wait(self.interval):
            self._write("running", heartbeat=True)

    def start(self):
        self._write("running")
        self.thread = threading.Thread(target=self._heartbeat, daemon=True)
        self.thread.start()

    def finish(self):
        self.done.set()
        if self.thread:
            self.thread.join(timeout=5)
        self._write(self.status)


@contextmanager
def controller_activity(directory, stage, *, heartbeat_seconds=5.0):
    """Project one real controller operation, excluding arguments, errors and paths.

    Handled failures can call ``operation.set_status('failed')``. A completed
    operation is not a positive mathematical verdict. Exceptions propagate intact.
    """
    operation = ControllerOperation(directory, stage, heartbeat_seconds)
    operation.start()
    try:
        yield operation
    except BaseException:
        operation.set_status("failed")
        raise
    finally:
        operation.finish()


def read_run_activity(directory, attempt_directory=None, previous_attempt_directories=()):
    """Merge bounded public transport/controller events without reading raw logs.

    Previous attempt paths are optional and capped at 20. A stale controller
    heartbeat is marked as stale, not called a failure or used to restart work.
    """
    directory = Path(directory).resolve()
    recent = []
    seen_paths = set()
    for attempt in [*list(previous_attempt_directories)[-20:], attempt_directory]:
        if attempt is None:
            continue
        attempt = Path(attempt).resolve()
        if not attempt.is_relative_to(directory) or attempt in seen_paths:
            continue
        seen_paths.add(attempt)
        recent.extend(read_activity(attempt / "activity.json")["recent"])
    data = _controller_state(directory / "controller-activity.json")
    recent.extend(data["recent"])
    recent.sort(key=lambda event: event["time"])
    recent = recent[-30:]
    active = sorted(data["active"].values(), key=lambda event: event["time"])
    for event in active:
        heartbeat = event.get("heartbeat_at", event["time"])
        event["heartbeat_stale"] = (datetime.now(timezone.utc) - datetime.fromisoformat(heartbeat)).total_seconds() > 15
    fresh = [event for event in active if not event["heartbeat_stale"]]
    current = fresh[-1] if fresh else recent[-1] if recent else None
    return {"available": bool(recent or active), "last_active_at": recent[-1]["time"] if recent else None,
            "current": current, "recent": recent, "active_controllers": active,
            "last_heartbeat_at": max((item.get("heartbeat_at", item["time"]) for item in active), default=None)}


def interrupt_controller_activity(directory):
    """Close stages only after a resource lease proves its owning worker exited."""
    path = Path(directory) / "controller-activity.json"
    if not path.exists():
        return
    with path.with_suffix(".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        data = _controller_state(path)
        for event in data["active"].values():
            event["status"] = "incomplete"
            # Retain last measured duration and heartbeat; offline time is unknown.
            event["time"] = event.get("heartbeat_at", event["time"])
            append_public_record(path.parent / "controller-activity-events.jsonl",
                                 {"record_type": "activity", **event}, earlier_history=True)
            data["recent"].append(event)
        data["recent"] = data["recent"][-30:]
        data["active"] = {}
        atomic_write(path, json_text(data))
