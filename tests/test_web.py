"""Local HTTP and background-process contracts; scripted agents, no model billing."""

import json
import os
import sys
import threading
import time
from contextlib import contextmanager

import httpx
import pytest
import yaml
from test_native import FAKE_NATIVE
from typer.testing import CliRunner

from mathlottery.cli import app
from mathlottery.config import Config
from mathlottery.models import CandidateInput, FormalCheckRequest, Problem, Review, Workflow
from mathlottery.orchestrator import Orchestrator
from mathlottery.web.jobs import BusyError
from mathlottery.web.server import LocalServer
from mathlottery.web.service import ResumeRequest, StartRequest, WebService

SIGNED_IN = {
    "available": True, "authenticated": True,
    "account": {"type": "chatgpt", "email": "t***@example.com", "plan_type": "pro"},
    "login": None,
}


@contextmanager
def serving(service, *, account_status=None):
    server = LocalServer(service, port=0)
    if account_status is not None:
        # Scripted research fixtures do not implement account RPC. Never inspect real logins.
        server.account.status = lambda: account_status
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
    thread.start()
    try:
        with httpx.Client(base_url=f"http://127.0.0.1:{server.server_port}", trust_env=False) as client:
            yield client, server
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


@pytest.fixture
def web(tmp_path, monkeypatch):
    executable = tmp_path / "scripted-codex"
    executable.write_text(f"#!{sys.executable}\n" + FAKE_NATIVE)
    executable.chmod(0o755)
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "scripted-codex-home"))
    monkeypatch.setenv("MATHLOTTERY_NATIVE_FAKE", "three_tasks")
    monkeypatch.setenv("OPENAI_API_KEY", "test-secret-never-sent-to-browser")
    config = Config()
    config.backend.codex_command = str(executable)
    config.backend.model = "configured-model"
    config.backend.reasoning_effort = "high"
    config.budget.max_wall_time_minutes = 1
    config.budget.max_iterations = 3
    (tmp_path / "config.yaml").write_text(yaml.safe_dump(config.model_dump(mode="json")))
    service = WebService(tmp_path)
    yield service
    # Never leave a slow fixture process behind, including after a failed assertion.
    for run in service.store.list_runs():
        if service.jobs.running(run.id):
            service.stop(run.id)
            wait_for(lambda: not service.jobs.running(run.id))


def wait_for(predicate, seconds=15):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        time.sleep(0.05)
    raise AssertionError("Timed out waiting for background worker")


def finished(web, run_id):
    wait_for(lambda: not web.jobs.running(run_id))
    return web.detail(run_id)


def test_api_exposes_partial_coverage_missing_sources_and_formal_failures(web):
    engine = Orchestrator(web.store)
    run = engine.create(web.config(), Problem(id="coverage-fixture", title="Coverage fixture", statement="All n"),
                        candidate=CandidateInput(claim="Only n=0", proof="By substitution", scope="PARTIAL",
                                                 remaining_obligations=["All positive n"]))
    run.iteration = 1
    engine.candidates.review(run, Review(
        verdict="NO_ISSUES_FOUND", truth_assessment="Base case holds", proof_assessment="Substitution checked",
        checks=[{"claim": "Base case", "method": "DERIVATION", "result": "SUPPORTED", "reasoning": "Substitute zero"}],
        original_problem_coverage="FULL", coverage_explanation="An unsupported completeness claim",
        novelty="POTENTIALLY_NEW", formal_check=FormalCheckRequest(files=["workspace/Main.lean"], declarations=["target"]),
    ))
    engine._finish(run, "Scripted coverage fixture, not a mathematical success")
    with serving(web, account_status=SIGNED_IN) as (client, _):
        data = client.get(f"/api/runs/{run.id}").json()
        candidate = data["candidates"][-1]
        review = candidate["reviews"][-1]
        assert candidate["level"] == "SELF_CHECKED"
        assert review["original_problem_coverage"] == "PARTIAL"
        assert review["remaining_obligations"] == ["All positive n"]
        assert review["novelty"] == "UNKNOWN"
        assert review["evidence_assessment"]["reasons"]
        assert review["formal_receipt"]["status"] == "UNAVAILABLE"
        report = client.get(f"/api/runs/{run.id}/report").text
        assert "Original-problem coverage: **PARTIAL**" in report
        assert "All positive n" in report and "UNAVAILABLE" in report


