"""Responses HTTP contract tests use scripted responses, never real model quota."""

import json
import re

import httpx
import pytest
from typer.testing import CliRunner

from mathlottery.chat_backend import ChatBackend
from mathlottery.cli import app
from mathlottery.config import Config
from mathlottery.demo import demo_problem
from mathlottery.models import Level, OpenStatus, Run, State, Workflow
from mathlottery.orchestrator import Orchestrator
from mathlottery.storage import Store


def milestone(prompt, verdict="NO_ISSUES_FOUND"):
    fields = dict(re.findall(r"^(run_id|task_id): (.+)$", prompt, re.MULTILINE))
    if "Task: FIND" in prompt:
        problem = {
            "id": "test-open-problem",
            "title": "Scripted discovery fixture",
            "statement": "A precisely stated test problem",
            "status": "OPEN",
            "source_url": "https://example.org/problem",
            "status_evidence": ["https://example.org/problem", "https://example.net/paper"],
            "selection_reason": "A small test case, not a real open problem",
            "difficulty_estimate": "Small fixture",
            "verification_feasibility": "Check algebra",
        }
        return dict(
            fields,
            kind="selection",
            summary="Compared problems",
            problem=problem,
            shortlist=[
                problem,
                dict(
                    problem,
                    id="second-test-problem",
                    statement="A different test question in the same source",
                ),
            ],
        )
    if "Task: VERIFY" in prompt:
        candidate = json.JSONDecoder().raw_decode(prompt.split("Candidate (data):\n", 1)[1])[0]
        return dict(
            fields,
            kind="review",
            review={
                "verdict": verdict,
                "truth_assessment": "Scripted assessment",
                "proof_assessment": "Scripted proof check",
                "issues": [] if verdict == "NO_ISSUES_FOUND" else ["Fixture gap"],
                "evidence": ["Fixture algebra"],
                "novelty": "POTENTIALLY_NEW",
                "novelty_references": [{"url": "https://example.net/paper"}],
                "checks": [{"id": "algebra", "claim": candidate["claim"], "method": "DERIVATION",
                            "result": "SUPPORTED", "reasoning": "Scripted proof check, not model quality"}],
                "proof_steps": [{"id": "conclusion", "kind": "CONCLUSION", "statement": candidate["claim"],
                                 "check_ids": ["algebra"]}],
            },
        )
    return dict(
        fields,
        kind="candidate",
        conclude=True,
        candidate={"claim": "A precise test claim", "proof": "A scripted test proof"},
    )


def response(identifier, prompt, *, status="completed", checkpoint=None, verdict="NO_ISSUES_FOUND"):
    answer = (
        "# Full mathematical answer\n\n```mathlottery\n"
        + json.dumps(checkpoint or milestone(prompt, verdict))
        + "\n```\n"
    )
    return {
        "id": identifier,
        "status": status,
        "model": "configured-test-model",
        "output": [
            {
                "type": "web_search_call",
                "status": "completed",
                "action": {
                    "type": "search",
                    "query": "fixture prior theorem erratum",
                    "sources": [
                        {"url": "https://example.org/problem"},
                        {"url": "https://example.net/paper"},
                    ],
                },
            },
            {"type": "code_interpreter_call", "code": "print(1 + 1)"},
            {
                "type": "message",
                "role": "assistant",
                "content": [
                    {"type": "output_text", "text": answer},
                ],
            },
        ]
        if status == "completed"
        else [],
        "usage": {
            "input_tokens": 20,
            "output_tokens": 10,
            "input_tokens_details": {"cached_tokens": 3},
        }
        if status == "completed"
        else None,
    }


@pytest.fixture
def chat_config(monkeypatch):
    monkeypatch.setenv("MATHLOTTERY_TEST_KEY", "test-secret-never-persist")
    config = Config()
    config.backend.mode = "chat"
    config.backend.model = "configured-test-model"
    config.backend.chat.api_key_env = "MATHLOTTERY_TEST_KEY"
    config.backend.chat.poll_interval_seconds = 0.001
    config.budget.max_iterations = 8
    return config


@pytest.fixture
def api(monkeypatch):
    requests = []

    def install(handler=None):
        def serve(request):
            requests.append(request)
            if handler:
                return handler(request)
            data = json.loads(request.content)
            return httpx.Response(200, json=response(f"resp_test_{len(requests)}", data["input"]))

        monkeypatch.setattr(
            ChatBackend,
            "_client",
            lambda self: httpx.Client(
                base_url=self.config.chat.base_url + "/",
                headers={"Authorization": "Bearer test-secret-never-persist"},
                transport=httpx.MockTransport(serve),
            ),
        )
        return requests

    return install


