"""Bounded native Solve wrap-up; every provider is a local scripted fake."""

import json
from datetime import datetime, timedelta

import pytest

from mathlottery.config import Config
from mathlottery.models import Phase, Problem, State, Workflow, now
from mathlottery.providers.base import BackendResult, BackendStatus
from mathlottery.runtime import budget
from mathlottery.runtime.native import NativeRunner
from mathlottery.runtime.orchestrator import Orchestrator


def problem():
    return Problem(id="wrap-up-test", title="An addition identity", statement="For every natural n, n + 0 = n.")


def candidate(scope="PARTIAL"):
    return {
        "kind": "candidate", "conclude": True,
        "summary": "The boundary case is established; the general case remains open.",
        "candidate": {
            "claim": "For every natural n, n + 0 = n.",
            "proof": "A scripted derivation, preserved without any independent review.",
            "scope": scope,
            "remaining_obligations": ["General case not yet established."] if scope == "PARTIAL" else [],
        },
    }


class ScriptedBackend:
    def __init__(self, *results, on_call=None):
        self.results, self.on_call, self.calls = results, on_call, []

    def invoke_native(self, prompt, directory, workspace, timeout, **kwargs):
        identifiers = dict(line.split(": ", 1) for line in prompt.splitlines()
                           if line.startswith(("run_id: ", "task_id: ")))
        index = len(self.calls)
        self.calls.append({**identifiers, "prompt": prompt, "workspace": workspace,
                           "timeout": timeout, "session": kwargs["session_id"],
                           "reviewer": kwargs["reviewer"]})
        assert index < len(self.results), "Unexpected repeated model invocation"
        kwargs["on_session"]("test-persistent-solver")
        if self.on_call:
            self.on_call(index)
        value = self.results[index]
        if isinstance(value, BackendResult):
            return value
        return BackendResult(
            BackendStatus.COMPLETED,
            text=("A useful narrative without a machine-readable milestone." if value is None else
                  "```mathlottery\n" + json.dumps({**identifiers, **value}) + "\n```\n"),
            invoked=True, session_id="test-persistent-solver",
            usage={"input_tokens": 12, "output_tokens": 3},
        )


def clock(monkeypatch):
    instant = [datetime.fromisoformat(now())]

    def current():
        return instant[0].isoformat()

    monkeypatch.setattr(budget, "now", current)
    monkeypatch.setattr("mathlottery.runtime.native.now", current)

    def advance(seconds):
        instant[0] += timedelta(seconds=seconds)

    return advance


def config():
    value = Config()
    value.budget.max_wall_time_minutes = 1
    value.budget.finalize_minutes = 5
    return value


def interrupted():
    return BackendResult(
        BackendStatus.INTERRUPTED, invoked=True, session_id="test-persistent-solver",
        error="Stop requested or total wall-time budget reached",
        usage={"input_tokens": 12, "output_tokens": 3},
    )


def summary_path(store, run):
    path = store.run_dir(run.id) / run.native.finalization.summary_path
    assert path.is_file() and path.read_text().strip()
    return path


@pytest.mark.parametrize("full_budget", [False, True])
def test_expired_research_gets_one_bounded_same_session_wrap_up(store, monkeypatch, full_budget):
    advance = clock(monkeypatch)
    backend = ScriptedBackend(interrupted(), candidate(), on_call=lambda i: advance(61 if i == 0 else 2))
    settings = config()
    settings.budget.solve_until_budget_exhausted = full_budget
    engine = Orchestrator(store, backend)
    result = engine.drive(engine.create(settings, problem(), workflow=Workflow.SOLVE).id)

    assert result.state == State.COMPLETED and result.phase == Phase.REPORT
    assert result.native.finalization.status == "completed"
    assert result.elapsed_seconds == 63 and result.active_since is None
    assert len(backend.calls) == 2
    first, final = backend.calls
    assert [first["session"], final["session"]] == [None, "test-persistent-solver"]
    assert first["workspace"] == final["workspace"]
    assert first["task_id"] != final["task_id"]
    assert first["timeout"] == 60 and 0 < final["timeout"] <= 300
    assert all(not call["reviewer"] for call in backend.calls)
    assert len(result.candidates) == 1
    assert result.candidates[0].scope == "PARTIAL" and not result.candidates[0].reviews
    assert result.candidates[0].remaining_obligations == ["General case not yet established."]
    assert result.native.finalization.candidate_id == result.candidates[0].id
    assert result.native.finalization.task_id == final["task_id"]
    assert result.usage.measured_calls == result.iteration == 2
    assert result.last_error is None
    summary_path(store, result)


