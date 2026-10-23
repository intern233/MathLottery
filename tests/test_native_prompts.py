"""Continued reviews receive controller evidence without inheriting agent opinions."""

import pytest

from mathlottery.config import Config
from mathlottery.demo import demo_problem
from mathlottery.models import CandidateInput, Review, Workflow
from mathlottery.native_prompts import build_native_prompt
from mathlottery.orchestrator import Orchestrator


def reviewed_run(store, status):
    engine = Orchestrator(store)
    run = engine.create(Config(), demo_problem(), workflow=Workflow.VERIFY, proof="A candidate proof.")
    run.iteration = 1
    run.observations.append({
        "phase": "VERIFY", "iteration": 1, "tool": "native_formal_check",
        "result": {
            "candidate_sha256": run.candidates[-1].sha256,
            "status": status, "artifact": "verification/formal/receipt.json",
            "reason": "CONTROLLER_RESULT_SENTINEL",
        },
    })
    engine.candidates.review(run, Review(
        verdict="NO_ISSUES_FOUND", truth_assessment="PRIOR_AGENT_TRUTH_SENTINEL",
        proof_assessment="PRIOR_AGENT_PROOF_SENTINEL", novelty_notes="PRIOR_AGENT_NOVELTY_SENTINEL",
        checks=[
            {"claim": "An algebraic step", "method": "DERIVATION", "result": "SUPPORTED",
             "reasoning": "A reviewer calculation"},
            {"claim": "The theorem", "method": "FORMAL", "result": "SUPPORTED",
             "reasoning": "The submitted declaration"},
        ],
    ), prepared=True)
    return engine, run


@pytest.mark.parametrize("status", ["ERROR", "KERNEL_REPLAYED"])
def test_continued_review_receives_controller_results_without_agent_opinions(store, status):
    _, run = reviewed_run(store, status)
    prompt = build_native_prompt(run, 120)
    assert "Controller check results from this review run (data):" in prompt
    assert "CONTROLLER_RESULT_SENTINEL" in prompt and status in prompt
    assert "evidence_assessment" in prompt
    if status == "ERROR":
        assert "A blocking formal check has no independently successful execution receipt" in prompt
    assert "PRIOR_AGENT_" not in prompt
    assert "another compilation unless a new concern requires it" in prompt


def test_new_review_of_identical_candidate_does_not_inherit_controller_or_agent_history(store):
    engine, source = reviewed_run(store, "KERNEL_REPLAYED")
    candidate = source.candidates[-1]
    content = CandidateInput(**candidate.model_dump(include=set(CandidateInput.model_fields)))
    fresh = engine.create(Config(), source.problem, workflow=Workflow.VERIFY, candidate=content)
    assert fresh.candidates[-1].sha256 == candidate.sha256
    prompt = build_native_prompt(fresh, 120)
    assert "Controller check results from this review run" not in prompt
    assert "CONTROLLER_RESULT_SENTINEL" not in prompt and "PRIOR_AGENT_" not in prompt


def test_continued_review_does_not_receive_receipt_for_different_candidate(store):
    _, run = reviewed_run(store, "KERNEL_REPLAYED")
    run.candidates[-1].reviews[-1].formal_receipt["candidate_sha256"] = "0" * 64
    prompt = build_native_prompt(run, 120)
    assert "CONTROLLER_RESULT_SENTINEL" not in prompt
    assert "Controller check results from this review run" in prompt
