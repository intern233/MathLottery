import json

from conftest import response

from mathlottery.demo import DemoBackend, demo_problem
from mathlottery.models import Phase, State
from mathlottery.orchestrator import Orchestrator
from mathlottery.sources import WebTools


def test_crash_during_report_generation_resumes_without_model_call(store, config, monkeypatch):
    engine = Orchestrator(store, DemoBackend())
    run = engine.create(config, demo_problem(), mode="demo")
    original = store.save
    interrupted = []

    def fail_after_reporting_checkpoint(run, event, **kwargs):
        original(run, event, **kwargs)
        if event == "reporting" and not interrupted:
            interrupted.append(True)
            raise KeyboardInterrupt

    monkeypatch.setattr(store, "save", fail_after_reporting_checkpoint)
    run = engine.drive(run.id)
    assert run.state == State.PAUSED
    assert run.phase == Phase.REPORT
    rounds = run.iteration
    resumed = engine.resume(run.id)
    assert resumed.state == State.COMPLETED
    assert resumed.iteration == rounds


def test_reasoning_summary_survives_without_explicit_memory(waiting):
    engine, run = waiting
    run = engine.submit(
        run.id, response(run, action="SELECT_PROBLEM", problem=run.problem.model_dump(mode="json"))
    )
    run = engine.submit(run.id, response(run, summary="Use induction; the n=0 boundary matters."))
    assert any("n=0 boundary" in item.content for item in run.memory)


def test_arxiv_api_uses_documented_endpoint_and_retains_evidence(tmp_path, monkeypatch):
    calls = []

    def fetch(self, url, *, check_robots=True):
        calls.append((url, check_robots))
        return (
            '<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>https://arxiv.org/abs/1</id><title>Paper</title></entry></feed>',
            url,
        )

    monkeypatch.setattr(WebTools, "_request", fetch)
    from mathlottery.config import ToolConfig

    result = WebTools(tmp_path, ToolConfig()).search('"additive combinatorics"', 2)
    assert calls[0][0].startswith("https://export.arxiv.org/api/query?")
    assert calls[0][1] is False  # API policy; ordinary web_fetch retains robots checks.
    assert result["results"][0]["artifact"]
    assert result["results"][0]["sha256"]
    assert (tmp_path / result["artifact"]).exists()


def test_manual_example_has_valid_nested_tool_json():
    from pathlib import Path

    data = json.loads(
        (Path(__file__).parents[1] / "examples/chat_response.template.json").read_text()
    )
    code = json.loads(data["tools"][0]["arguments_json"])["code"]
    compile(code, "example", "exec")


def test_legacy_inconclusive_review_continues_research(store, config):
    engine = Orchestrator(store)
    run = engine.drive(
        engine.create(config, demo_problem(), proof="A proof with a missing step").id
    )
    run = engine.submit(
        run.id,
        response(
            run,
            action="REVIEW",
            review={
                "verdict": "INCONCLUSIVE",
                "truth_assessment": "Not established",
                "proof_assessment": "Needs a lemma",
                "issues": ["Missing lemma"],
            },
        ),
    )
    assert run.state == State.WAITING_FOR_USER and run.phase == Phase.SOLVE
    assert run.candidates[-1].reviews[-1].verdict == "INCONCLUSIVE"