def test_http_find_solve_verify_uses_shared_checkpoints_and_independent_review(web, monkeypatch):
    personal_home = web.store.root / "scripted-codex-home"
    personal_home.mkdir()
    sentinel = b'{"test_only": "personal login must stay unchanged"}'
    (personal_home / "auth.json").write_bytes(sentinel)
    env_log = web.store.root / "worker-codex-env.jsonl"
    monkeypatch.setenv("MATHLOTTERY_FAKE_ENV_LOG", str(env_log))
    with serving(web, account_status=SIGNED_IN) as (client, _):
        bootstrap = client.get("/api/bootstrap")
        assert bootstrap.status_code == 200
        assert "test-secret-never-sent-to-browser" not in bootstrap.text
        assert "codex_command" not in bootstrap.text
        client.headers["X-MathLottery-Token"] = bootstrap.json()["csrf_token"]
        response = client.post("/api/runs", json={"workflow": "find", "query": "Small problems", "count": 2})
        assert response.status_code == 202, response.text
        found = finished(web, response.json()["id"])
        assert found["state"] == "COMPLETED"
        assert found["shortlist"][0]["status"] == "UNKNOWN"
        problem_id = found["shortlist"][0]["id"]
        response = client.post("/api/runs", json={"workflow": "solve", "problem_id": problem_id,
                                                  "from_discovery": found["id"],
                                                  "discovery_problem_sha256": found["shortlist_bindings"][problem_id]})
        assert response.status_code == 202, response.text
        solved = finished(web, response.json()["id"])
        assert solved["state"] == "COMPLETED"
        assert solved["candidates"][0]["reviews"] == []
        response = client.post("/api/runs", json={"workflow": "verify", "from_run": solved["id"]})
        assert response.status_code == 202, response.text
        reviewed = finished(web, response.json()["id"])
        assert reviewed["workflow"] == "verify"
        assert found["problem_id"] is None and found["problem_key"] is None
        assert solved["problem_id"] == reviewed["problem_id"] == problem_id
        assert solved["problem_key"] == reviewed["problem_key"]
        assert len(solved["problem_key"]) == 64
        assert solved["discovery_context"]["source_run_id"] == found["id"]
        assert solved["discovery_context"]["files"]
        assert reviewed["discovery_context"] is None
        assert reviewed["candidates"][0]["reviews"][0]["verdict"] == "INCONCLUSIVE"
        assert reviewed["candidates"][0]["level"] != "FORMALLY_VERIFIED"
        assert web.store.load(reviewed["id"]).native.reviewer_session_id != web.store.load(solved["id"]).native.solver_session_id
        assert web.store.load(reviewed["id"]).native.solver_session_id is None
        assert web.store.load(solved["id"]).candidates[0].reviews == []
        detail = client.get(f"/api/runs/{reviewed['id']}")
        assert detail.json()["events"] and detail.json()["report"]["text"]
        download = client.get(f"/api/runs/{reviewed['id']}/report")
        assert download.status_code == 200
        assert "attachment" in download.headers["content-disposition"]
        assert "INCONCLUSIVE" in download.text
        isolated_home = web.store.root / ".mathlottery" / "codex-home"
        calls = [json.loads(line) for line in env_log.read_text().splitlines()]
        assert len([call for call in calls if "exec" in call["args"] and "--help" not in call["args"]]) == 3
        assert all(call["home"] == call["sqlite"] == str(isolated_home) for call in calls)
        assert all(not call["api_key_present"] for call in calls)
        assert len(list((isolated_home / "sessions").glob("*.jsonl"))) == 3
        assert not (isolated_home / "auth.json").exists()
        assert list(personal_home.iterdir()) == [personal_home / "auth.json"]
        assert (personal_home / "auth.json").read_bytes() == sentinel
        assert os.environ["CODEX_HOME"] == str(personal_home)


