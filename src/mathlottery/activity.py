"""Bounded public projections of real transport events, without tool payloads."""

from __future__ import annotations

import json
from collections import deque

from mathlottery.models import now
from mathlottery.storage import atomic_write, json_text

KINDS = {"session", "model", "reasoning", "message", "search", "command", "file", "tool", "computation"}
STATUSES = {"running", "completed", "failed", "queued", "cancelled", "incomplete"}


class ActivityReporter:
    def __init__(self, directory):
        self.path = directory / "activity.json"
        self.events = deque(maxlen=30)
        self.seen = deque(maxlen=512)

    def record(self, kind, status, identifier=""):
        if not isinstance(kind, str) or not isinstance(status, str) or kind not in KINDS or status not in STATUSES:
            return
        key = (kind, status, str(identifier)[:256])
        if key in self.seen:
            return
        self.seen.append(key)
        event = {"kind": kind, "status": status, "time": now()}
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
                  and item.get("status") in STATUSES and isinstance(item.get("time"), str)
                  and len(item["time"]) < 40]
        return {"available": bool(recent), "last_active_at": recent[-1]["time"] if recent else None,
                "current": recent[-1] if recent else None, "recent": recent}
    except (OSError, ValueError, TypeError, AttributeError):
        return empty
