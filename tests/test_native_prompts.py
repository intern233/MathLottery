"""Continued reviews receive controller evidence without inheriting agent opinions."""

import pytest

from mathlottery.config import Config
from mathlottery.demo import demo_problem
from mathlottery.models import CandidateInput, Phase, Review, State, Workflow, digest
from mathlottery.native_prompts import build_native_prompt, milestone_schema
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
        assert "A blocking formal check has no matching independently checked theorem declarations" in prompt
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


def test_organize_requires_full_parallel_reports_with_identical_evidence_limits(store):
    engine, source = reviewed_run(store, "ERROR")
    source.state, source.phase = State.COMPLETED, Phase.REPORT
    store.save(source, "fixture_reviewed")
    run = engine.organize(Config(), source.id, language="en")
    prompt = build_native_prompt(run, 120)
    assert "two complete, standalone reports" in prompt
    assert "not a summary" in prompt and "theorem and lemma numbering" in prompt
    assert "endpoint cases" in prompt and "all limitations equivalent" in prompt
    assert '"report_markdowns"' in prompt and '"zh"' in prompt and '"en"' in prompt
    assert "default display" in prompt and "compatibility filename" in prompt
    assert "Do not rerun expensive compilation merely for formatting" in prompt
    run.organization_context.report_languages = None
    legacy_prompt = build_native_prompt(run, 120)
    assert "historical task retains its original single-language output contract" in legacy_prompt
    assert '"report_markdown":' in legacy_prompt


@pytest.mark.parametrize("mode", ["codex", "chat"])
def test_organize_distinguishes_statement_receipt_hash_from_full_problem_fingerprint(store, mode):
    engine, source = reviewed_run(store, "KERNEL_REPLAYED")
    source.state, source.phase = State.COMPLETED, Phase.REPORT
    store.save(source, "fixture_reviewed")
    run = engine.organize(Config(), source.id)
    run.mode = mode
    statement_hash = digest(run.problem.statement)
    record_hash = run.organization_context.problem_sha256
    assert statement_hash != record_hash
    prompt = build_native_prompt(run, 120)
    assert f"statement-text SHA-256 is {statement_hash}" in prompt
    assert f"full-record fingerprint is {record_hash}" in prompt
    assert "compare each hash only within its own domain" in prompt
    assert "does not certify mathematical or natural-language correspondence" in prompt


@pytest.mark.parametrize("workflow", [Workflow.FIND, Workflow.SOLVE, Workflow.VERIFY])
@pytest.mark.parametrize("mode", ["codex", "chat"])
def test_research_prompts_keep_editorial_reports_out_of_milestones(store, workflow, mode):
    run = Orchestrator(store).create(
        Config(), None if workflow == Workflow.FIND else demo_problem(), workflow=workflow,
        proof="A candidate proof." if workflow == Workflow.VERIFY else None,
    )
    run.mode = mode
    prompt = build_native_prompt(run, 120)
    assert "report_markdown and report_markdowns are valid only for kind=organization" in prompt
    assert "Omit both report fields from progress, selection, candidate, review and stop milestones" in prompt
    assert "Find reports may be saved as workspace artifacts, never as milestone report fields" in prompt


def test_shared_milestone_schema_documents_organization_only_report_fields():
    properties = milestone_schema()["properties"]
    for field in ("report_markdown", "report_markdowns"):
        description = properties[field]["description"]
        assert "Valid only for kind=organization" in description
        assert "omit for every other kind, including Find selection" in description
        assert "final Markdown answer or workspace artifacts" in description
