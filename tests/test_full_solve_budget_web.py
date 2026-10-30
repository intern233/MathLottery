"""Browser request contracts for full-budget Solve; never call a model or real account."""

import pytest
from test_web import SIGNED_IN, serving
from test_web import web as web

from mathlottery.models import Problem, Workflow
from mathlottery.runtime.orchestrator import Orchestrator
from mathlottery.web.service import ResumeRequest


@pytest.mark.parametrize("enabled", [False, True])
def test_http_start_persists_full_solve_budget_for_only_this_task(web, monkeypatch, enabled):
    config_before = (web.store.root / "config.yaml").read_bytes()
    launches = []
    monkeypatch.setattr(web.jobs, "launch", lambda *a, **kw: launches.append((a, kw)))
    with serving(web, account_status=SIGNED_IN) as (client, server):
        response = client.post("/api/runs", json={
            "workflow": "solve", "statement": "For every natural n, n + 0 = n.",
            "options": {"solve_until_budget_exhausted": enabled, "budget_minutes": 360},
        }, headers={"X-MathLottery-Token": server.csrf_token})
        assert response.status_code == 202, response.text
        created = response.json()
        assert created["settings"]["solve_until_budget_exhausted"] is enabled
        saved = web.store.load(created["id"])
        assert saved.config["budget"]["solve_until_budget_exhausted"] is enabled
        assert saved.config["budget"]["max_wall_time_minutes"] == 360
        detail = client.get(f"/api/runs/{saved.id}").json()
        assert detail["settings"]["solve_until_budget_exhausted"] is enabled

    assert launches == [((saved.id, "drive"), {})]
    assert (web.store.root / "config.yaml").read_bytes() == config_before


@pytest.mark.parametrize("saved_flag", [False, True])
@pytest.mark.parametrize("requested_flag", [None, False, True])
def test_resume_preserves_omitted_full_budget_policy_and_accepts_explicit_toggle(
    web, monkeypatch, saved_flag, requested_flag,
):
    config = web.config()
    config.budget.solve_until_budget_exhausted = saved_flag
    config.backend.model = "saved-research-model"
    run = Orchestrator(web.store).create(config, problem=Problem(
        id="test-addition", title="Addition identity", statement="For every natural n, n + 0 = n.",
    ), workflow=Workflow.SOLVE)
    run.elapsed_seconds = 1200
    run.native.solver_session_id = "test-saved-research-session"
    web.store.save(run, "test_saved_partial_research")
    saved = web.store.load(run.id)
    launches = []
    monkeypatch.setattr(web.jobs, "launch", lambda *a, **kw: launches.append((a, kw)))
    request = {"message": "Continue from the saved research.", "budget_minutes": 360}
    if requested_flag is not None:
        request["solve_until_budget_exhausted"] = requested_flag

    response = web.resume(run.id, ResumeRequest.model_validate(request))

    assert response["id"] == run.id and len(launches) == 1
    args, payload = launches[0]
    assert args == (run.id, "resume")
    expected = saved_flag if requested_flag is None else requested_flag
    assert payload["config"]["budget"]["solve_until_budget_exhausted"] is expected
    assert payload["config"]["budget"]["max_wall_time_minutes"] == 360
    assert payload["config"]["backend"] == saved.config["backend"]
    assert payload["message"] == request["message"]
    # Applying a queued change belongs to the worker. HTTP must not alter the
    # old checkpoint, erase active time or fork a fresh research session.
    unchanged = web.store.load(run.id)
    assert unchanged.config == saved.config
    assert unchanged.elapsed_seconds == 1200
    assert unchanged.native.solver_session_id == "test-saved-research-session"
    assert len(web.store.list_runs()) == 1