def test_pipeline_budget_wrap_up_does_not_launch_verify(store, monkeypatch):
    advance = clock(monkeypatch)
    backend = ScriptedBackend(interrupted(), candidate(), on_call=lambda i: advance(61 if i == 0 else 2))
    engine = Orchestrator(store, backend)
    result = engine.drive(engine.create(config(), problem(), workflow=Workflow.PIPELINE).id)
    assert result.state == State.COMPLETED and result.phase == Phase.REPORT
    assert len(backend.calls) == 2 and all(not call["reviewer"] for call in backend.calls)
    assert result.candidates[0].scope == "PARTIAL" and not result.candidates[0].reviews


@pytest.mark.parametrize("kind", ["stop", "progress"])
def test_explicit_unfinished_wrap_up_is_a_result_without_a_fabricated_candidate(store, monkeypatch, kind):
    advance = clock(monkeypatch)
    backend = ScriptedBackend(
        interrupted(), {"kind": kind, "summary": "No full proof; the induction step remains unresolved."},
        on_call=lambda i: advance(61 if i == 0 else 2),
    )
    engine = Orchestrator(store, backend)
    result = engine.drive(engine.create(config(), problem(), workflow=Workflow.SOLVE).id)
    assert result.state == State.COMPLETED and result.phase == Phase.REPORT
    assert result.native.finalization.status == "completed"
    assert not result.candidates and len(backend.calls) == 2
    assert "induction step remains unresolved" in summary_path(store, result).read_text()
    assert result.native.finalization.candidate_id is None


@pytest.mark.parametrize("kind", ["stop", "progress"])
def test_narrative_closing_does_not_reuse_a_previous_complete_claim(store, monkeypatch, kind):
    advance = clock(monkeypatch)
    backend = ScriptedBackend(
        candidate("COMPLETE"), {"kind": kind, "summary": "The claimed general argument has a gap."},
        on_call=lambda i: advance(61 if i == 0 else 2),
    )
    settings = config()
    settings.budget.solve_until_budget_exhausted = True
    engine = Orchestrator(store, backend)
    result = engine.drive(engine.create(settings, problem(), workflow=Workflow.SOLVE).id)
    assert result.state == State.COMPLETED and not result.native.candidate_conclude
    assert result.native.finalization.candidate_id is None
    assert len(result.candidates) == 1 and result.candidates[0].scope == "COMPLETE"
    summary = summary_path(store, result).read_text()
    assert "historical claim, not the final outcome" in summary
    assert "general argument has a gap" in summary


@pytest.mark.parametrize("field,limit", [("max_iterations", 1), ("max_input_tokens", 12), ("max_output_tokens", 3)])
def test_other_resource_limits_prevent_a_paid_wrap_up_even_at_time_expiry(store, monkeypatch, field, limit):
    advance = clock(monkeypatch)
    backend = ScriptedBackend(interrupted(), on_call=lambda _: advance(61))
    settings = config()
    setattr(settings.budget, field, limit)
    engine = Orchestrator(store, backend)
    result = engine.drive(engine.create(settings, problem(), workflow=Workflow.SOLVE).id)
    assert result.state == State.PAUSED and len(backend.calls) == 1
    assert result.native.finalization.status != "running"
    assert not result.candidates


