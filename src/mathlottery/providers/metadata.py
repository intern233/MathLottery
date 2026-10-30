"""Whitelisted metadata and token counters from one explicitly identified Codex session."""

import json
import os
from pathlib import Path
from uuid import UUID

from mathlottery.providers.identity import CodexIdentity


def session_path(session_id: str, home: Path) -> Path | None:
    """Find one session strictly inside the selected account's storage."""
    UUID(session_id)
    if home.is_symlink() or home.parent.is_symlink():
        return None
    home = home.resolve()
    sessions = home / "sessions"
    if not sessions.resolve().is_relative_to(home):
        return None
    try:
        return next(
            (path for path in sessions.rglob(f"*{session_id}*.jsonl")
             if path.is_file() and path.resolve().is_relative_to(home)),
            None,
        )
    except OSError:
        return None


def session_runtime(session_id: str, home: Path | None = None) -> dict:
    """Read only this session's whitelisted runtime metadata, never credentials/history."""
    home = home if home is not None else CodexIdentity(Path.cwd()).home
    runtime = {}
    try:
        path = session_path(session_id, home)
        if path is None:
            return runtime
        with path.open("rb") as stream:
            size = stream.seek(0, os.SEEK_END)
            offset = max(0, size - 4_000_000)
            stream.seek(offset)
            if offset:
                stream.readline()
            for line in stream:
                if b'"turn_context"' not in line and b'"token_count"' not in line:
                    continue
                try:
                    event = json.loads(line)
                except (ValueError, UnicodeError):
                    continue
                if not isinstance(event, dict):
                    continue
                payload = event.get("payload") or {}
                if not isinstance(payload, dict):
                    continue
                if event.get("type") == "event_msg" and payload.get("type") == "token_count":
                    info = payload.get("info") or {}
                    counts = info.get("total_token_usage") if isinstance(info, dict) else None
                    if isinstance(counts, dict):
                        runtime["token_usage"] = clean_usage(counts)
                    continue
                if event.get("type") != "turn_context":
                    continue
                if isinstance(payload.get("model"), str):
                    runtime["model"] = payload["model"]
                    runtime["model_source"] = "Codex session turn_context"
                effort = payload.get("effort") or payload.get("reasoning_effort")
                if isinstance(effort, str):
                    runtime["reasoning_effort"] = effort
                policy = payload.get("sandbox_policy") or {}
                if isinstance(policy, dict) and isinstance(policy.get("type"), str):
                    runtime["sandbox"] = policy["type"]
    except OSError:
        pass  # Session formats/storage can change; unknown is not a guessed model name.
    return runtime


def clean_usage(value: dict) -> dict:
    return {
        key: count
        for key, count in value.items()
        if key
        in {
            "input_tokens",
            "output_tokens",
            "cached_input_tokens",
            "reasoning_output_tokens",
            "cache_write_input_tokens",
            "total_tokens",
        }
        and type(count) is int
        and count >= 0
    }


def turn_usage(reported: dict, before: dict | None, after: dict | None, resumed: bool):
    """Match CLI counters to session snapshots; never charge cumulative usage twice."""
    required = {"input_tokens", "output_tokens"}
    reported = clean_usage(reported)
    if not required <= reported.keys():
        return {}, "unreported"
    if not resumed:
        return reported, "first_session_turn"
    if before is None or after is None:
        return {}, "unknown: resumed session counters unavailable"
    before, after = clean_usage(before), clean_usage(after)
    keys = reported.keys() & before.keys() & after.keys()
    if not required <= keys or any(after[k] < before[k] for k in keys):
        return {}, "unknown: missing or reset session counters"
    delta = {key: after[key] - before[key] for key in keys}
    if all(reported[key] == after[key] for key in keys):
        return delta, "session_cumulative_delta"
    if all(reported[key] == delta[key] for key in keys):
        return delta, "per_turn_confirmed"
    return {}, "unknown: CLI usage disagrees with session counters"
