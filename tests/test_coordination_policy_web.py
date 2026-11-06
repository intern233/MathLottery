"""Browser selection of optional coordination tuning; fake accounts, no model calls."""

import pytest
from test_web import SIGNED_IN, serving
from test_web import web as web
from test_web_frontend_modules import browser as browser

from mathlottery.models import Problem, Workflow
from mathlottery.runtime.orchestrator import Orchestrator
from mathlottery.web.requests import ResumeRequest


@pytest.mark.parametrize("flag", [False, True])
def test_start_saves_task_toggle_without_editing_global_configuration(web, monkeypatch, flag):
    original = (web.store.root / "config.yaml").read_bytes()
    launches = []
    monkeypatch.setattr(web.jobs, "launch", lambda *a, **kw: launches.append((a, kw)))
    with serving(web, account_status=SIGNED_IN) as (client, server):
        response = client.post("/api/runs", json={"workflow": "solve", "statement": "For all n, n+0=n",
            "options": {"solve_parallel_agents": 2, "solve_adaptive_coordination": flag}},
            headers={"X-MathLottery-Token": server.csrf_token})
        assert response.status_code == 202, response.text
        data = response.json()
        assert data["settings"]["solve_adaptive_coordination"] is flag
        saved = web.store.load(data["id"])
        assert saved.config["solve"]["adaptive_coordination"] is flag
    assert len(launches) == 1 and (web.store.root / "config.yaml").read_bytes() == original


@pytest.mark.parametrize("saved_flag", [False, True])
@pytest.mark.parametrize("requested_flag", [None, False, True])
def test_resume_preserves_omitted_toggle_and_applies_explicit_user_choice(web, monkeypatch, saved_flag, requested_flag):
    config = web.config()
    config.solve.parallel_agents = 2
    config.solve.adaptive_coordination = saved_flag
    run = Orchestrator(web.store).create(config, Problem(id="identity", title="Identity", statement="n+0=n"), workflow=Workflow.SOLVE)
    before = web.store.load(run.id)
    launches = []
    monkeypatch.setattr(web.jobs, "launch", lambda *a, **kw: launches.append((a, kw)))
    request = ResumeRequest(message="Continue", solve_adaptive_coordination=requested_flag)
    web.resume(run.id, request)
    expected = saved_flag if requested_flag is None else requested_flag
    queued = launches[0][1]["config"]
    assert queued["solve"]["adaptive_coordination"] is expected
    assert queued["backend"] == before.config["backend"]
    assert web.store.load(run.id).config == before.config


def test_toggle_does_not_apply_to_find_or_missing_parallelism(web, monkeypatch):
    monkeypatch.setattr(web.jobs, "launch", lambda *a, **kw: pytest.fail("Invalid request launched"))
    with serving(web, account_status=SIGNED_IN) as (client, server):
        headers = {"X-MathLottery-Token": server.csrf_token}
        for body in [
            {"workflow": "find", "query": "A problem", "options": {"solve_adaptive_coordination": True}},
            {"workflow": "solve", "statement": "n+0=n", "options": {"solve_adaptive_coordination": True}},
        ]:
            response = client.post("/api/runs", json=body, headers=headers)
            assert response.status_code == 400
    assert not web.store.list_runs()


def test_browser_start_and_resume_submit_explicit_toggle(web, monkeypatch, browser):
    launches = []
    monkeypatch.setattr(web.jobs, "launch", lambda *a, **kw: launches.append((a, kw)))
    monkeypatch.setattr("mathlottery.web.server.codex_models", lambda *a: {"data": [{
        "model": "configured-model", "supportedReasoningEfforts": [{"reasoningEffort": "high"}],
    }]})
    with serving(web, account_status=SIGNED_IN) as (_, server):
        context = browser.new_context(locale="zh-CN")
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        try:
            page.goto(f"http://127.0.0.1:{server.server_port}")
            page.locator('[data-workflow="solve"]').click()
            page.locator('#task-form [data-i18n="budgetSettings"]').click()
            assert not page.locator("#solve-adaptive").is_checked()
            page.locator("#solve-parallel").fill("2")
            page.locator("#solve-adaptive").check()
            page.locator("#statement").fill("For all natural n, n+0=n")
            page.wait_for_function("!document.querySelector('#start').disabled")
            with page.expect_response(lambda r: r.request.method == "POST" and r.url.endswith("/api/runs")) as posted:
                page.locator("#start").click()
            data = posted.value.json()
            assert posted.value.status == 202 and data["settings"]["solve_adaptive_coordination"]
            page.locator("#show-resume").click()
            assert page.locator("#resume-adaptive").is_checked()
            page.locator("#resume-adaptive").uncheck()
            page.locator("#direction").fill("Continue with the default coordination policy")
            with page.expect_response(lambda r: r.request.method == "POST" and r.url.endswith("/resume")) as resumed:
                page.locator("#resume-submit").click()
            assert resumed.value.status == 202
            assert launches[-1][1]["config"]["solve"]["adaptive_coordination"] is False
            assert not errors
        finally:
            context.close()