def test_history_identity_separates_same_titles_and_changed_statements(web):
    problem = Problem(id="sample-problem", title="A shared title", statement="For all n > 0, P(n).")
    run = Orchestrator(web.store).create(web.config(), problem=problem, workflow=Workflow.SOLVE)
    original = web.summary(run)
    run.problem.title = "A more descriptive title"
    run.problem.status = "SOLVED"
    assert web.summary(run)["problem_key"] == original["problem_key"]

    run.problem.title = original["title"]
    run.problem.id = "different-problem"
    assert web.summary(run)["problem_key"] != original["problem_key"]
    run.problem.id = "sample-problem"
    run.problem.statement = "For all n >= 0, P(n)."
    assert web.summary(run)["problem_key"] != original["problem_key"]
    # Grouping metadata is a projection; reading it does not change saved checkpoints.
    assert web.summary(web.store.load(run.id)) == original


def test_http_choose_second_find_problem_rejects_stale_selection(web):
    from mathlottery.models import Phase, State

    engine = Orchestrator(web.store)
    source = engine.create(web.config(), workflow=Workflow.FIND, discovery_request="Prefer elementary proofs")
    source.shortlist = [Problem(id=f"choice-{i}", title=f"Choice {i}", statement=f"Statement {i}",
                                lean_feasibility="Finite sum lemmas") for i in (1, 2)]
    source.problem = source.shortlist[0]
    source.state, source.phase = State.COMPLETED, Phase.REPORT
    web.store.save(source, "fixture_shortlist")
    with serving(web, account_status=SIGNED_IN) as (client, _):
        client.headers["X-MathLottery-Token"] = client.get("/api/bootstrap").json()["csrf_token"]
        found = client.get(f"/api/runs/{source.id}").json()
        assert found["shortlist_count"] == 2 and found["problem_id"] is None
        request = {"workflow": "solve", "problem_id": "choice-2", "from_discovery": source.id,
                   "discovery_problem_sha256": "0" * 64}
        assert client.post("/api/runs", json=request).status_code == 400
        assert len(web.store.list_runs()) == 1
        request["discovery_problem_sha256"] = found["shortlist_bindings"]["choice-2"]
        response = client.post("/api/runs", json=request)
        assert response.status_code == 202, response.text
        solved = finished(web, response.json()["id"])
        assert solved["problem"]["statement"] == "Statement 2"
        assert solved["discovery_run_id"] == source.id
        assert web.store.load(source.id).problem.id == "choice-1"
        assert len(web.store.list_runs()) == 2


@pytest.mark.parametrize("fields", [
    {"workflow": "find", "from_discovery": "run-aaaaaaaaaaaa", "problem_id": "p"},
    {"workflow": "solve", "problem_id": "p", "discovery_problem_sha256": "0" * 64},
    {"workflow": "solve", "problem_id": "p", "from_discovery": "run-aaaaaaaaaaaa"},
])
def test_discovery_selection_requires_explicit_valid_binding(fields):
    with pytest.raises(ValueError):
        StartRequest(**fields)


def test_history_unselected_searches_keep_individual_run_identities(web):
    engine = Orchestrator(web.store)
    searches = [
        engine.create(web.config(), workflow=Workflow.FIND, discovery_request="Small problems")
        for _ in range(2)
    ]
    records = web.bootstrap()["runs"]
    assert {record["id"] for record in records} == {run.id for run in searches}
    assert all(record["problem_id"] is None and record["problem_key"] is None for record in records)