def test_user_stop_takes_precedence_over_expired_research_budget(store, monkeypatch):
    advance = clock(monkeypatch)

    def stop(_):
        engine._stop_file(created).write_text("Explicit user stop")
        advance(61)

    backend = ScriptedBackend(interrupted(), on_call=stop)
    engine = Orchestrator(store, backend)
    created = engine.create(config(), problem(), workflow=Workflow.SOLVE)
    result = engine.drive(created.id)
    assert result.state == State.CANCELLED and result.stop_reason == "Stopped by user"
    assert len(backend.calls) == 1 and not result.candidates
    assert result.native.finalization.status != "running"


def test_user_stop_during_wrap_up_cancels_and_saves_a_local_summary(store, monkeypatch):
    advance = clock(monkeypatch)

    def stop(index):
        advance(61 if index == 0 else 2)
        if index == 1:
            engine._stop_file(created).write_text("Explicit user stop during wrap-up")

    backend = ScriptedBackend(interrupted(), interrupted(), on_call=stop)
    engine = Orchestrator(store, backend)
    created = engine.create(config(), problem(), workflow=Workflow.SOLVE)
    result = engine.drive(created.id)
    assert result.state == State.CANCELLED and result.stop_reason == "Stopped by user"
    assert result.native.finalization.status == "incomplete"
    assert len(backend.calls) == 2 and not result.candidates
    summary_path(store, result)


@pytest.mark.parametrize("workflow", [Workflow.FIND, Workflow.VERIFY])
def test_budget_wrap_up_is_not_implicitly_added_to_other_stages(store, monkeypatch, workflow):
    advance = clock(monkeypatch)
    backend = ScriptedBackend(interrupted(), on_call=lambda _: advance(61))
    engine = Orchestrator(store, backend)
    arguments = {"problem": problem(), "proof": "A proof submitted for review."} if workflow == Workflow.VERIFY else {}
    result = engine.drive(engine.create(config(), workflow=workflow, **arguments).id)
    assert result.state == State.PAUSED and result.native.finalization.status == "idle"
    assert len(backend.calls) == 1


@pytest.mark.parametrize("outcome,state", [
    (BackendStatus.INTERRUPTED, State.PAUSED),
    (BackendStatus.RATE_LIMITED, State.RATE_LIMITED),
    (BackendStatus.FAILED, State.FAILED),
])
def test_failed_wrap_up_is_bounded_has_local_summary_and_is_not_retried(store, monkeypatch, outcome, state):
    advance = clock(monkeypatch)
    failure = BackendResult(outcome, invoked=True, error="Scripted finalization interruption")
    backend = ScriptedBackend(interrupted(), failure, on_call=lambda i: advance(61 if i == 0 else 301))
    engine = Orchestrator(store, backend)
    result = engine.drive(engine.create(config(), problem(), workflow=Workflow.SOLVE).id)
    assert result.state == state and result.native.finalization.status == "incomplete"
    assert len(backend.calls) == 2 and not result.candidates
    saved = summary_path(store, result).read_bytes()

    resumed = engine.resume(result.id)
    assert len(backend.calls) == 2 and resumed.native.finalization.status == "incomplete"
    assert summary_path(store, resumed).read_bytes() == saved
    assert not resumed.candidates


def test_wrap_up_without_milestone_preserves_answer_without_inventing_success(store, monkeypatch):
    advance = clock(monkeypatch)
    backend = ScriptedBackend(interrupted(), None, on_call=lambda i: advance(61 if i == 0 else 2))
    engine = Orchestrator(store, backend)
    result = engine.drive(engine.create(config(), problem(), workflow=Workflow.SOLVE).id)
    assert result.state in {State.PAUSED, State.FAILED}
    assert result.native.finalization.status == "incomplete" and not result.candidates
    assert len(backend.calls) == 2
    summary_path(store, result)
    answer = store.run_dir(result.id) / result.native.history[-1]["answer"]
    assert "useful narrative" in answer.read_text()


