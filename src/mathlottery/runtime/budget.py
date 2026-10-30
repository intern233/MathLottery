from datetime import datetime

from mathlottery.config import Config
from mathlottery.models import Run, now


def elapsed(run: Run) -> float:
    active = 0.0
    if run.active_since:
        active = max(
            0.0,
            (
                datetime.fromisoformat(now()) - datetime.fromisoformat(run.active_since)
            ).total_seconds(),
        )
    return run.elapsed_seconds + active


def settle(run: Run) -> None:
    run.elapsed_seconds = elapsed(run)
    run.active_since = None


def interrupted_elapsed(run: Run, resources: dict | None) -> float | None:
    """Bound a dead local Codex worker's time by its last durable resource sample.

    Callers must establish that the owning worker is gone. A sampled lower bound
    is preferable to charging hours of downtime. Remote Chat responses may keep
    running after their worker exits, so this correction does not apply to them.
    """
    if (not run.active_since or run.execution != "native" or run.mode not in {"codex", "work"}
            or not resources or resources.get("state") != "interrupted"):
        return None
    # A Codex primary may have hosted Responses peers still running after this
    # local worker died. Do not erase their elapsed time using a local sample.
    if any(
        attempt.get("mode") == "chat"
        for attempt in run.native.solve_team.active_attempts
    ):
        return None
    try:
        start = datetime.fromisoformat(run.active_since)
        admitted = datetime.fromisoformat(resources["started_at"])
        sampled = datetime.fromisoformat(resources["updated_at"])
        current = datetime.fromisoformat(now())
        if not admitted <= start <= sampled <= current:
            return None  # A different execution, an invalid clock, or no usable sample.
        return run.elapsed_seconds + (sampled - start).total_seconds()
    except (KeyError, TypeError, ValueError):
        return None


def remaining(run: Run, config: Config) -> float:
    limit = (run.native.finalization.deadline_elapsed_seconds
             if run.native.finalization.status == "running"
             else config.budget.max_wall_time_minutes * 60)
    return max(0.0, limit - elapsed(run))


def exhausted(run: Run, config: Config) -> str | None:
    if remaining(run, config) <= 0:
        if run.native.finalization.status == "running":
            return "Finalization time budget reached"
        return "Active wall-time budget reached"
    return hard_limit_reason(run, config)


def hard_limit_reason(run: Run, config: Config) -> str | None:
    """Non-time limits remain binding during the extra closing turn."""
    if run.iteration >= config.budget.max_iterations:
        return "Iteration budget reached"
    for name in ("input_tokens", "output_tokens"):
        limit = getattr(config.budget, f"max_{name}")
        count = getattr(run.usage, name)
        if limit is not None:
            if run.mode == "manual" or run.usage.unknown_calls:
                return "Token usage is unknown; cannot enforce the configured token budget"
            if count is not None and count >= limit:
                return f"Measured {name} budget reached (checked between calls)"
    return None