@pytest.mark.parametrize("title", ["A custom problem", None])
def test_http_custom_problem_starts_at_solve_and_keeps_review_in_same_group(web, title):
    statement = "For every positive integer n, determine whether P(n) holds."
    with serving(web, account_status=SIGNED_IN) as (client, _):
        client.headers["X-MathLottery-Token"] = client.get("/api/bootstrap").json()["csrf_token"]
        response = client.post("/api/runs", json={
            "workflow": "solve", "statement": statement, "title": title,
        })
        assert response.status_code == 202, response.text
        solved = finished(web, response.json()["id"])
        expected_title = title or statement[:100]
        assert solved["title"] == expected_title
        assert solved["problem"]["statement"] == statement
        assert solved["problem"]["status"] == "UNKNOWN"
        assert solved["shortlist"] == []
        bootstrap = client.get("/api/bootstrap").json()
        assert [run["workflow"] for run in bootstrap["runs"]] == ["solve"]
        assert bootstrap["problems"][0]["id"] == solved["problem_id"]

        response = client.post("/api/runs", json={"workflow": "verify", "from_run": solved["id"]})
        assert response.status_code == 202, response.text
        reviewed = finished(web, response.json()["id"])
        assert reviewed["problem"] == solved["problem"]
        assert reviewed["problem_key"] == solved["problem_key"]
        records = client.get("/api/bootstrap").json()["runs"]
        assert sorted(run["workflow"] for run in records) == ["solve", "verify"]
        assert {run["title"] for run in records} == {expected_title}
        assert len({run["problem_key"] for run in records}) == 1


def test_http_boundaries_reject_cross_site_mutations_and_file_access(web):
    with serving(web, account_status=SIGNED_IN) as (client, server):
        for asset in ("/", "/app.js", "/style.css", "/mark.svg"):
            response = client.get(asset)
            assert response.status_code == 200
            assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
            assert response.headers["x-content-type-options"] == "nosniff"
        assert client.post("/api/runs", json={"workflow": "find"}).status_code == 403
        headers = {"X-MathLottery-Token": server.csrf_token}
        for extra in ({"Origin": "https://example.com"}, {"Host": "attacker.example"}):
            response = client.post("/api/runs", json={"workflow": "find"}, headers={**headers, **extra})
            assert response.status_code == 403
        assert client.get("/api/bootstrap", headers={"Host": "attacker.example"}).status_code == 403
        for path in ("/config.yaml", "/.mathlottery/state.sqlite3", "/%2e%2e/config.yaml", "/api/runs/../../config.yaml"):
            assert client.get(path).status_code == 404
        assert client.post("/api/runs", content=b"x", headers=headers).status_code == 415
        assert client.post("/api/runs", content=b"{" * 1_000_001, headers={**headers, "Content-Type": "application/json"}).status_code == 413
        assert client.post("/api/runs", json={"workflow": "solve"}, headers=headers).status_code == 400
        assert web.store.list_runs() == []


@pytest.mark.parametrize("payload", [
    {"workflow": "find", "statement": "Unexpected problem"},
    {"workflow": "find", "count": 0},
    {"workflow": "find", "source": "file:///etc/passwd"},
    {"workflow": "find", "source": "https://"},
    {"workflow": "solve", "statement": "   "},
    {"workflow": "solve", "statement": "A", "problem_id": "b"},
    {"workflow": "verify", "statement": "Claim", "proof": " "},
    {"workflow": "verify", "from_run": "../secret"},
    {"workflow": "find", "options": {"budget_minutes": float("inf")}},
    {"workflow": "find", "options": {"api_key": "must not be accepted"}},
    {"workflow": "find", "instructions": "x" * 30001},
])
def test_invalid_browser_inputs_are_rejected(payload):
    with pytest.raises(ValueError):
        StartRequest.model_validate(payload)