@pytest.mark.parametrize("kind", ["progress", "stop"])
def test_empty_closing_milestone_does_not_count_as_a_delivered_result(store, monkeypatch, kind):
    advance = clock(monkeypatch)
    backend = ScriptedBackend(interrupted(), {"kind": kind, "summary": " \n "},
                              on_call=lambda i: advance(61 if i == 0 else 2))
    engine = Orchestrator(store, backend)
    result = engine.drive(engine.create(config(), problem(), workflow=Workflow.SOLVE).id)
    assert result.state == State.PAUSED
    assert result.native.finalization.status == "incomplete"
    assert len(backend.calls) == 2 and not result.candidates
    assert "Local fallback" in summary_path(store, result).read_text()


def test_disabled_wrap_up_retains_hard_pause_and_local_summary_without_model_call(store, monkeypatch):
    advance = clock(monkeypatch)
    backend = ScriptedBackend(interrupted(), on_call=lambda _: advance(61))
    settings = config()
    settings.budget.finalize_minutes = 0
    engine = Orchestrator(store, backend)
    result = engine.drive(engine.create(settings, problem(), workflow=Workflow.SOLVE).id)
    assert result.state == State.PAUSED and result.stop_reason == "Active wall-time budget reached"
    assert result.native.finalization.status == "incomplete" and len(backend.calls) == 1
    summary_path(store, result)


def test_old_already_paused_task_gets_wrap_up_when_resumed_with_new_default(store, monkeypatch):
    clock(monkeypatch)
    backend = ScriptedBackend(candidate())
    engine = Orchestrator(store, backend)
    run = engine.create(config(), problem(), workflow=Workflow.SOLVE)
    run.config["budget"].pop("finalize_minutes")  # Historical checkpoints predate this option.
    run.elapsed_seconds, run.state = 61, State.PAUSED
    run.stop_reason = "Active wall-time budget reached"
    run.native.solver_session_id = "test-persistent-solver"
    store.save(run, "historical_budget_pause")

    result = engine.resume(run.id)
    assert result.id == run.id and len(store.list_runs()) == 1
    assert result.state == State.COMPLETED and result.native.finalization.status == "completed"
    assert len(backend.calls) == 1 and backend.calls[0]["session"] == "test-persistent-solver"
    assert 0 < backend.calls[0]["timeout"] <= 300
    assert result.candidates[0].scope == "PARTIAL"


def test_queued_wrap_up_receipt_replays_once_after_interruption(store, monkeypatch):
    advance = clock(monkeypatch)
    backend = ScriptedBackend(interrupted(), candidate(), on_call=lambda i: advance(61 if i == 0 else 2))
    engine = Orchestrator(store, backend)
    original = NativeRunner.apply
    crashed = []

    def interrupt_before_apply(runner, run):
        if run.native.finalization.status == "running" and run.native.pending_result and not crashed:
            crashed.append(True)
            raise KeyboardInterrupt
        return original(runner, run)

    monkeypatch.setattr(NativeRunner, "apply", interrupt_before_apply)
    paused = engine.drive(engine.create(config(), problem(), workflow=Workflow.SOLVE).id)
    assert crashed and paused.native.pending_result and len(backend.calls) == 2
    result = engine.resume(paused.id)
    assert result.state == State.COMPLETED and result.native.finalization.status == "completed"
    assert len(backend.calls) == result.iteration == result.usage.measured_calls == 2
    assert len(result.candidates) == 1 and result.native.pending_result is None
    assert result.candidates[0].scope == "PARTIAL"


def test_missing_wrap_up_receipt_after_worker_loss_does_not_start_a_second_wrap_up(store, monkeypatch):
    advance = clock(monkeypatch)

    def crash(index):
        advance(61 if index == 0 else 2)
        if index == 1:
            raise KeyboardInterrupt

    backend = ScriptedBackend(interrupted(), candidate(), on_call=crash)
    engine = Orchestrator(store, backend)
    paused = engine.drive(engine.create(config(), problem(), workflow=Workflow.SOLVE).id)
    assert paused.state == State.PAUSED and len(backend.calls) == 2
    assert paused.native.active_attempt and paused.native.finalization.status == "running"

    result = engine.resume(paused.id)
    assert len(backend.calls) == 2 and not result.candidates
    assert result.native.finalization.status == "incomplete"
    summary_path(store, result)


