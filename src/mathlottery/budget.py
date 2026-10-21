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


def remaining(run: Run, config: Config) -> float:
    return max(0.0, config.budget.max_wall_time_minutes * 60 - elapsed(run))


def exhausted(run: Run, config: Config) -> str | None:
    if remaining(run, config) <= 0:
        return "Active wall-time budget reached"
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