def test_pasted_proof_and_candidate_integrity(web):
    created = web.start(StartRequest(workflow="verify", statement="n + 0 = n", proof="By identity."))
    reviewed = finished(web, created["id"])
    assert reviewed["candidates"][0]["claim"] == "n + 0 = n"
    assert reviewed["candidates"][0]["proof"] == "By identity."
    path = web.store.run_dir(created["id"]) / "candidates" / f"{reviewed['candidates'][0]['id']}.json"
    data = json.loads(path.read_text())
    data["assumptions"] = ["Tampered assumption"]
    path.write_text(json.dumps(data))
    count = len(web.store.list_runs())
    with pytest.raises(ValueError, match="modified"):
        web.start(StartRequest(workflow="verify", from_run=created["id"]))
    assert len(web.store.list_runs()) == count


@pytest.mark.parametrize("workflow", ["find", "solve", "verify"])
def test_initial_direction_reaches_first_prompt_without_changing_problem(web, workflow):
    problem = web.store.save_problem(Problem(
        id="fixed-statement", title="An immutable research objective", statement="For every n, n + 0 = n.",
    ))
    before = problem.model_dump()
    instruction = "Provide a complete Lean proof and record the compiler version and axiom check."
    request = {"workflow": workflow, "instructions": f"  {instruction}\n"}
    if workflow == "find":
        request["query"] = "Find a publicly stated problem suitable for formalization."
    else:
        request["problem_id"] = problem.id
        if workflow == "verify":
            request["proof"] = "Apply the right additive identity."
    created = web.start(StartRequest.model_validate(request))
    completed = finished(web, created["id"])
    assert completed["state"] == "COMPLETED"
    run = web.store.load(created["id"])
    first = run.native.history[0]
    prompt = (web.store.run_dir(run.id) / "tasks" / first["task_id"] / "prompt.md").read_text()
    assert "Additional user direction:\n" + instruction in prompt
    assert web.store.load_problem(problem.id).model_dump() == before
    if workflow != "find":
        assert run.problem.model_dump() == before
    if workflow == "verify":
        assert first["role"] == "review"
        assert run.candidates[0].claim == problem.statement
        assert run.candidates[0].proof == request["proof"]


@pytest.mark.parametrize("instructions", [None, "", " \n\t "])
def test_blank_initial_direction_does_not_create_steering(web, monkeypatch, instructions):
    monkeypatch.setattr(web.jobs, "launch", lambda *args, **kwargs: None)
    created = web.start(StartRequest(workflow="find", instructions=instructions))
    assert web.store.load(created["id"]).native.steering is None
    with web.store.connect() as db:
        events = [json.loads(row[0])["event"] for row in db.execute(
            "SELECT data FROM events WHERE run_id=?", (created["id"],),
        )]
    assert "web_initial_direction" not in events


def test_config_overrides_are_temporary_and_resume_preserves_saved_settings(web):
    config_before = (web.store.root / "config.yaml").read_bytes()
    created = web.start(StartRequest(workflow="solve", statement="A precise question", options={
        "model": "override-model", "reasoning_effort": "max", "max_iterations": 1,
    }))
    done = finished(web, created["id"])
    assert done["settings"]["model"] == "override-model"
    assert (web.store.root / "config.yaml").read_bytes() == config_before
    (web.store.root / "config.yaml").write_text("backend:\n  model: changed-default\n")
    web.resume(done["id"], ResumeRequest(message="Check another case", max_iterations=4, budget_minutes=2))
    resumed = finished(web, done["id"])
    assert resumed["settings"]["model"] == "override-model"
    assert resumed["settings"]["max_iterations"] == 4
    assert resumed["settings"]["budget_minutes"] == 2
    assert resumed["iteration"] == 2
    assert len(resumed["candidates"]) == 2
    with pytest.raises(ValueError, match="Add new instructions"):
        web.resume(done["id"], ResumeRequest())


