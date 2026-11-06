"""Opt-in policy tuning, persistence and rejection without paid model calls."""

import json
from datetime import datetime, timedelta

import pytest
from test_solve_campaign import CampaignBackend, setup

from mathlottery.config import Config
from mathlottery.models import State
from mathlottery.solve.board import Message, SolveBoard
from mathlottery.solve.board_tools import BoardTools
from mathlottery.solve.bulletin.contracts import BoardEvent
from mathlottery.solve.bulletin.curation import suggestions
from mathlottery.solve.coordination_policy import (
    decide,
    defaults,
    history,
    needs_review,
    snapshot,
    view,
)
from mathlottery.web.requests import Overrides


def proposal(revision=0, **changes):
    return {"base_revision": revision,
            "policy": {"review_interval_seconds": 60, "archive_min_age_seconds": 60,
                       "archive_read_threshold": 2, "board_guidance": "Publish exact hypotheses",
                       "collaboration_guidance": "Compare endpoint calculations", **changes},
            "evidence": ["metrics"], "rationale": "Review concrete research friction",
            "expected_effect": "Peers can locate and compare endpoint lemmas",
            "previous_assessment": "No previous intervention; benefit remains unmeasured"}


def enabled_run(store):
    engine, run = setup(store, CampaignBackend())
    run.config["solve"]["adaptive_coordination"] = True
    store.save(run, "enabled_for_test")
    return engine, run, SolveBoard(store, run.id)


def attempt(run, board, task="policy-turn"):
    return {"task_id": task, "purpose": "review", "coordination_snapshot": snapshot(run, board)}


def commit(store, run, update, observed=None):
    run.native.solve_team.campaign.decisions.append({"coordination_update": update,
                                                     "coordination_observation": observed})
    store.save(run, "fixture_policy_receipt")


def test_default_and_old_configs_do_not_enable_tuning():
    assert not Config().solve.adaptive_coordination
    data = Config().model_dump()
    data["solve"].pop("adaptive_coordination")
    assert not Config.model_validate(data).solve.adaptive_coordination
    with pytest.raises(ValueError, match="explicit parallelism"):
        Overrides(solve_adaptive_coordination=True).apply(Config())
    configured = Overrides(solve_parallel_agents=2, solve_adaptive_coordination=True).apply(Config())
    assert configured.solve.adaptive_coordination and configured.solve.parallel_agents == 2
    with pytest.raises(ValueError):
        Overrides(solve_adaptive_coordination="true")


@pytest.mark.parametrize("mutation,reason", [
    ({"base_revision": 7}, "stale"),
    ({"evidence": ["board:invented"]}, "snapshot"),
    ({"policy": {"review_interval_seconds": 1}}, "30–3600"),
    ({"policy": {"parallel_agents": 32}}, "Extra inputs"),
    ({"policy": {"archive_min_age_seconds": 0}}, "greater than"),
    ({"rationale": " "}, "Describe"),
])
def test_invalid_policy_is_advisory_and_never_mutates_budget_or_accounts(store, mutation, reason):
    _, run, board = enabled_run(store)
    before = json.dumps(run.config, sort_keys=True)
    result = decide(run, attempt(run, board), {**proposal(), **mutation})
    assert result["status"] == "rejected" and reason in result["feedback"]
    assert json.dumps(run.config, sort_keys=True) == before
    assert view(run)["revision"] == 0


def test_policy_roundtrip_disable_and_restore_keeps_audit(store):
    _, run, board = enabled_run(store)
    update = decide(run, attempt(run, board), proposal())
    assert update["status"] == "applied" and update["revision"] == 1
    commit(store, run, update)
    restored = store.load(run.id)
    assert view(restored)["policy"]["review_interval_seconds"] == 60
    assert restored.config["solve"]["board_review_interval_seconds"] == 300
    restored.config["solve"]["adaptive_coordination"] = False
    assert view(restored)["policy"] == defaults(restored).model_dump()
    assert history(restored) == [update]
    denied = decide(restored, attempt(restored, board), proposal(1))
    assert denied["status"] == "rejected" and "disabled" in denied["feedback"]
    restored.config["solve"]["adaptive_coordination"] = True
    assert view(restored)["policy"] == update["after"]
    rollback = decide(restored, attempt(restored, board, "rollback"),
                      proposal(1, **defaults(restored).model_dump()))
    commit(store, restored, rollback)
    assert view(restored)["revision"] == 2 and view(restored)["policy"] == defaults(restored).model_dump()
    assert len(history(restored)) == 2


@pytest.mark.parametrize("bad", ["not an object", ["unexpected"], proposal(review_interval_seconds=float("nan"))])
def test_malformed_optional_update_keeps_receipt_safe_for_browser_json(store, bad):
    _, run, board = enabled_run(store)
    receipt = decide(run, attempt(run, board), bad)
    assert receipt["status"] == "rejected"
    json.dumps(receipt, allow_nan=False)


