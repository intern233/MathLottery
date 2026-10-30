"""A dead local worker must not spend its remaining budget while the host is off."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone

import pytest
from test_solve_continuation import ScriptedBackend, candidate, problem

from mathlottery.config import Config
from mathlottery.models import CandidateInput, State, Workflow
from mathlottery.runtime import budget
from mathlottery.runtime.orchestrator import Orchestrator
from mathlottery.storage.core import atomic_write, json_text
from mathlottery.web.service import WebService


@pytest.fixture
def crashed(store, monkeypatch):
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    current = start + timedelta(hours=20)
    monkeypatch.setattr(budget, "now", lambda: current.isoformat())
    monkeypatch.setattr("mathlottery.runtime.native.now", lambda: current.isoformat())
    config = Config()
    config.budget.max_wall_time_minutes = 10
    config.budget.max_iterations = 2
    config.budget.solve_until_budget_exhausted = True
    engine = Orchestrator(store)
    run = engine.create(config, problem(), workflow=Workflow.SOLVE)
    run.active_since = start.isoformat()
    run.elapsed_seconds = 60
    run.state = State.SOLVING
    run.native.solver_session_id = "test-solve-session"
    run.native.active_attempt = "tasks/task-crashed/attempt-crashed"
    engine._candidate(run, CandidateInput.model_validate(candidate()["candidate"]))
    store.save(run, "test_crash")
    resources = {
        "state": "interrupted", "started_at": start.isoformat(),
        "updated_at": (start + timedelta(minutes=7)).isoformat(),
    }
    atomic_write(store.run_dir(run.id) / "resources.json", json_text(resources))
    return engine, run, resources


def test_resume_after_host_restart_preserves_session_results_and_remaining_budget(store, crashed):
    _, run, resources = crashed
    saved = store.run_dir(run.id) / "candidates" / f"{run.candidates[0].id}.json"
    original = saved.read_bytes()
    observed_errors = []
    backend = ScriptedBackend(candidate("PARTIAL", conclude=False),
                              on_call=lambda _: observed_errors.append(store.load(run.id).last_error))
    result = Orchestrator(store, backend).resume(run.id, message="Continue the same problem after restart.")
    assert len(backend.calls) == 1
    assert observed_errors == [None]
    assert backend.calls[0]["session"] == "test-solve-session"
    assert backend.calls[0]["timeout"] == pytest.approx(120, abs=0.01)
    assert result.elapsed_seconds == 480
    assert result.active_since is None
    assert result.stop_reason == "Iteration budget reached"
    assert result.native.history[0]["status"] == "INTERRUPTED"
    assert result.iteration == 2 and result.usage.unknown_calls == 1
    assert len(result.candidates) == 2 and saved.read_bytes() == original
    # Interrupted work was not silently accepted as a completed proof.
    assert all(not item.reviews for item in result.candidates)
    from test_resume_errors import recorded_errors

    assert "Recovered an interrupted native attempt; its token usage is unknown" in recorded_errors(store, run.id)


def test_idle_web_clock_stops_at_observed_time_without_mutating_checkpoint(store, crashed, monkeypatch):
    _, run, _ = crashed
    service = WebService(store.root)
    before = store.load(run.id).model_dump()
    value = service.summary(run)
    assert not value["busy"]
    assert value["elapsed_seconds"] == 480
    assert value["elapsed_timing_basis"] == "last_resource_sample"
    assert value["resources"]["state"] == "interrupted"
    assert store.load(run.id).model_dump() == before
    monkeypatch.setattr(budget, "now", lambda: "2026-01-03T00:00:00+00:00")
    assert service.summary(run)["elapsed_seconds"] == 480
    # Never freeze a genuinely live worker based on a stale projection.
    monkeypatch.setattr(service.jobs, "running", lambda *a, **kw: True)
    assert service.summary(run)["elapsed_timing_basis"] == "wall_clock"


@pytest.mark.parametrize("change", [
    {"state": "running"}, {"state": "queued"},
    {"started_at": "2026-01-01T01:00:00+00:00"},
    {"updated_at": "2025-12-31T23:59:00+00:00"},
    {"updated_at": "2026-02-01T00:00:00+00:00"},
    {"updated_at": "2026-01-01T00:07:00"}, {"updated_at": "invalid"},
])
def test_invalid_or_other_execution_samples_do_not_reset_time(crashed, change):
    _, run, resources = crashed
    assert budget.interrupted_elapsed(run, {**resources, **change}) is None


@pytest.mark.parametrize("mode,execution", [("chat", "native"), ("codex", "structured")])
def test_remote_or_legacy_execution_keeps_its_existing_accounting(crashed, mode, execution):
    _, run, resources = crashed
    run = deepcopy(run)
    run.mode, run.execution = mode, execution
    assert budget.interrupted_elapsed(run, resources) is None