def test_live_worker_survives_server_restart_and_stop_preserves_checkpoint(web, monkeypatch):
    monkeypatch.setenv("MATHLOTTERY_NATIVE_FAKE", "visible_then_slow")
    with serving(web, account_status=SIGNED_IN) as (client, server):
        response = client.post("/api/runs", json={"workflow": "solve", "statement": "A question"}, headers={"X-MathLottery-Token": server.csrf_token})
        assert response.status_code == 202
        run_id = response.json()["id"]
        wait_for(lambda: web.store.load(run_id).native.solver_session_id)
    reopened = WebService(web.store.root)
    assert reopened.jobs.running(run_id)
    with pytest.raises(BusyError):
        reopened.jobs.launch(run_id, "resume", config=reopened.store.load(run_id).config)
    with serving(reopened, account_status=SIGNED_IN) as (client, server):
        headers = {"X-MathLottery-Token": server.csrf_token}
        assert client.get(f"/api/runs/{run_id}").json()["busy"] is True
        assert client.post(f"/api/runs/{run_id}/resume", json={}, headers=headers).status_code == 409
        assert client.post(f"/api/runs/{run_id}/stop", json={}, headers=headers).status_code == 202
        stopped = finished(reopened, run_id)
        assert stopped["state"] == "CANCELLED"
        assert stopped["iteration"] == 1
        assert stopped["candidates"] == []
        assert stopped["report"]["text"]
    monkeypatch.setenv("MATHLOTTERY_NATIVE_FAKE", "three_tasks")
    reopened.resume(run_id, ResumeRequest(message="Continue", max_iterations=5))
    resumed = finished(reopened, run_id)
    assert resumed["state"] == "COMPLETED"
    assert reopened.store.load(run_id).native.solver_session_id is not None


def test_browser_uses_chat_without_provider_or_billing_fallback(web, monkeypatch):
    launched = []
    monkeypatch.setattr(web.jobs, "launch", lambda run_id, action, **kw: launched.append(run_id))
    run = web.start(StartRequest(workflow="find", options={
        "backend": "chat", "reasoning_mode": "pro", "model": "configured-chat-model",
    }))
    saved = web.store.load(run["id"])
    assert saved.mode == "chat"
    assert saved.config["backend"]["chat"]["reasoning_mode"] == "pro"
    assert len(launched) == 1
    with pytest.raises(ValueError, match="only to the chat"):
        web.start(StartRequest(workflow="find", options={"reasoning_mode": "pro"}))


@pytest.mark.parametrize("status,message", [
    ({"available": True, "authenticated": False, "account": None}, "Sign in with ChatGPT"),
    ({"available": True, "authenticated": False, "account": None,
      "login": {"status": "pending"}}, "Complete ChatGPT sign-in"),
    ({"available": False, "authenticated": False, "account": None}, "backend is unavailable"),
    ({"available": True, "authenticated": False, "account": {"type": "apiKey"}}, "Switch account"),
    ({"available": True, "authenticated": True, "account": {"type": "unknown"}}, "Sign in with ChatGPT"),
])
def test_http_auth_preflight_rejects_before_saving_problem_or_run(web, monkeypatch, status, message):
    launched = []
    monkeypatch.setattr(web.jobs, "launch", lambda *args, **kwargs: launched.append(args))
    with serving(web, account_status=status) as (client, server):
        response = client.post("/api/runs", json={
            "workflow": "solve", "statement": "An input that must not be persisted yet",
            "instructions": "Request Lean verification after sign-in.",
        }, headers={"X-MathLottery-Token": server.csrf_token})
    assert response.status_code == 400
    assert message in response.json()["error"]
    assert web.store.list_runs() == []
    assert web.store.list_problems() == []
    assert launched == []


