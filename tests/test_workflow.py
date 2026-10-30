import json

import pytest
from conftest import response
from typer.testing import CliRunner

from mathlottery.cli import app
from mathlottery.config import Config
from mathlottery.models import CandidateInput, Level, Review, State
from mathlottery.providers.demo import DemoBackend, demo_problem
from mathlottery.runtime.orchestrator import Orchestrator
from mathlottery.runtime.structured_prompts import build_prompt
from mathlottery.storage.core import Store
from mathlottery.verify.auditor import audit


@pytest.mark.parametrize(
    "case,level",
    [
        ("correct", Level.SELF_CHECKED),
        ("incorrect", Level.REJECTED),
        ("hidden-assumption", Level.REJECTED),
        ("finite-only", Level.REJECTED),
    ],
)
def test_offline_demo_has_real_calculations_and_honest_verification(tmp_path, case, level):
    result = CliRunner().invoke(app, ["--root", str(tmp_path), "demo", "--case", case])
    assert result.exit_code == 0, result.output
    store = Store(tmp_path)
    run = store.list_runs()[0]
    assert run.state == State.COMPLETED
    assert run.candidates[-1].level == level
    assert run.usage.input_tokens is None
    experiments = [o for o in run.observations if o["tool"] == "python_exec"]
    assert len(experiments) == 2
    assert all(o["result"]["status"] == "OK" for o in experiments)
    assert all(o["result"]["stdout"] for o in experiments)
    assert (store.run_dir(run.id) / "report.md").exists()
    assert run.candidates[-1].reviews[-1].novelty == "UNKNOWN"


def test_chat_full_handoff_and_unknown_usage(waiting, store):
    engine, run = waiting
    demo = DemoBackend()
    for _ in range(8):
        if run.state == State.COMPLETED:
            break
        assert run.state == State.WAITING_FOR_USER
        prompt = (store.run_dir(run.id) / run.prompt_path).read_text()
        answer = demo.invoke(prompt, {}, store.root, 1).text
        run = engine.submit(run.id, answer)
    assert run.state == State.COMPLETED
    assert run.iteration == 5
    assert run.usage.unknown_calls == 5
    assert run.usage.input_tokens is None
    assert run.candidates[0].level == Level.SELF_CHECKED


@pytest.mark.parametrize("text", ["not JSON", "{}", "[]", '{"unexpected":1}'])
def test_invalid_chat_json_does_not_change_state(waiting, store, text):
    engine, run = waiting
    before = store.load(run.id).model_dump()
    with pytest.raises(ValueError):
        engine.submit(run.id, text)
    assert store.load(run.id).model_dump() == before


def test_stale_response_and_changed_statement_are_rejected(waiting):
    engine, run = waiting
    with pytest.raises(ValueError, match="Stale"):
        engine.submit(run.id, response(run, task_id="other"))
    other = run.problem.model_dump(mode="json")
    other["statement"] = "1=2"
    with pytest.raises(ValueError, match="must not be changed"):
        engine.submit(run.id, response(run, action="SELECT_PROBLEM", problem=other))


def test_agent_cannot_promote_lemma_or_set_formal_target(waiting):
    engine, run = waiting
    selected = run.problem.model_dump(mode="json")
    selected["formal_target"] = "True"
    run = engine.submit(
        run.id,
        response(
            run,
            action="SELECT_PROBLEM",
            problem=selected,
            memory=[{"kind": "lemma", "content": "Unsupported fact", "status": "verified"}],
        ),
    )
    assert run.problem.formal_target is None
    assert run.memory[-1].status == "unverified"


def test_structured_reselection_cannot_omit_saved_source_obligations(waiting, store):
    from mathlottery.models import LiteratureObstacle

    engine, run = waiting
    old = run.problem.model_copy(deep=True)
    old.literature_search.obstacles = [LiteratureObstacle(
        id="prior-theorem", kind="UNCLEAR_COMPARISON", description="Compare the closest known theorem",
        impact="It could already imply the claim", next_action="Read both hypotheses and conclusions",
        source_url="https://example.test/paper",
    )]
    old.evidence_assessment.policy_version = "evidence-v4"
    old.evidence_assessment.obstacles = [{"id": "prior-theorem", "resolution_supported": False}]
    store.save_problem(old)
    selected = run.problem.model_dump(mode="json")
    run = engine.submit(run.id, response(run, action="SELECT_PROBLEM", problem=selected))
    assert "prior-theorem" in run.problem.evidence_assessment.unresolved_obstacle_ids
    assert run.problem.evidence_assessment.obstacles[0]["previous_status"] == "OPEN"
    assert run.shortlist[0].literature_search.obstacles[0].id == "prior-theorem"


def test_independent_review_excludes_solver_memory_and_previous_candidate_reviews(store, config):
    engine = Orchestrator(store)
    run = engine.create(config, demo_problem(), proof="Induction on n.")
    from mathlottery.models import MemoryItem

    run.memory.append(MemoryItem(kind="strategy", content="SECRET_SOLVER_SUCCESS_CLAIM"))
    run.observations.append(
        {
            "phase": "VERIFY",
            "iteration": 0,
            "tool": "python_exec",
            "result": {"stdout": "OLD_CANDIDATE_CONTEXT"},
        }
    )
    prompt = build_prompt(run, config)
    assert "SECRET_SOLVER_SUCCESS_CLAIM" not in prompt
    assert "OLD_CANDIDATE_CONTEXT" not in prompt
    assert "Induction on n." in prompt


