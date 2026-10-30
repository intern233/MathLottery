"""Solve continuation controls with scripted backends; no model calls or credentials."""

import json
from datetime import datetime, timedelta

import pytest

from mathlottery.config import Config
from mathlottery.models import CandidateInput, Phase, Problem, State, Workflow, now
from mathlottery.providers.base import BackendResult, BackendStatus
from mathlottery.runtime import budget
from mathlottery.runtime.orchestrator import Orchestrator


def problem():
    return Problem(id="test-addition", title="Addition identity", statement="For every natural n, n + 0 = n.")


def candidate(scope="PARTIAL", *, conclude=True, obligations=()):
    return {
        "kind": "candidate", "conclude": conclude,
        "candidate": {
            "claim": "For every natural n, n + 0 = n.",
            "proof": f"Scripted {scope} derivation checkpoint.",
            "scope": scope, "remaining_obligations": list(obligations),
        },
    }


class ScriptedBackend:
    def __init__(self, *milestones, on_call=None):
        self.milestones = milestones
        self.on_call = on_call
        self.calls = []

    def invoke_native(self, prompt, directory, workspace, timeout, **kwargs):
        index = len(self.calls)
        self.calls.append({"session": kwargs["session_id"], "reviewer": kwargs["reviewer"],
                           "timeout": timeout, "workspace": workspace, "prompt": prompt})
        # Exhausting this script is a test failure, never permission to call a provider.
        assert index < len(self.milestones), "Unexpected extra model invocation"
        session = "test-review-session" if kwargs["reviewer"] else "test-solve-session"
        kwargs["on_session"](session)
        if self.on_call:
            self.on_call(index)
        identifiers = dict(line.split(": ", 1) for line in prompt.splitlines()
                           if line.startswith(("run_id: ", "task_id: ")))
        milestone = {**identifiers, **self.milestones[index]}
        return BackendResult(
            BackendStatus.COMPLETED,
            text="```mathlottery\n" + json.dumps(milestone) + "\n```\n",
            invoked=True, session_id=session, usage={"input_tokens": 12, "output_tokens": 3},
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


@pytest.mark.parametrize("scope", ["UNKNOWN", "PARTIAL", "COMPLETE", "COUNTEREXAMPLE"])
@pytest.mark.parametrize("obligations", [[], ["The unbounded case remains unproved."]])
@pytest.mark.parametrize("conclude", [False, True])
def test_only_an_explicit_complete_claim_without_gaps_can_finish_solve(
    store, scope, obligations, conclude,
):
    backend = ScriptedBackend(candidate(scope, conclude=conclude, obligations=obligations))
    config = Config()
    config.budget.max_iterations = 1
    engine = Orchestrator(store, backend)
    run = engine.drive(engine.create(config, problem(), workflow=Workflow.SOLVE).id)

    finishes = conclude and scope in {"COMPLETE", "COUNTEREXAMPLE"} and not obligations
    assert run.state == (State.COMPLETED if finishes else State.PAUSED)
    assert run.native.candidate_conclude == finishes
    if not finishes:
        assert run.stop_reason == "Iteration budget reached"
        assert run.phase == Phase.SOLVE
    assert run.last_error is None
    assert len(run.candidates) == 1 and not run.candidates[0].reviews
    assert run.candidates[0].scope == scope
    assert run.candidates[0].remaining_obligations == obligations
    assert run.native.history[0]["milestone"]["conclude"] == conclude
    assert len(backend.calls) == 1 and not backend.calls[0]["reviewer"]


def test_partial_then_complete_keeps_the_session_and_immutable_candidate(store):
    snapshots = []

    def inspect_first_candidate(index):
        if index == 1:
            current = store.load(created.id)
            path = engine.candidates.path(current, current.candidates[0])
            snapshots.append((path, path.read_bytes()))

    backend = ScriptedBackend(candidate(), candidate("COMPLETE"), on_call=inspect_first_candidate)
    engine = Orchestrator(store, backend)
    created = engine.create(Config(), problem(), workflow=Workflow.SOLVE)
    run = engine.drive(created.id)

    assert run.state == State.COMPLETED
    assert [call["session"] for call in backend.calls] == [None, "test-solve-session"]
    assert backend.calls[0]["workspace"] == backend.calls[1]["workspace"]
    assert all(not call["reviewer"] for call in backend.calls)
    assert [value.scope for value in run.candidates] == ["PARTIAL", "COMPLETE"]
    assert run.candidates[0].id != run.candidates[1].id
    assert all(not value.reviews for value in run.candidates)
    assert snapshots[0][0].read_bytes() == snapshots[0][1]
    assert run.iteration == run.usage.measured_calls == 2
    assert run.usage.input_tokens == 24 and run.usage.output_tokens == 6
    assert run.native.history[0]["milestone"]["conclude"] is True


def test_budget_expiry_preserves_partial_without_an_extra_invocation(store, monkeypatch):
    advance = clock(monkeypatch)
    backend = ScriptedBackend(candidate(), on_call=lambda _: advance(61))
    config = Config()
    config.budget.finalize_minutes = 0  # Closing turns are covered separately in test_finalization.
    config.budget.max_wall_time_minutes = 1
    engine = Orchestrator(store, backend)
    run = engine.drive(engine.create(config, problem(), workflow=Workflow.SOLVE).id)

    assert run.state == State.PAUSED and run.phase == Phase.SOLVE
    assert run.stop_reason == "Active wall-time budget reached"
    assert run.elapsed_seconds == 61 and run.active_since is None
    assert len(run.candidates) == len(backend.calls) == 1
    assert run.candidates[0].scope == "PARTIAL" and not run.candidates[0].reviews
    assert run.native.pending_result is None and run.last_error is None


def test_resume_uses_remaining_cumulative_time_and_same_session(store, monkeypatch):
    advance = clock(monkeypatch)
    backend = ScriptedBackend(candidate(), candidate(), on_call=lambda index: advance(20 if index == 0 else 45))
    config = Config()
    config.budget.finalize_minutes = 0  # Closing turns are covered separately in test_finalization.
    config.budget.max_wall_time_minutes = 1
    config.budget.max_iterations = 1
    engine = Orchestrator(store, backend)
    paused = engine.drive(engine.create(config, problem(), workflow=Workflow.SOLVE).id)
    assert paused.stop_reason == "Iteration budget reached" and paused.elapsed_seconds == 20

    advance(600)  # Human/queue idle time must not spend research time or reset it.
    config.budget.max_iterations = 3
    resumed = engine.resume(paused.id, config=config)
    assert resumed.id == paused.id
    assert resumed.state == State.PAUSED
    assert resumed.stop_reason == "Active wall-time budget reached"
    assert resumed.elapsed_seconds == 65
    assert [call["timeout"] for call in backend.calls] == [60, 40]
    assert [call["session"] for call in backend.calls] == [None, "test-solve-session"]
    assert len(resumed.candidates) == 2 and resumed.iteration == 2


def test_model_stop_during_solve_is_progress_in_the_same_session(store):
    backend = ScriptedBackend({"kind": "stop", "summary": "I have not solved it yet."}, candidate("COMPLETE"))
    engine = Orchestrator(store, backend)
    run = engine.drive(engine.create(Config(), problem(), workflow=Workflow.SOLVE).id)
    assert run.state == State.COMPLETED
    assert [call["session"] for call in backend.calls] == [None, "test-solve-session"]
    assert run.native.history[0]["milestone"]["kind"] == "stop"
    assert len(run.candidates) == 1 and run.candidates[0].scope == "COMPLETE"
    assert run.stop_reason != "I have not solved it yet."


@pytest.mark.parametrize("workflow", [Workflow.FIND, Workflow.VERIFY])
def test_model_stop_in_other_workflows_retains_its_existing_meaning(store, workflow):
    backend = ScriptedBackend({"kind": "stop", "summary": "Explicit stage conclusion."})
    engine = Orchestrator(store, backend)
    arguments = {"problem": problem(), "proof": "A submitted proof."} if workflow == Workflow.VERIFY else {}
    run = engine.drive(engine.create(Config(), workflow=workflow, **arguments).id)
    assert run.state == State.COMPLETED
    assert run.stop_reason == "Explicit stage conclusion."
    assert len(backend.calls) == 1


def test_real_user_stop_takes_precedence_over_budget_after_partial_save(store, monkeypatch):
    advance = clock(monkeypatch)

    def request_stop(_):
        engine._stop_file(created).write_text("Explicit user stop")
        advance(61)

    backend = ScriptedBackend(candidate(), on_call=request_stop)
    config = Config()
    config.budget.max_wall_time_minutes = 1
    engine = Orchestrator(store, backend)
    created = engine.create(config, problem(), workflow=Workflow.SOLVE)
    run = engine.drive(created.id)
    assert run.state == State.CANCELLED
    assert run.stop_reason == "Stopped by user"
    assert run.last_error is None and run.native.pending_result is None
    assert len(run.candidates) == len(backend.calls) == 1
    assert run.candidates[0].scope == "PARTIAL"


def positive_partial_review():
    claim = problem().statement
    return {
        "kind": "review", "review": {
            "verdict": "NO_ISSUES_FOUND", "truth_assessment": "The submitted identity holds.",
            "proof_assessment": "Its derivation is complete for the declared claim.",
            "checks": [{"id": "zero", "claim": claim, "method": "DERIVATION", "result": "SUPPORTED",
                        "reasoning": "Natural addition at zero is defined by n + 0 = n."}],
            "proof_steps": [{"id": "conclusion", "kind": "CONCLUSION", "statement": claim,
                             "check_ids": ["zero"]}],
        },
    }


def test_pipeline_still_reviews_partial_claims_without_finishing_them(store):
    backend = ScriptedBackend(candidate(), positive_partial_review())
    config = Config()
    config.budget.max_iterations = 2
    engine = Orchestrator(store, backend)
    run = engine.drive(engine.create(config, problem(), workflow=Workflow.PIPELINE).id)
    assert [call["reviewer"] for call in backend.calls] == [False, True]
    assert [call["session"] for call in backend.calls] == [None, None]
    assert run.candidates[0].reviews[-1].verdict == "NO_ISSUES_FOUND"
    assert not run.native.candidate_conclude
    assert run.state == State.PAUSED and run.phase == Phase.SOLVE
    assert run.stop_reason == "Iteration budget reached"


@pytest.mark.parametrize("legacy_conclude", [False, True])
def test_pipeline_review_cannot_finish_a_partial_even_with_a_legacy_conclude_flag(store, legacy_conclude):
    backend = ScriptedBackend(positive_partial_review())
    config = Config()
    config.budget.max_iterations = 1
    engine = Orchestrator(store, backend)
    run = engine.create(config, problem(), workflow=Workflow.PIPELINE)
    engine._candidate(run, CandidateInput.model_validate(candidate()["candidate"]))
    run.phase = Phase.VERIFY
    run.native.candidate_conclude = legacy_conclude
    store.save(run, "test_pending_partial_review")

    result = engine.drive(run.id)
    assert result.candidates[0].reviews[-1].verdict == "NO_ISSUES_FOUND"
    assert result.state == State.PAUSED and result.phase == Phase.SOLVE
    assert result.stop_reason == "Iteration budget reached"
    assert len(backend.calls) == 1 and backend.calls[0]["reviewer"]


@pytest.mark.parametrize("scope", ["COMPLETE", "COUNTEREXAMPLE"])
def test_full_solve_budget_keeps_complete_checkpoint_until_time_expires(store, monkeypatch, scope):
    advance = clock(monkeypatch)
    snapshots = []

    def track_progress(index):
        if index == 1:
            saved = store.load(created.id)
            assert saved.phase == Phase.SOLVE
            path = engine.candidates.path(saved, saved.candidates[0])
            snapshots.append((path, path.read_bytes()))
        advance(20 if index == 0 else 41)

    backend = ScriptedBackend(
        candidate(scope),
        {"kind": "progress", "summary": "Checked an additional endpoint without changing the claim."},
        on_call=track_progress,
    )
    config = Config()
    config.budget.finalize_minutes = 0  # Closing turns are covered separately in test_finalization.
    config.budget.solve_until_budget_exhausted = True
    config.budget.max_wall_time_minutes = 1
    engine = Orchestrator(store, backend)
    created = engine.create(config, problem(), workflow=Workflow.SOLVE)
    result = engine.drive(created.id)

    assert result.state == State.PAUSED and result.phase == Phase.SOLVE
    assert result.stop_reason == "Active wall-time budget reached"
    assert result.elapsed_seconds == 61 and result.active_since is None
    assert result.last_error is None and result.native.pending_result is None
    assert len(backend.calls) == 2 and len(result.candidates) == 1
    assert [call["session"] for call in backend.calls] == [None, "test-solve-session"]
    assert [call["timeout"] for call in backend.calls] == [60, 40]
    assert backend.calls[0]["workspace"] == backend.calls[1]["workspace"]
    assert all(not call["reviewer"] for call in backend.calls)
    assert result.candidates[0].scope == scope and not result.candidates[0].reviews
    assert result.native.history[0]["milestone"]["conclude"] is True
    assert result.native.history[0]["continuation_reason"]
    assert snapshots[0][0].read_bytes() == snapshots[0][1]
    assert result.usage.measured_calls == 2 and result.usage.input_tokens == 24
    # The first call and its continuation must both receive the requested policy.
    assert all("full active-time budget" in call["prompt"] for call in backend.calls)
    assert "finishes solving and leaves verification" not in backend.calls[0]["prompt"]


def test_enabling_full_solve_budget_on_resume_keeps_elapsed_time_and_saved_session(store, monkeypatch):
    advance = clock(monkeypatch)
    backend = ScriptedBackend(
        candidate(), candidate("COMPLETE"),
        {"kind": "stop", "summary": "No additional gap found in this route."},
        on_call=lambda index: advance([20, 20, 25][index]),
    )
    config = Config()
    config.budget.finalize_minutes = 0  # Closing turns are covered separately in test_finalization.
    config.budget.max_wall_time_minutes = 1
    config.budget.max_iterations = 1
    engine = Orchestrator(store, backend)
    paused = engine.drive(engine.create(config, problem(), workflow=Workflow.SOLVE).id)
    assert paused.elapsed_seconds == 20 and paused.stop_reason == "Iteration budget reached"

    advance(600)  # Neither a pause nor enabling the policy resets or spends active time.
    config.budget.solve_until_budget_exhausted = True
    config.budget.max_iterations = 5
    result = engine.resume(paused.id, config=config)

    assert result.id == paused.id and len(store.list_runs()) == 1
    assert result.config["budget"]["solve_until_budget_exhausted"] is True
    assert result.state == State.PAUSED and result.phase == Phase.SOLVE
    assert result.stop_reason == "Active wall-time budget reached" and result.elapsed_seconds == 65
    assert [call["timeout"] for call in backend.calls] == [60, 40, 20]
    assert [call["session"] for call in backend.calls] == [None, "test-solve-session", "test-solve-session"]
    assert [entry.scope for entry in result.candidates] == ["PARTIAL", "COMPLETE"]
    assert all(not entry.reviews for entry in result.candidates)
    assert result.native.history[-1]["milestone"]["kind"] == "stop"
    assert result.iteration == 3 and result.last_error is None


def test_user_stop_still_cancels_full_budget_after_complete_checkpoint(store, monkeypatch):
    advance = clock(monkeypatch)

    def stop(_):
        engine._stop_file(created).write_text("Explicit user stop")
        advance(10)

    backend = ScriptedBackend(candidate("COMPLETE"), on_call=stop)
    config = Config()
    config.budget.solve_until_budget_exhausted = True
    config.budget.max_wall_time_minutes = 1
    engine = Orchestrator(store, backend)
    created = engine.create(config, problem(), workflow=Workflow.SOLVE)
    result = engine.drive(created.id)

    assert result.state == State.CANCELLED and result.stop_reason == "Stopped by user"
    assert result.elapsed_seconds == 10 and len(backend.calls) == 1
    assert result.candidates[0].scope == "COMPLETE" and not result.candidates[0].reviews
    assert result.last_error is None


@pytest.mark.parametrize("field,limit,reason", [
    ("max_iterations", 1, "Iteration budget reached"),
    ("max_input_tokens", 12, "Measured input_tokens budget reached (checked between calls)"),
    ("max_output_tokens", 3, "Measured output_tokens budget reached (checked between calls)"),
])
def test_full_solve_budget_does_not_override_other_resource_limits(store, field, limit, reason):
    backend = ScriptedBackend(candidate("COMPLETE"))
    config = Config()
    config.budget.solve_until_budget_exhausted = True
    setattr(config.budget, field, limit)
    engine = Orchestrator(store, backend)
    result = engine.drive(engine.create(config, problem(), workflow=Workflow.SOLVE).id)

    assert result.state == State.PAUSED and result.stop_reason == reason
    assert result.phase == Phase.SOLVE and len(backend.calls) == 1
    assert result.candidates[0].scope == "COMPLETE" and result.last_error is None


@pytest.mark.parametrize("status,state", [
    (BackendStatus.RATE_LIMITED, State.RATE_LIMITED),
    (BackendStatus.FAILED, State.FAILED),
    (BackendStatus.INTERRUPTED, State.PAUSED),
])
def test_full_solve_budget_preserves_provider_interruptions_without_retrying(store, monkeypatch, status, state):
    backend = ScriptedBackend()
    calls = []

    def interrupted(*args, **kwargs):
        calls.append(kwargs["session_id"])
        assert len(calls) == 1, "Provider interruption must not silently retry"
        return BackendResult(status, invoked=True, error="Scripted provider interruption")

    monkeypatch.setattr(backend, "invoke_native", interrupted)
    config = Config()
    config.budget.solve_until_budget_exhausted = True
    engine = Orchestrator(store, backend)
    result = engine.drive(engine.create(config, problem(), workflow=Workflow.SOLVE).id)

    assert result.state == state and result.last_error == "Scripted provider interruption"
    assert result.stop_reason == "Scripted provider interruption" and len(calls) == 1
    assert not result.candidates and result.native.pending_result is None


@pytest.mark.parametrize("workflow", [Workflow.FIND, Workflow.VERIFY])
def test_full_solve_budget_is_not_applied_to_other_standalone_stages(store, workflow):
    backend = ScriptedBackend({"kind": "stop", "summary": "Stage finished honestly."})
    config = Config()
    config.budget.solve_until_budget_exhausted = True
    engine = Orchestrator(store, backend)
    arguments = {"problem": problem(), "proof": "A submitted proof."} if workflow == Workflow.VERIFY else {}
    result = engine.drive(engine.create(config, workflow=workflow, **arguments).id)

    assert result.state == State.COMPLETED and result.stop_reason == "Stage finished honestly."
    assert len(backend.calls) == 1 and "full active-time budget" not in backend.calls[0]["prompt"]


def test_full_solve_budget_does_not_prevent_pipeline_review_completion(store):
    backend = ScriptedBackend(candidate("COMPLETE"), positive_partial_review())
    config = Config()
    config.budget.solve_until_budget_exhausted = True
    engine = Orchestrator(store, backend)
    result = engine.drive(engine.create(config, problem(), workflow=Workflow.PIPELINE).id)

    assert result.state == State.COMPLETED and len(backend.calls) == 2
    assert [call["reviewer"] for call in backend.calls] == [False, True]
    assert result.candidates[0].scope == "COMPLETE"
    assert result.candidates[0].reviews[-1].verdict == "NO_ISSUES_FOUND"
    assert all("full active-time budget" not in call["prompt"] for call in backend.calls)