@pytest.mark.parametrize("workflow", [Workflow.FIND, Workflow.SOLVE, Workflow.VERIFY])
def test_three_tasks_use_automatic_chat_api(store, chat_config, api, workflow):
    requests = api()
    engine = Orchestrator(store)
    kwargs = {"workflow": workflow}
    if workflow != Workflow.FIND:
        kwargs["problem"] = demo_problem()
    if workflow == Workflow.VERIFY:
        kwargs["proof"] = "Check this proof independently"
    run = engine.drive(engine.create(chat_config, **kwargs).id)
    assert run.state == State.COMPLETED and run.iteration == 1
    assert len(requests) == 1 and requests[0].method == "POST"
    payload = json.loads(requests[0].content)
    assert payload["background"] and payload["store"]
    assert {tool["type"] for tool in payload["tools"]} == {"web_search", "code_interpreter"}
    assert "max_tool_calls" not in payload and "max_output_tokens" not in payload
    assert run.usage.input_tokens == 20 and run.usage.unknown_calls == 0
    assert run.native.history[0]["runtime"]["tools_observed"] == [
        "code_interpreter_call",
        "web_search_call",
    ]
    if workflow == Workflow.FIND:
        assert len(run.shortlist) == 2 and not run.candidates
        assert run.problem.status == OpenStatus.UNKNOWN
        assert run.problem.evidence_assessment.observed_queries == ["fixture prior theorem erratum"]
        assert store.load_problem(run.shortlist[1].id).selection_reason
        assert (store.run_dir(run.id) / "literature/selection.json").exists()
    elif workflow == Workflow.SOLVE:
        assert run.candidates[0].level == Level.CANDIDATE
        assert not run.candidates[0].reviews and run.native.reviewer_response_id is None
    else:
        assert run.native.solver_response_id is None
        assert run.native.reviewer_response_id
        assert run.candidates[0].level == Level.SELF_CHECKED
    for path in store.run_dir(run.id).rglob("*"):
        if path.is_file():
            assert b"test-secret-never-persist" not in path.read_bytes()


def test_pipeline_chains_research_but_starts_fresh_review(store, chat_config, api):
    requests = api()
    run = Orchestrator(store).create(chat_config)
    run = Orchestrator(store).drive(run.id)
    assert run.state == State.COMPLETED and run.iteration == 3
    payloads = [json.loads(r.content) for r in requests]
    assert "previous_response_id" not in payloads[0]
    assert payloads[1]["previous_response_id"] == "resp_test_1"
    assert "previous_response_id" not in payloads[2]
    assert run.native.solver_response_id == "resp_test_2"
    assert run.native.reviewer_response_id == "resp_test_3"
    assert run.candidates[0].reviews[0].novelty == "UNKNOWN"
    assert run.candidates[0].reviews[0].reported_novelty == "POTENTIALLY_NEW"


def test_pipeline_does_not_finish_on_a_positive_verdict_without_checks(store, chat_config, api):
    chat_config.budget.max_iterations = 3

    def serve(request):
        prompt = json.loads(request.content)["input"]
        checkpoint = milestone(prompt)
        if checkpoint["kind"] == "review":
            checkpoint["review"]["checks"] = []
        return httpx.Response(200, json=response("resp_test", prompt, checkpoint=checkpoint))

    api(serve)
    run = Orchestrator(store).create(chat_config)
    run = Orchestrator(store).drive(run.id)
    assert run.state == State.PAUSED
    assert run.phase == "SOLVE"
    assert run.candidates[-1].reviews[-1].verdict == "INCONCLUSIVE"