def test_graceful_interrupt_before_closing_invocation_does_not_restart_research_on_steering(store, monkeypatch):
    advance = clock(monkeypatch)
    backend = ScriptedBackend(interrupted(), on_call=lambda _: advance(61))
    original = NativeRunner.prepare
    closing_task = []

    def interrupt_before_invoke(runner, run, settings):
        if run.native.finalization.status == "running":
            closing_task.append(run.native.finalization.task_id)
            raise KeyboardInterrupt
        return original(runner, run, settings)

    monkeypatch.setattr(NativeRunner, "prepare", interrupt_before_invoke)
    engine = Orchestrator(store, backend)
    paused = engine.drive(engine.create(config(), problem(), workflow=Workflow.SOLVE).id)
    assert closing_task and paused.state == State.PAUSED
    assert len(backend.calls) == 1 and paused.native.finalization.status == "incomplete"
    summary_path(store, paused)

    result = engine.resume(paused.id, message="Please collect the saved partial results.")
    assert len(backend.calls) == 1 and not result.candidates
    assert result.native.finalization.status == "incomplete"
    assert result.native.finalization.task_id == closing_task[0]


def test_worker_loss_after_begin_preserves_closing_task_id_when_resumed_with_steering(store, monkeypatch):
    advance = clock(monkeypatch)
    backend = ScriptedBackend(interrupted(), candidate(), on_call=lambda i: advance(61 if i == 0 else 2))
    original = NativeRunner.prepare
    closing_task = []

    def worker_exit_before_invoke(runner, run, settings):
        if run.native.finalization.status == "running" and not closing_task:
            closing_task.append(run.native.finalization.task_id)
            # Unlike a caught Ctrl-C, abrupt worker loss leaves the durable begin
            # checkpoint running, with no active attempt or queued receipt yet.
            raise SystemExit("Simulated worker exit before model invocation")
        return original(runner, run, settings)

    monkeypatch.setattr(NativeRunner, "prepare", worker_exit_before_invoke)
    engine = Orchestrator(store, backend)
    created = engine.create(config(), problem(), workflow=Workflow.SOLVE)
    with pytest.raises(SystemExit, match="Simulated worker exit"):
        engine.drive(created.id)
    saved = store.load(created.id)
    assert saved.native.finalization.status == "running"
    assert saved.task_id == saved.native.finalization.task_id == closing_task[0]
    assert not saved.native.active_attempt and not saved.native.pending_result
    assert len(backend.calls) == 1

    result = engine.resume(created.id, message="Please collect the existing partial results now.")
    assert result.state == State.COMPLETED and result.native.finalization.status == "completed"
    assert len(backend.calls) == 2
    assert backend.calls[-1]["task_id"] == closing_task[0]
    assert backend.calls[-1]["session"] == "test-persistent-solver"
    assert "Task: SOLVE finalization" in backend.calls[-1]["prompt"]
    assert result.candidates[0].scope == "PARTIAL" and not result.candidates[0].reviews
    summary_path(store, result)


