"""Candidate evidence must survive refactoring, imports and independent reviews intact."""

import json

import pytest

from mathlottery.candidates import review_input
from mathlottery.config import Config
from mathlottery.demo import demo_problem
from mathlottery.models import CandidateInput, Level, Reference, Review
from mathlottery.native_workspace import NativeWorkspace
from mathlottery.orchestrator import Orchestrator


@pytest.fixture
def candidate_run(store):
    engine = Orchestrator(store)
    run = engine.create(
        Config(),
        demo_problem(),
        candidate=CandidateInput(
            claim="An exact claim",
            proof="An exact proof",
            assumptions=["n is positive"],
            references=[Reference(url="https://example.org/original")],
        ),
    )
    return engine, run


@pytest.mark.parametrize(
    "changed",
    [
        {"claim": "A different claim"},
        {"proof": "A different proof"},
        {"assumptions": []},
        {"references": [{"url": "https://example.org/other"}]},
        {"id": "a-different-id"},
        {"source_iteration": 999},
        {"sha256": "0" * 64},
    ],
)
def test_all_immutable_candidate_fields_are_checked(candidate_run, changed):
    engine, run = candidate_run
    path = engine.candidates.path(run, run.candidates[-1])
    payload = json.loads(path.read_text())
    path.write_text(json.dumps(payload | changed))
    with pytest.raises(ValueError, match="modified"):
        engine.candidates.check(run)


def test_checkpoint_content_must_agree_with_candidate_artifact(candidate_run):
    engine, run = candidate_run
    run.candidates[-1].assumptions.clear()
    with pytest.raises(ValueError, match="modified"):
        engine.candidates.check(run)


def test_review_does_not_rewrite_candidate_or_leak_previous_verdict(candidate_run):
    engine, run = candidate_run
    path = engine.candidates.path(run, run.candidates[-1])
    original = path.read_bytes()
    candidate = engine.candidates.review(
        run,
        Review(
            verdict="NO_ISSUES_FOUND",
            truth_assessment="PREVIOUS_VERDICT",
            proof_assessment="PREVIOUS_VERDICT",
            evidence=["PREVIOUS_CHECK"],
            checks=[{"id": "derivation", "claim": "An exact claim", "method": "DERIVATION", "result": "SUPPORTED",
                     "reasoning": "PREVIOUS_CHECK: explicit mathematical derivation"}],
            proof_steps=[{"id": "conclusion", "kind": "CONCLUSION", "statement": "An exact claim", "check_ids": ["derivation"]}],
        ),
    )
    assert candidate.level == Level.SELF_CHECKED
    assert path.read_bytes() == original
    assert engine.candidates.check(run) == candidate
    workspace = NativeWorkspace(engine.store, engine.candidates)
    prompt = workspace.prepare(run, Config())
    review_file = (workspace.path(run) / "candidate.json").read_text()
    for marker in ("PREVIOUS_VERDICT", "PREVIOUS_CHECK", "SELF_CHECKED"):
        assert marker not in prompt and marker not in review_file
    assert json.loads(review_file) == review_input(candidate)
    assert "n is positive" in review_file
    assert "https://example.org/original" in review_file