@pytest.mark.parametrize(
    "effort,mode,expected",
    [
        (None, None, {}),
        ("max", None, {"effort": "max"}),
        (None, "pro", {"mode": "pro"}),
        ("max", "pro", {"effort": "max", "mode": "pro"}),
        ("max", "standard", {"effort": "max", "mode": "standard"}),
    ],
)
def test_chat_reasoning_controls_are_independent(store, chat_config, api, effort, mode, expected):
    chat_config.backend.model = "gpt-6-astra"
    chat_config.backend.reasoning_effort = effort
    chat_config.backend.chat.reasoning_mode = mode
    observed = {"effort": effort or "medium", "mode": mode or "standard"}

    def serve(request):
        payload = json.loads(request.content)
        value = response("resp_reasoning", payload["input"])
        value.update(model="gpt-6-astra", reasoning=observed)
        return httpx.Response(200, json=value)

    requests = api(serve)
    engine = Orchestrator(store)
    run = engine.drive(engine.create(chat_config, demo_problem(), workflow=Workflow.SOLVE).id)
    assert run.state == State.COMPLETED and len(requests) == 1
    payload = json.loads(requests[0].content)
    assert payload["model"] == "gpt-6-astra"
    assert payload.get("reasoning", {}) == expected
    if not expected:
        assert "reasoning" not in payload
    assert {tool["type"] for tool in payload["tools"]} == {"web_search", "code_interpreter"}
    runtime = run.native.history[0]["runtime"]
    assert runtime["reasoning_effort"] == observed["effort"]
    assert runtime["reasoning_mode"] == observed["mode"]
    persisted = store.load(run.id)
    assert persisted.config["backend"]["chat"]["reasoning_mode"] == mode
    assert persisted.config["backend"]["reasoning_effort"] == effort


def test_requested_pro_does_not_fabricate_observed_mode(store, chat_config, api):
    chat_config.backend.chat.reasoning_mode = "pro"
    api()  # This fixture does not report effective reasoning settings.
    engine = Orchestrator(store)
    run = engine.drive(engine.create(chat_config, demo_problem(), workflow=Workflow.SOLVE).id)
    assert run.native.history[0]["runtime"]["reasoning_mode"] is None
    report = (store.run_dir(run.id) / "report.md").read_text()
    assert "Requested Chat reasoning mode: `pro`" in report
    assert '"reasoning_mode": null' in report


@pytest.mark.parametrize("verdict", ["ISSUES_FOUND", "INCONCLUSIVE"])
def test_standalone_verify_finishes_for_every_verdict(store, chat_config, api, verdict):
    requests = api(
        lambda req: httpx.Response(
            200, json=response("resp_audit", json.loads(req.content)["input"], verdict=verdict)
        )
    )
    engine = Orchestrator(store)
    run = engine.drive(
        engine.create(
            chat_config, demo_problem(), proof="A dubious proof", workflow=Workflow.VERIFY
        ).id
    )
    assert run.state == State.COMPLETED and len(requests) == 1
    assert run.candidates[0].reviews[0].verdict == verdict
    assert run.native.solver_response_id is None


def test_chat_token_budget_uses_reported_values(store, chat_config, api):
    def serve(request):
        prompt = json.loads(request.content)["input"]
        checkpoint = milestone(prompt)
        checkpoint = {
            "run_id": checkpoint["run_id"],
            "task_id": checkpoint["task_id"],
            "kind": "progress",
        }
        return httpx.Response(200, json=response("resp_progress", prompt, checkpoint=checkpoint))

    requests = api(serve)
    chat_config.budget.max_input_tokens = 15
    run = Orchestrator(store).create(chat_config, demo_problem(), workflow=Workflow.SOLVE)
    run = Orchestrator(store).drive(run.id)
    assert run.state == State.PAUSED and len(requests) == 1
    assert run.usage.input_tokens == 20 and "Measured input_tokens" in run.stop_reason


@pytest.mark.parametrize("status", [400, 401, 429])
def test_api_errors_are_not_retried_or_switched(store, chat_config, api, status):
    requests = api(lambda req: httpx.Response(status, json={"error": "test-secret-never-persist"}))
    run = Orchestrator(store).create(chat_config, demo_problem())
    run = Orchestrator(store).drive(run.id)
    assert run.state in {State.FAILED, State.RATE_LIMITED} and len(requests) == 1
    assert run.mode == "chat" and str(status) in run.last_error
    assert "test-secret-never-persist" not in run.last_error


def test_pending_response_recovers_without_duplicate_creation(store, chat_config, api):
    saved = {}
    failure = [True]

    def serve(request):
        if request.method == "POST":
            saved["prompt"] = json.loads(request.content)["input"]
            return httpx.Response(
                200, json=response("resp_recover", saved["prompt"], status="queued")
            )
        if failure[0]:
            failure[0] = False
            raise httpx.ReadError("connection lost")
        return httpx.Response(200, json=response("resp_recover", saved["prompt"]))

    requests = api(serve)
    engine = Orchestrator(store)
    run = engine.drive(engine.create(chat_config, demo_problem(), workflow=Workflow.SOLVE).id)
    assert run.state == State.FAILED and run.native.active_attempt
    assert run.iteration == 0 and run.usage.input_tokens is None
    run = engine.resume(run.id)
    assert run.state == State.COMPLETED and run.iteration == 1
    assert run.usage.input_tokens == 20
    assert [r.method for r in requests] == ["POST", "GET", "GET"]


