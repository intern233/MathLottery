"""Completed search evidence survives interrupted turns; no model or network research."""

import json

import pytest
from test_native import native_config as native_config
from test_web import serving

from mathlottery.config import Config
from mathlottery.models import LiteratureSearch, State, Workflow
from mathlottery.providers.base import BackendResult, BackendStatus
from mathlottery.providers.codex import NativeWorkBackend
from mathlottery.runtime.orchestrator import Orchestrator
from mathlottery.verify.policy import assess_sources
from mathlottery.web.service import WebService


@pytest.mark.parametrize("behavior,state", [
    ("search_then_slow", State.PAUSED), ("search_then_rate", State.RATE_LIMITED),
    ("search_partial_milestone", State.PAUSED),
])
def test_completed_search_survives_interruption_resume_database_and_http(
    store, native_config, monkeypatch, behavior, state,
):
    monkeypatch.setenv("MATHLOTTERY_NATIVE_FAKE", behavior)
    native_config.backend.native_turn_timeout_seconds = 1
    engine = Orchestrator(store)
    run = engine.drive(engine.create(native_config, workflow=Workflow.FIND).id)
    assert run.state == state and not run.shortlist and not run.candidates
    assert run.native.history[0]["runtime"]["tool_observations_confirmed"]
    assert "milestone" not in run.native.history[0]
    saved = store.load(run.id)
    searches = [item for item in saved.observations if item["tool"] == "native_search"]
    sources = [item for item in saved.observations if item["tool"] == "native_source"]
    assert len(searches) == len(sources) == 1
    assert searches[0]["result"]["queries"] == ["completed exact conjecture search"]
    assert sources[0]["result"]["url"] == "https://example.org/completed-paper"
    assert searches[0]["phase"] == "FIND"
    original_time = searches[0]["result"]["retrieved_at"]
    assert original_time == saved.native.history[0]["source_observed_at"]
    assert not any(item.get("result", {}).get("record_kind") == "source_snapshot" for item in saved.observations)

    # The next turn only submits its dossier. It does not repeat any search.
    monkeypatch.setenv("MATHLOTTERY_NATIVE_FAKE", "selection_after_search")
    resumed = engine.resume(run.id)
    assert resumed.state == State.COMPLETED
    assert resumed.native.solver_session_id == saved.native.solver_session_id
    assert resumed.native.history[-1]["runtime"]["search_queries"] == []
    assert [item for item in resumed.observations if item["tool"] == "native_search"] == searches
    assessment = resumed.shortlist[0].evidence_assessment
    assert assessment.observed_queries == ["completed exact conjecture search"]
    assert not assessment.supported  # Searches alone do not establish a source/open-status claim.
    with serving(WebService(store.root)) as (client, _):
        response = client.get(f"/api/runs/{run.id}")
        assert response.status_code == 200
        projected = response.json()["shortlist"][0]["evidence_assessment"]
        assert projected["observed_queries"] == assessment.observed_queries
        assert not projected["supported"]


@pytest.mark.parametrize("behavior", ["search_missing_session", "search_wrong_session"])
def test_search_events_without_the_expected_session_never_form_receipts(tmp_path, native_config, monkeypatch, behavior):
    monkeypatch.setenv("MATHLOTTERY_NATIVE_FAKE", behavior)
    backend = NativeWorkBackend(native_config.backend, root=tmp_path)
    session = "11111111-1111-4111-8111-111111111111" if behavior == "search_wrong_session" else None
    if session:
        folder = backend.identity.home / "sessions"
        folder.mkdir(parents=True)
        (folder / f"rollout-{session}.jsonl").write_text("{}\n")
    result = backend.invoke_native(
        "run_id: run-123456789012\ntask_id: task-example\n",
        tmp_path / "attempt", tmp_path / "work", 3, session_id=session,
    )
    assert result.status in {BackendStatus.FAILED, BackendStatus.INTERRUPTED}
    assert not result.runtime["tool_observations_confirmed"]
    assert result.runtime["search_queries"] == result.runtime["source_urls"] == []


@pytest.mark.parametrize("confirmed,matching", [(False, True), (True, False)])
def test_interrupted_observation_metadata_requires_confirmation_and_current_session(store, confirmed, matching):
    class ScriptedBackend:
        def invoke_native(self, *args, **kwargs):
            kwargs["on_session"]("expected-fixture-session")
            return BackendResult(
                BackendStatus.INTERRUPTED, invoked=True, error="Turn interrupted",
                session_id="expected-fixture-session" if matching else "other-task-session",
                runtime={"tool_observations_confirmed": confirmed, "search_queries": ["untrusted query"],
                         "source_urls": ["https://example.org/other"]},
            )

    engine = Orchestrator(store, ScriptedBackend())
    run = engine.drive(engine.create(Config(), workflow=Workflow.FIND).id)
    assert store.load(run.id).observations == []


def test_interrupted_search_keeps_original_timestamp_and_cannot_refresh_stale_evidence(store):
    old_time = "2000-01-01T00:00:00+00:00"

    class ScriptedBackend:
        def invoke_native(self, prompt, directory, *args, **kwargs):
            turn = json.loads((directory / "turn.json").read_text())
            turn["started_at"] = old_time
            (directory / "turn.json").write_text(json.dumps(turn))
            kwargs["on_session"]("expected-fixture-session")
            return BackendResult(
                BackendStatus.INTERRUPTED, invoked=True, error="Turn interrupted",
                session_id="expected-fixture-session",
                runtime={"tool_observations_confirmed": True, "search_queries": ["old query"]},
            )

    engine = Orchestrator(store, ScriptedBackend())
    run = engine.drive(engine.create(Config(), workflow=Workflow.FIND).id)
    observations = store.load(run.id).observations
    assert len(observations) == 1 and observations[0]["result"]["retrieved_at"] == old_time
    assessment = assess_sources([], LiteratureSearch(queries=["old query"], conclusion="A saved search."),
                                [item["result"] for item in observations])
    assert assessment.observed_queries == []
    assert any("no recent observed search-tool receipt" in reason for reason in assessment.reasons)


@pytest.mark.parametrize("behavior", ["search_before_session", "search_session_changes"])
def test_search_receipts_cannot_cross_session_confirmation_boundaries(store, native_config, monkeypatch, behavior):
    monkeypatch.setenv("MATHLOTTERY_NATIVE_FAKE", behavior)
    native_config.budget.max_iterations = 1
    engine = Orchestrator(store)
    run = engine.drive(engine.create(native_config, workflow=Workflow.FIND).id)
    assert not store.load(run.id).observations
    assert not run.shortlist and not run.candidates
    if behavior == "search_before_session":
        assert run.native.history[0]["runtime"]["tool_observations_confirmed"]
        assert run.native.history[0]["runtime"]["search_queries"] == []
    else:
        assert not run.native.history[0]["runtime"]["tool_observations_confirmed"]