@pytest.mark.parametrize("mode", ["codex", "work"])
def test_http_resume_checks_saved_backend_before_launch(web, monkeypatch, mode):
    config = web.config()
    config.backend.mode = mode
    run = Orchestrator(web.store).create(config, workflow=Workflow.FIND)
    saved = web.store.load(run.id).model_dump()
    config.backend.mode = "chat"
    (web.store.root / "config.yaml").write_text(yaml.safe_dump(config.model_dump(mode="json")))
    launched = []
    monkeypatch.setattr(web.jobs, "launch", lambda *args, **kwargs: launched.append(args))
    with serving(web, account_status={
        "available": True, "authenticated": False, "account": None,
    }) as (client, server):
        response = client.post(f"/api/runs/{run.id}/resume", json={
            "message": "Continue this saved task", "budget_minutes": 2,
        }, headers={"X-MathLottery-Token": server.csrf_token})
    assert response.status_code == 400
    assert "Sign in with ChatGPT" in response.json()["error"]
    assert web.store.load(run.id).model_dump() == saved
    assert launched == []


def test_http_chat_start_and_resume_do_not_require_codex_account(web, monkeypatch):
    launched = []
    monkeypatch.setattr(web.jobs, "launch", lambda *args, **kwargs: launched.append((args, kwargs)))
    with serving(web) as (client, server):
        def no_account_access():
            raise AssertionError("Chat tasks must not inspect the Codex login")

        monkeypatch.setattr(server.account, "status", no_account_access)
        headers = {"X-MathLottery-Token": server.csrf_token}
        response = client.post("/api/runs", json={
            "workflow": "find", "options": {"backend": "chat"},
        }, headers=headers)
        assert response.status_code == 202, response.text
        run_id = response.json()["id"]
        resumed = client.post(f"/api/runs/{run_id}/resume", json={}, headers=headers)
        assert resumed.status_code == 202, resumed.text
    assert web.store.load(run_id).mode == "chat"
    assert len(launched) == 2


def test_http_start_override_and_fresh_status_control_preflight(web, monkeypatch):
    config = web.config()
    config.backend.mode = "chat"
    (web.store.root / "config.yaml").write_text(yaml.safe_dump(config.model_dump(mode="json")))
    launched = []
    monkeypatch.setattr(web.jobs, "launch", lambda *args, **kwargs: launched.append(args))
    status = dict(SIGNED_IN)
    with serving(web, account_status=status) as (client, server):
        headers = {"X-MathLottery-Token": server.csrf_token}
        body = {"workflow": "find", "options": {"backend": "codex"}}
        first = client.post("/api/runs", json=body, headers=headers)
        assert first.status_code == 202, first.text
        status.update(authenticated=False, account=None)
        second = client.post("/api/runs", json=body, headers=headers)
        assert second.status_code == 400
        assert "Sign in with ChatGPT" in second.json()["error"]
    assert len(web.store.list_runs()) == len(launched) == 1
    assert web.store.load(first.json()["id"]).mode == "codex"


def test_bounded_progress_and_path_escape(web, tmp_path):
    run = Orchestrator(web.store).create(web.config(), Problem(id="test", title="Test", statement="Claim"), workflow=Workflow.VERIFY, candidate=CandidateInput(claim="Claim", proof="Proof"))
    target = web.store.run_dir(run.id) / "report.md"
    target.write_text("a" * 200)
    assert web.text_artifact(run.id, "report.md", limit=100) == {"text": "a" * 100, "truncated": True}
    target.unlink()
    target.symlink_to(tmp_path / "config.yaml")
    with pytest.raises(ValueError, match="inside"):
        web.detail(run.id)


def test_serve_cli_passes_workspace_and_port(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr("mathlottery.web.server.serve", lambda *args: calls.append(args))
    result = CliRunner().invoke(app, ["--root", str(tmp_path), "serve", "--port", "9001", "--open"])
    assert result.exit_code == 0, result.output
    assert calls == [(tmp_path, None, 9001, True, False, False)]