def test_ctrl_c_cancels_remote_work(store, chat_config, api):
    saved = {}

    def serve(request):
        if request.url.path.endswith("/cancel"):
            return httpx.Response(
                200, json=response("resp_cancel", saved["prompt"], status="cancelled")
            )
        if request.method == "GET":
            raise KeyboardInterrupt
        saved["prompt"] = json.loads(request.content)["input"]
        return httpx.Response(200, json=response("resp_cancel", saved["prompt"], status="queued"))

    requests = api(serve)
    run = Orchestrator(store).create(chat_config, demo_problem())
    run = Orchestrator(store).drive(run.id)
    assert run.state == State.PAUSED and not run.native.active_attempt
    assert requests[-1].url.path.endswith("/cancel")


def test_missing_key_and_zero_cost_limit_fail_without_network(store, chat_config, monkeypatch):
    monkeypatch.delenv("MATHLOTTERY_TEST_KEY")
    engine = Orchestrator(store)
    run = engine.drive(engine.create(chat_config, demo_problem()).id)
    assert run.state == State.FAILED and run.iteration == 0
    assert "MATHLOTTERY_TEST_KEY" in run.last_error
    chat_config.budget.max_external_cost_usd = 0
    with pytest.raises(ValueError, match="forbids"):
        engine.create(chat_config, demo_problem())


def test_old_manual_checkpoint_does_not_become_paid_chat():
    old = {
        "id": "run-123456789012",
        "mode": "chat",
        "execution": "native",
        "config": {"backend": {"mode": "chat"}},
    }
    restored = Run.model_validate(old)
    assert restored.mode == restored.config["backend"]["mode"] == "manual"


def test_stop_cancels_a_detached_background_request(store, chat_config, api):
    saved = {}

    def serve(request):
        if request.url.path.endswith("/cancel"):
            return httpx.Response(
                200, json=response("resp_detached", saved["prompt"], status="cancelled")
            )
        if request.method == "GET":
            raise httpx.ReadError("Connection lost while the server is still running")
        saved["prompt"] = json.loads(request.content)["input"]
        return httpx.Response(200, json=response("resp_detached", saved["prompt"], status="queued"))

    requests = api(serve)
    engine = Orchestrator(store)
    run = engine.drive(engine.create(chat_config, demo_problem()).id)
    assert run.native.active_attempt
    run = engine.stop(run.id)
    assert run.state == State.CANCELLED and not run.native.active_attempt
    assert requests[-1].url.path.endswith("/cancel")


def test_cli_three_tasks_and_candidate_verification(tmp_path, chat_config, api):
    import yaml

    api()
    (tmp_path / "config.yaml").write_text(yaml.safe_dump(chat_config.model_dump(mode="json")))
    cli = CliRunner()
    prefix = ["--root", str(tmp_path)]
    result = cli.invoke(
        app, prefix + ["find", "--backend", "chat", "--query", "small test problems"]
    )
    assert result.exit_code == 0, result.output
    assert "WAITING_FOR_USER" not in result.output and "Selection:" in result.output
    result = cli.invoke(
        app, prefix + ["solve", "--backend", "chat", "--problem", "test-open-problem"]
    )
    assert result.exit_code == 0, result.output
    store = Store(tmp_path)
    solved = next(run for run in store.list_runs() if run.workflow == Workflow.SOLVE)
    result = cli.invoke(app, prefix + ["verify", "--backend", "chat", "--from-run", solved.id])
    assert result.exit_code == 0, result.output
    audited = next(run for run in store.list_runs() if run.workflow == Workflow.VERIFY)
    assert audited.candidates[0].claim == solved.candidates[0].claim
    assert audited.native.solver_response_id is None
    path = store.run_dir(solved.id) / "candidates" / f"{solved.candidates[0].id}.json"
    result = cli.invoke(app, prefix + ["verify", "--candidate", str(path)])
    assert result.exit_code == 0, result.output


