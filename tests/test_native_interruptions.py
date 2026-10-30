"""Expected task controls stay distinct from provider errors and raw diagnostics."""

import json
from datetime import datetime, timedelta

import pytest

from mathlottery.config import Config
from mathlottery.models import State, Workflow, now
from mathlottery.providers.base import BackendResult, BackendStatus
from mathlottery.runtime import budget
from mathlottery.runtime.native import NativeRunner
from mathlottery.runtime.orchestrator import Orchestrator

RAW_INTERRUPTION = "Stop requested or total wall-time budget reached"


@pytest.mark.parametrize("status,stopped,expired,expected_state,expected_reason,expected_error", [
    (BackendStatus.INTERRUPTED, False, True, State.PAUSED, "Active wall-time budget reached", None),
    (BackendStatus.INTERRUPTED, True, False, State.CANCELLED, "Stopped by user", None),
    (BackendStatus.INTERRUPTED, True, True, State.CANCELLED, "Stopped by user", None),
    (BackendStatus.INTERRUPTED, False, False, State.PAUSED, RAW_INTERRUPTION, RAW_INTERRUPTION),
    (BackendStatus.FAILED, False, True, State.FAILED, "Provider failure", "Provider failure"),
    (BackendStatus.RATE_LIMITED, False, True, State.RATE_LIMITED, "Provider failure", "Provider failure"),
    (BackendStatus.UNSUPPORTED, False, True, State.FAILED, "Provider failure", "Provider failure"),
    (BackendStatus.FAILED, True, True, State.FAILED, "Provider failure", "Provider failure"),
    (BackendStatus.RATE_LIMITED, True, True, State.RATE_LIMITED, "Provider failure", "Provider failure"),
])
def test_interrupt_reason_uses_task_state_without_masking_errors(
    store, monkeypatch, status, stopped, expired, expected_state, expected_reason, expected_error,
):
    raw = RAW_INTERRUPTION if status == BackendStatus.INTERRUPTED else "Provider failure"

    class ScriptedBackend:
        def invoke_native(self, *args, **kwargs):
            kwargs["on_session"]("fixture_session")
            if stopped:
                engine._stop_file(run).write_text("explicit test stop")
            if expired:
                later = (datetime.fromisoformat(now()) + timedelta(seconds=61)).isoformat()
                monkeypatch.setattr(budget, "now", lambda: later)
            return BackendResult(
                status, error=raw, text="Useful visible work", invoked=True,
                session_id="fixture_session", usage={"input_tokens": 12, "output_tokens": 3},
            )

    config = Config()
    config.budget.max_wall_time_minutes = 1
    engine = Orchestrator(store, ScriptedBackend())
    run = engine.create(config, workflow=Workflow.FIND)
    result = engine.drive(run.id)
    assert result.state == expected_state
    assert result.stop_reason == expected_reason
    assert result.last_error == expected_error
    assert result.native.solver_session_id == "fixture_session"
    assert result.native.pending_result is None
    assert result.iteration == 1
    assert result.usage.input_tokens == 12 and result.usage.output_tokens == 3
    assert len(result.native.history) == 1
    answer = store.run_dir(run.id) / result.native.history[-1]["answer"]
    assert answer.read_text() == "Useful visible work"
    receipt = json.loads(answer.with_name("receipt.json").read_text())
    assert receipt["result"]["error"] == raw
    assert receipt["result"]["status"] == status
    with store.connect() as db:
        events = [json.loads(row[0]) for row in db.execute("SELECT data FROM events WHERE run_id=?", (run.id,))]
    interruption = next(event for event in events if event["event"] == "native_attempt_interrupted")
    assert interruption["error"] == raw and interruption["reason"] == expected_reason


def test_exhausted_pending_chat_keeps_response_recovery_and_unsettled_usage(store, monkeypatch):
    class PendingBackend:
        def invoke_native(self, *args, **kwargs):
            kwargs["on_session"]("resp_pending_fixture")
            later = (datetime.fromisoformat(now()) + timedelta(seconds=61)).isoformat()
            monkeypatch.setattr(budget, "now", lambda: later)
            return BackendResult(
                BackendStatus.INTERRUPTED, error="Chat cancellation is pending; resume will retrieve this response",
                invoked=True, pending=True, session_id="resp_pending_fixture",
            )

    config = Config()
    config.backend.mode = "chat"
    config.budget.max_wall_time_minutes = 1
    engine = Orchestrator(store, PendingBackend())
    run = engine.drive(engine.create(config, workflow=Workflow.FIND).id)
    assert run.state == State.PAUSED
    assert run.stop_reason == "Active wall-time budget reached"
    assert run.last_error is None
    assert run.native.active_attempt
    assert run.native.solver_response_id == "resp_pending_fixture"
    assert run.native.pending_result is None
    assert run.iteration == 0
    assert run.usage.measured_calls == run.usage.unknown_calls == 0
    receipt = json.loads((store.run_dir(run.id) / run.native.active_attempt / "receipt.json").read_text())
    assert receipt["result"]["pending"] is True
    assert receipt["result"]["error"].startswith("Chat cancellation is pending")


def test_recovered_interruption_is_consumed_once_and_continues_same_session(store, monkeypatch):
    calls = []

    class NextBackend:
        def invoke_native(self, *args, **kwargs):
            calls.append(kwargs["session_id"])
            return BackendResult(BackendStatus.RATE_LIMITED, error="Next invocation quota", invoked=True)

    engine = Orchestrator(store, NextBackend())
    run = engine.create(Config(), workflow=Workflow.FIND)
    runner = NativeRunner(engine)
    runner.prepare(run, Config())
    run.native.solver_session_id = "fixture_preserved_session"
    run.native.active_attempt = f"tasks/{run.task_id}/attempt-recovered"
    (store.run_dir(run.id) / run.native.active_attempt).mkdir(parents=True)
    store.save(run, "fixture_interrupted_without_receipt")
    monkeypatch.setattr("mathlottery.runtime.attempts.NativeWorkBackend.stop_orphan", lambda directory: None)
    resumed = engine.drive(run.id)
    assert calls == ["fixture_preserved_session"]
    assert resumed.state == State.RATE_LIMITED
    assert resumed.last_error == "Next invocation quota"
    assert resumed.native.pending_result is None and resumed.native.active_attempt is None
    assert resumed.iteration == 2
    assert resumed.usage.unknown_calls == 2
    assert len(resumed.native.history) == 2
    assert resumed.native.history[0]["status"] == BackendStatus.INTERRUPTED
    assert resumed.native.history[1]["status"] == BackendStatus.RATE_LIMITED
    with store.connect() as db:
        events = [json.loads(row[0]) for row in db.execute("SELECT data FROM events WHERE run_id=?", (run.id,))]
    recovered = [event for event in events if (event.get("error") or "").startswith("Recovered an interrupted")]
    assert len(recovered) == 1