def test_threshold_changes_only_suggestions_and_runtime_tools_see_current_policy(store, monkeypatch):
    _, run, board = enabled_run(store)
    workspace = store.run_dir(run.id) / "workspace"
    workspace.mkdir(exist_ok=True)
    board.publish("peer", "g", Message(id="note", kind="failed_route", title="An old route", body="Useful context"), workspace)
    board.event("peer", "g", BoardEvent(id="read", action="read", focus=["peer:note"]))

    class Later(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime.now(tz) + timedelta(seconds=120)

    monkeypatch.setattr("mathlottery.solve.bulletin.curation.datetime", Later)
    assert not suggestions(board)["candidates"]
    commit(store, run, decide(run, attempt(run, board), proposal()))
    assert [v["key"] for v in suggestions(board)["candidates"]] == ["peer:note"]
    assert not board.read("peer:note")["archived"]
    board.project(workspace)
    projected = json.loads((workspace / "bulletin/policy.json").read_text())
    hosted = BoardTools(board, "peer", "g", workspace).execute("solve_board_status", {})
    assert projected["revision"] == hosted["coordination_policy"]["revision"] == 1
    assert json.loads((store.run_dir(run.id) / "solve/coordination-policy.json").read_text())["history"]


def test_activity_can_request_periodic_review_but_reads_and_supervisor_notes_cannot(store):
    _, run, board = enabled_run(store)
    commit(store, run, None, snapshot(run, board)["observation"])
    workspace = store.run_dir(run.id) / "workspace"
    workspace.mkdir(exist_ok=True)
    board.publish("supervisor", "g", Message(id="note", kind="intent", title="Plan", body="A plan"), workspace)
    board.event("peer", "g", BoardEvent(id="read", action="read", focus=["supervisor:note"]))
    assert not needs_review(run, board)
    board.event("peer", "g", BoardEvent(id="help", action="activity", summary="Need a parameter bound"))
    assert needs_review(run, board)
    run.config["solve"]["adaptive_coordination"] = False
    assert not needs_review(run, board)


def test_campaign_applies_assesses_and_reverts_policy_with_same_research_session(store):
    observed = []

    def supervise(backend, payload, context, kwargs):
        revision = context["coordination"]["revision"]
        if revision == 0:
            payload["coordination_update"] = proposal()
        elif revision == 1:
            payload["coordination_update"] = proposal(1, review_interval_seconds=300,
                archive_min_age_seconds=600, archive_read_threshold=0, board_guidance="", collaboration_guidance="")
            payload["coordination_update"]["previous_assessment"] = "Benefit not established; return to baseline"

    def research(backend, author, workspace, kwargs, turn):
        observed.append(json.loads((workspace / "bulletin/policy.json").read_text()))

    backend = CampaignBackend(reject_first=True, supervision=supervise, research=research)
    engine, run = setup(store, backend)
    run.config["solve"]["adaptive_coordination"] = True
    store.save(run, "enable_test")
    result = engine.drive(run.id)
    assert result.state == State.COMPLETED, result.last_error
    assert [v["policy"]["review_interval_seconds"] for v in observed] == [60, 300]
    assert [v["revision"] for v in history(result)] == [1, 2]
    research_calls = [c for c in backend.calls if c["author"] == "primary"]
    assert [c["session"] for c in research_calls] == [None, "session-primary"]
    assert "Compare endpoint calculations" in research_calls[0]["prompt"]
    assert result.config["solve"]["parallel_agents"] == 1 and not result.candidates[-1].reviews


@pytest.mark.parametrize("enabled", [False, True])
@pytest.mark.parametrize("bad", [
    {"unrecognized_setting": "never execute"},
    "not an object",
    proposal(review_interval_seconds=float("nan")),
])
def test_disabled_or_invalid_tuning_does_not_abort_valid_mathematics(store, enabled, bad):
    def supervise(backend, payload, context, kwargs):
        payload["coordination_update"] = bad

    engine, run = setup(store, CampaignBackend(supervision=supervise))
    run.config["solve"]["adaptive_coordination"] = enabled
    store.save(run, "configuration_test")
    result = engine.drive(run.id)
    assert result.state == State.COMPLETED and result.native.solve_team.campaign.accepted_candidate_id
    assert all(v["status"] == "rejected" for v in history(result))
    assert view(result)["revision"] == 0
    # The complete durable record, including native history, must remain valid
    # for strict browser JSON; rejecting the policy receipt alone is insufficient.
    json.dumps(store.load(result.id).model_dump(mode="json"), allow_nan=False)