def test_pending_chat_closing_receipt_survives_stop_and_recovers_as_finalization(store, monkeypatch):
    advance = clock(monkeypatch)
    recovery_calls = []

    def stop_while_pending(index):
        advance(61 if index == 0 else 2)
        if index == 1:
            engine._stop_file(created).write_text("User stopped while remote cancellation was pending")

    pending = BackendResult(
        BackendStatus.INTERRUPTED, invoked=True, pending=True,
        session_id="test-persistent-solver", error="Remote cancellation awaiting acknowledgement",
    )
    backend = ScriptedBackend(interrupted(), pending, on_call=stop_while_pending)

    def recover_native(directory, timeout, **kwargs):
        recovery_calls.append({"directory": directory, "timeout": timeout})
        assert len(recovery_calls) == 1, "The same remote receipt must not be recovered twice"
        current = store.load(created.id)
        kwargs["on_session"]("test-persistent-solver")
        return BackendResult(
            BackendStatus.COMPLETED, invoked=True, session_id="test-persistent-solver",
            text="```mathlottery\n" + json.dumps({
                "run_id": current.id, "task_id": current.task_id, **candidate(),
            }) + "\n```\n",
            usage={"input_tokens": 24, "output_tokens": 6},
        )

    monkeypatch.setattr(backend, "recover_native", recover_native, raising=False)
    settings = config()
    settings.backend.mode = "chat"
    engine = Orchestrator(store, backend)
    created = engine.create(settings, problem(), workflow=Workflow.SOLVE)
    paused = engine.drive(created.id)
    assert paused.state == State.CANCELLED and paused.stop_reason == "Stopped by user"
    assert paused.native.finalization.status == "incomplete"
    assert paused.native.active_attempt and not paused.native.pending_result
    assert paused.native.solver_response_id == "test-persistent-solver"
    assert len(backend.calls) == 2 and paused.iteration == 1
    closing_task = paused.native.finalization.task_id
    local_summary = summary_path(store, paused)
    assert "Local fallback" in local_summary.read_text()

    result = engine.resume(paused.id, message="Recover the existing closing result.")
    assert result.state == State.COMPLETED and result.phase == Phase.REPORT
    assert result.native.finalization.status == "completed"
    assert result.native.finalization.task_id == closing_task
    assert len(backend.calls) == 2 and len(recovery_calls) == 1
    assert result.iteration == result.usage.measured_calls == 2
    assert result.usage.input_tokens == 36 and result.usage.output_tokens == 9
    assert len(result.candidates) == 1 and not result.candidates[0].reviews
    assert result.candidates[0].scope == "PARTIAL"
    assert not result.native.active_attempt and not result.native.pending_result
    assert summary_path(store, result) == local_summary
    assert "boundary case is established" in local_summary.read_text()
    assert "Local fallback" not in local_summary.read_text()


def test_explicit_larger_research_budget_reopens_research_without_overwriting_old_summary(store, monkeypatch):
    advance = clock(monkeypatch)
    backend = ScriptedBackend(interrupted(), candidate(), candidate("COMPLETE"),
                              on_call=lambda i: advance(61 if i == 0 else 2))
    engine = Orchestrator(store, backend)
    settings = config()
    completed = engine.drive(engine.create(settings, problem(), workflow=Workflow.SOLVE).id)
    artifact = summary_path(store, completed)
    original = artifact.read_bytes()
    settings.budget.max_wall_time_minutes = 3

    result = engine.resume(completed.id, config=settings, message="Extend the original investigation.")
    assert result.state == State.COMPLETED and len(backend.calls) == 3
    assert result.elapsed_seconds == 65
    assert backend.calls[-1]["session"] == "test-persistent-solver"
    assert backend.calls[-1]["workspace"] == backend.calls[0]["workspace"]
    assert backend.calls[-1]["timeout"] == 117
    assert [value.scope for value in result.candidates] == ["PARTIAL", "COMPLETE"]
    assert all(not value.reviews for value in result.candidates)
    assert artifact.read_bytes() == original


def test_finalization_remaining_time_survives_pause_without_renewing_allowance(store, monkeypatch):
    advance = clock(monkeypatch)
    engine = Orchestrator(store, ScriptedBackend())
    settings = config()
    run = engine.create(settings, problem(), workflow=Workflow.SOLVE)
    run.elapsed_seconds = 61
    wrap_up = run.native.finalization
    wrap_up.status = "running"
    wrap_up.research_limit_seconds = 60
    wrap_up.started_elapsed_seconds = 61
    wrap_up.deadline_elapsed_seconds = 361
    run.active_since = budget.now()
    advance(45)
    assert budget.remaining(run, settings) == 255
    budget.settle(run)
    advance(3600)  # Human downtime does not either spend or replenish the allowance.
    assert budget.remaining(run, settings) == 255
    restored = type(run).model_validate_json(run.model_dump_json())
    assert budget.remaining(restored, settings) == 255
    restored.native.finalization.status = "completed"
    assert budget.remaining(restored, settings) == 0
