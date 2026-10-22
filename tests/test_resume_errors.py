"""A resumed run presents current execution state while preserving failure history."""

import json

import pytest

from mathlottery.backends import BackendResult, BackendStatus
from mathlottery.config import Config
from mathlottery.models import State, Workflow
from mathlottery.orchestrator import Orchestrator


def recorded_errors(store, run_id):
    with store.connect() as db:
        rows = db.execute("SELECT data FROM events WHERE run_id=? ORDER BY seq", (run_id,))
        return [event["error"] for row in rows if (event := json.loads(row[0])).get("error")]


@pytest.mark.parametrize("failure,state", [
    (BackendStatus.INTERRUPTED, State.PAUSED),
    (BackendStatus.RATE_LIMITED, State.RATE_LIMITED),
    (BackendStatus.FAILED, State.FAILED),
])
def test_resume_clears_stale_error_before_next_invocation_and_keeps_history(store, failure, state):
    observations = []

    class ScriptedBackend:
        def invoke_native(self, *args, **kwargs):
            observations.append(store.load(run.id))
            if len(observations) == 1:
                return BackendResult(failure, error="Previous invocation failed", invoked=True)
            return BackendResult(BackendStatus.FAILED, error="New provider failure", invoked=True)

    engine = Orchestrator(store, ScriptedBackend())
    run = engine.create(Config(), workflow=Workflow.FIND)
    paused = engine.drive(run.id)
    assert paused.state == state
    assert paused.last_error == "Previous invocation failed"
    resumed = engine.resume(run.id)
    assert len(observations) == 2
    assert observations[1].state == State.DISCOVERING
    assert observations[1].stop_reason is None
    assert observations[1].last_error is None
    assert resumed.last_error == "New provider failure"
    assert recorded_errors(store, run.id) == ["Previous invocation failed", "New provider failure"]


def test_pending_chat_resume_retains_recovery_and_replaces_current_error(store):
    calls, recovered = [], []

    class PendingBackend:
        def invoke_native(self, *args, **kwargs):
            calls.append("create")
            kwargs["on_session"]("resp_pending_fixture")
            return BackendResult(
                BackendStatus.FAILED, error="Lost connection to pending response",
                invoked=True, pending=True, session_id="resp_pending_fixture",
            )

        def recover_native(self, *args, **kwargs):
            calls.append("recover")
            recovered.append(store.load(run.id))
            return BackendResult(
                BackendStatus.FAILED, error="Connection is still unavailable",
                invoked=True, pending=True, session_id="resp_pending_fixture",
            )

    config = Config()
    config.backend.mode = "chat"
    engine = Orchestrator(store, PendingBackend())
    run = engine.create(config, workflow=Workflow.FIND)
    paused = engine.drive(run.id)
    assert paused.native.active_attempt and paused.iteration == 0
    saved = paused.model_dump()
    with pytest.raises(ValueError, match="Recover the pending attempt"):
        engine.resume(run.id, mode="codex")
    assert store.load(run.id).model_dump() == saved
    resumed = engine.resume(run.id)
    assert calls == ["create", "recover"]
    assert recovered[0].last_error is None
    assert recovered[0].native.active_attempt == paused.native.active_attempt
    assert recovered[0].native.solver_response_id == "resp_pending_fixture"
    assert resumed.native.active_attempt == paused.native.active_attempt
    assert resumed.iteration == 0
    assert resumed.last_error == "Connection is still unavailable"
    assert recorded_errors(store, run.id) == [
        "Lost connection to pending response", "Connection is still unavailable",
    ]
