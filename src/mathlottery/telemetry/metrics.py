"""Observable workflow outcomes, not a score of mathematical ability or novelty."""

from collections import Counter

from mathlottery.models import Run


def run_metrics(run: Run) -> dict:
    stages = {}
    for entry in run.native.history:
        # Older checkpoints did not distinguish FIND from SOLVE in research history.
        phase = entry.get("phase") or ("VERIFY" if entry["role"] == "review" else "UNKNOWN")
        stage = stages.setdefault(
            phase,
            {
                "returns": 0,
                "completed": 0,
                "handoff_errors": 0,
                "timed_returns": 0,
                "invocation_seconds": None,
                "milestones": {},
            },
        )
        stage["returns"] += 1
        if entry["status"] == "COMPLETED":
            stage["completed"] += 1
            milestone = entry.get("milestone", {}).get("kind")
            if milestone:
                stage["milestones"][milestone] = stage["milestones"].get(milestone, 0) + 1
            elif entry.get("mode", run.mode) != "manual":
                stage["handoff_errors"] += 1
        seconds = entry.get("invocation_seconds")
        if seconds is not None:
            stage["timed_returns"] += 1
            stage["invocation_seconds"] = round((stage["invocation_seconds"] or 0) + seconds, 3)
    reviews = [c.reviews[-1] for c in run.candidates if c.reviews]
    legacy_usage = sum(
        entry.get("mode", run.mode) in {"codex", "work"}
        and bool(entry.get("usage"))
        and not entry.get("runtime", {}).get("usage_scope")
        for entry in run.native.history
    )
    return {
        "schema_version": 1,
        "workflow": run.workflow.value,
        "state": run.state.value,
        "stages": stages,
        "candidates": len(run.candidates),
        "reviewed_candidates": len(reviews),
        "latest_verdicts": dict(Counter(r.verdict for r in reviews)),
        "candidate_levels": dict(Counter(c.level.value for c in run.candidates)),
        "usage": run.usage.model_dump(mode="json"),
        "unreconciled_codex_returns": legacy_usage,
        "usage_warning": (
            "Historical Codex counters were not reconciled with session totals and may double-count "
            "resumed sessions. Stored totals are preserved, not retroactively corrected."
            if legacy_usage
            else None
        ),
        "scope": (
            "Recorded native returns and client invocation time only. Missing measurements are "
            "unknown; pending/recovered calls may have multiple returns. LLM reviews, workflow "
            "completion and these metrics do not establish correctness or novelty."
        ),
    }