def test_candidate_artifact_tampering_blocks_review(store, config):
    engine = Orchestrator(store)
    run = engine.create(config, demo_problem(), proof="Original proof")
    path = store.run_dir(run.id) / "candidates" / f"{run.candidates[0].id}.json"
    data = json.loads(path.read_text())
    data["proof"] = "Changed proof"
    path.write_text(json.dumps(data))
    run = engine.drive(run.id)
    assert run.state == State.FAILED
    assert "modified" in run.last_error


def test_crash_after_tool_output_reuses_saved_result(waiting, store, monkeypatch):
    engine, run = waiting
    from mathlottery.tooling.registry import ToolRegistry

    original = ToolRegistry.execute
    executions = []

    def crash_after_result(self, call, run, number):
        result = original(self, call, run, number)
        executions.append(result)
        raise KeyboardInterrupt

    monkeypatch.setattr(ToolRegistry, "execute", crash_after_result)
    run = engine.submit(
        run.id,
        response(
            run,
            tools=[
                {
                    "name": "write_artifact",
                    "arguments_json": json.dumps({"path": "note.txt", "content": "persisted"}),
                }
            ],
        ),
    )
    assert run.state == State.PAUSED
    assert run.pending_response
    monkeypatch.setattr(ToolRegistry, "execute", original)
    resumed = engine.resume(run.id)
    assert resumed.state == State.WAITING_FOR_USER
    assert resumed.iteration == 1
    assert len(resumed.observations) == 1
    assert len(executions) == 1
    assert resumed.pending_response is None


def test_sqlite_is_authoritative_after_projection_loss(waiting, store):
    _, run = waiting
    (store.run_dir(run.id) / "metadata.json").write_text("broken projection")
    loaded = store.load(run.id)
    assert loaded.task_id == run.task_id
    store.project(loaded)
    assert json.loads((store.run_dir(run.id) / "metadata.json").read_text())["id"] == run.id


def test_iteration_budget_and_resume_preserve_history(store, config):
    config.budget.max_iterations = 2
    engine = Orchestrator(store, DemoBackend())
    run = engine.create(config, demo_problem(), mode="demo")
    run = engine.drive(run.id)
    assert run.state == State.PAUSED
    assert run.iteration == 2
    count = len(run.observations)
    config.budget.max_iterations = 10
    resumed = engine.resume(run.id, config=config)
    assert resumed.state == State.COMPLETED
    assert resumed.iteration == 5
    assert len(resumed.observations) > count


def test_chat_token_budget_is_not_faked(store, config):
    config.budget.max_input_tokens = 100
    engine = Orchestrator(store)
    run = engine.drive(engine.create(config, demo_problem()).id)
    assert run.state == State.PAUSED
    assert "unknown" in run.stop_reason
    assert run.iteration == 0


def test_stop_then_explicit_resume(waiting, store):
    engine, run = waiting
    stopped = engine.stop(run.id)
    assert stopped.state == State.CANCELLED
    assert (store.run_dir(run.id) / "report.md").exists()
    resumed = engine.resume(run.id)
    assert resumed.state == State.WAITING_FOR_USER
    assert resumed.task_id == run.task_id


def test_explicit_mode_switch_preserves_research(waiting):
    engine, run = waiting
    config = Config.model_validate(run.config)
    config.backend.codex_command = "/nonexistent/codex"
    switched = engine.resume(run.id, mode="work", config=config)
    assert switched.state == State.FAILED
    assert switched.mode == "work"
    restored = engine.resume(run.id, mode="manual")
    assert restored.state == State.WAITING_FOR_USER
    assert restored.problem == run.problem
    assert restored.task_id == run.task_id


def test_unknown_novelty_and_kernel_checks_do_not_prove_informal_claim(store, config):
    engine = Orchestrator(store)
    run = engine.create(config, demo_problem())
    engine._candidate(run, CandidateInput(claim="A much stronger conjecture", proof="Model proof"))
    review = Review(
        verdict="NO_ISSUES_FOUND",
        truth_assessment="uncertain",
        proof_assessment="looks fine",
        novelty="POTENTIALLY_NEW",
        checks=[{"claim": "Pinned Lean lemma only", "method": "FORMAL", "result": "SUPPORTED",
                 "reasoning": "The trusted check covers True only, not the conjecture."}],
        original_problem_coverage="PARTIAL",
        remaining_obligations=["The original conjecture"],
    )
    candidate = audit(
        run.candidates[0],
        review,
        [
            {
                "tool": "lean_check",
                "phase": "VERIFY",
                "artifact": "experiments/lean.json",
                "result": {
                    "status": "KERNEL_CHECKED",
                    "formal_target": "True",
                    "statement_alignment": "NOT_ASSESSED",
                },
            }
        ],
    )
    assert candidate.level == Level.CANDIDATE
    assert candidate.reviews[0].verdict == "INCONCLUSIVE"
    assert not candidate.reviews[0].proof_coverage.proof_complete
    assert candidate.level != Level.FORMALLY_VERIFIED
    assert candidate.reviews[0].novelty == "UNKNOWN"


def test_report_export_and_cli_errors(tmp_path):
    runner = CliRunner()
    assert runner.invoke(app, ["--root", str(tmp_path), "demo"]).exit_code == 0
    run = Store(tmp_path).list_runs()[0]
    for command in (
        ["status", run.id, "--json"],
        ["report", run.id, "--show"],
        ["export", run.id, "--format", "json"],
    ):
        result = runner.invoke(app, ["--root", str(tmp_path), *command])
        assert result.exit_code == 0, result.output
    destination = tmp_path / "export.md"
    command = ["--root", str(tmp_path), "export", run.id, "--output", str(destination)]
    assert runner.invoke(app, command).exit_code == 0
    assert runner.invoke(app, command).exit_code == 2