@pytest.mark.parametrize("command", ["find", "solve", "verify", "run", "resume"])
def test_cli_model_and_pro_settings_reach_every_chat_workflow(
    tmp_path, chat_config, api, command
):
    import yaml

    chat_config.backend.reasoning_effort = "low"
    chat_config.backend.chat.reasoning_mode = "standard"
    (tmp_path / "config.yaml").write_text(yaml.safe_dump(chat_config.model_dump(mode="json")))
    requests = api()
    store = Store(tmp_path)
    args = [command]
    if command in {"solve", "run"}:
        args += ["--prompt", "Check a test claim"]
    elif command == "verify":
        path = tmp_path / "candidate.json"
        path.write_text(json.dumps({"claim": "Test claim", "proof": "Test proof"}))
        args += ["--candidate", str(path)]
    elif command == "resume":
        engine = Orchestrator(store)
        run = engine.drive(engine.create(chat_config, demo_problem(), workflow=Workflow.SOLVE).id)
        args += [run.id, "--message", "Check the boundary cases"]
    initial_calls = len(requests)
    result = CliRunner().invoke(
        app,
        ["--root", str(tmp_path)]
        + args
        + [
            "--backend", "chat", "--model", "gpt-6-astra",
            "--reasoning-effort", "max", "--reasoning-mode", "pro",
        ],
    )
    assert result.exit_code == 0, result.output
    assert len(requests) > initial_calls
    for request in requests[initial_calls:]:
        payload = json.loads(request.content)
        assert payload["model"] == "gpt-6-astra"
        assert payload["reasoning"] == {"effort": "max", "mode": "pro"}
    saved = store.list_runs()[0]
    assert saved.config["backend"]["model"] == "gpt-6-astra"
    assert saved.config["backend"]["chat"]["reasoning_mode"] == "pro"
    if command == "resume":
        payload = json.loads(requests[initial_calls].content)
        assert payload["previous_response_id"] == run.native.solver_response_id


def test_cli_does_not_silently_ignore_chat_reasoning_mode_for_codex(tmp_path, api):
    requests = api()
    result = CliRunner().invoke(
        app,
        [
            "--root", str(tmp_path), "solve", "--backend", "codex",
            "--prompt", "Test problem", "--reasoning-mode", "pro",
        ],
    )
    assert result.exit_code == 2
    assert "--reasoning-mode requires --backend chat" in result.output
    assert not requests and not Store(tmp_path).list_runs()


def test_rediscovery_retains_the_existing_problem_id(store, chat_config, api):
    engine = Orchestrator(store)
    api()
    first = engine.drive(engine.create(chat_config, workflow=Workflow.FIND).id)

    def rediscover(request):
        prompt = json.loads(request.content)["input"]
        selected = milestone(prompt)
        selected["problem"]["id"] = "another-agent-name-for-the-same-problem"
        return httpx.Response(200, json=response("resp_rediscovery", prompt, checkpoint=selected))

    api(rediscover)
    second = engine.drive(engine.create(chat_config, workflow=Workflow.FIND).id)
    assert second.state == State.COMPLETED
    assert second.problem.id == first.problem.id
    assert len(store.list_problems()) == 2
    assert len({problem.id for problem in second.shortlist}) == 2


def test_unobserved_sources_do_not_certify_open_status(store, chat_config, api):
    def serve(request):
        value = response("resp_no_sources", json.loads(request.content)["input"])
        value["output"] = [item for item in value["output"] if item["type"] == "message"]
        return httpx.Response(200, json=value)

    api(serve)
    engine = Orchestrator(store)
    run = engine.drive(engine.create(chat_config, workflow=Workflow.FIND).id)
    assert run.state == State.COMPLETED and run.problem.status == OpenStatus.UNKNOWN
    record = json.loads((store.run_dir(run.id) / "literature/selection.json").read_text())
    assert record["agent_assessment"]["problem"]["status"] == "OPEN"


def test_legacy_problem_database_migration_preserves_rows(tmp_path):
    import sqlite3

    from mathlottery.models import Problem

    internal = tmp_path / ".mathlottery"
    internal.mkdir()
    original = Problem(
        id="first",
        title="First question",
        statement="First statement",
        source_url="https://example.org/paper",
    )
    with sqlite3.connect(internal / "state.sqlite3") as db:
        db.execute(
            "CREATE TABLE problems (id TEXT PRIMARY KEY, source_url TEXT UNIQUE, data TEXT NOT NULL)"
        )
        db.execute(
            "INSERT INTO problems VALUES (?, ?, ?)",
            (original.id, original.source_url, original.model_dump_json()),
        )
    store = Store(tmp_path)
    assert store.load_problem(original.id) == original
    second = original.model_copy(update={"id": "second", "statement": "A different question"})
    assert store.save_problem(second).id == "second"
    reopened = Store(tmp_path)
    assert reopened.load_problem("first") == original
    assert reopened.load_problem("second") == second
