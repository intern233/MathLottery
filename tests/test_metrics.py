from mathlottery.config import Config
from mathlottery.metrics import run_metrics
from mathlottery.orchestrator import Orchestrator


def test_measurements_distinguish_missing_handoffs_and_unknown_history(store):
    run = Orchestrator(store).create(Config())
    run.native.history = [
        {"role": "research", "status": "COMPLETED", "mode": "codex"},
        {
            "role": "research",
            "phase": "FIND",
            "status": "COMPLETED",
            "mode": "codex",
            "milestone": {"kind": "selection"},
            "invocation_seconds": 12.25,
        },
        {"role": "research", "phase": "SOLVE", "status": "COMPLETED", "mode": "manual"},
        {"role": "review", "phase": "VERIFY", "status": "INTERRUPTED", "mode": "chat"},
        {
            "role": "review",
            "phase": "VERIFY",
            "status": "COMPLETED",
            "mode": "chat",
            "milestone": {"kind": "review"},
            "invocation_seconds": 5.0,
        },
    ]
    metrics = run_metrics(run)
    assert metrics["stages"]["UNKNOWN"]["handoff_errors"] == 1
    assert metrics["stages"]["UNKNOWN"]["invocation_seconds"] is None
    assert metrics["stages"]["SOLVE"]["handoff_errors"] == 0
    assert metrics["stages"]["FIND"]["milestones"] == {"selection": 1}
    assert metrics["stages"]["VERIFY"] == {
        "returns": 2,
        "completed": 1,
        "handoff_errors": 0,
        "timed_returns": 1,
        "invocation_seconds": 5.0,
        "milestones": {"review": 1},
    }
    assert run.id not in str(metrics)
