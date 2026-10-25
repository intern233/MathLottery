"""Display research claims independently of workflow execution and verification."""

import pytest

from mathlottery.config import Config
from mathlottery.models import Candidate, Level, ProofCoverage, Review, Run, State, Workflow, digest
from mathlottery.web.outcomes import research_outcome
from mathlottery.web.service import WebService


def candidate(scope="UNKNOWN", claim="A mathematical candidate.", **kwargs):
    return Candidate(id="candidate-123456789abc", sha256=digest(claim + "\nProof"),
                     source_iteration=1, claim=claim, proof="Proof", scope=scope, **kwargs)


def run_with(item=None, **kwargs):
    return Run(id="run-123456789abc", mode="codex", candidates=[item] if item else [],
               config=Config().model_dump(mode="json"), **kwargs)


def review(verdict="NO_ISSUES_FOUND", **kwargs):
    return Review(verdict=verdict, truth_assessment="Assessment", proof_assessment="Assessment", **kwargs)


@pytest.mark.parametrize("scope", ["COMPLETE", "COUNTEREXAMPLE"])
def test_explicit_complete_claim_is_not_downgraded_by_review(scope):
    item = candidate(scope, reviews=[review("ISSUES_FOUND", original_problem_coverage="DIFFERENT",
                                          novelty="KNOWN", remaining_obligations=["Missing lemma"])])
    shown = research_outcome(run_with(item, state=State.COMPLETED))
    assert shown["solve"]["status"] == scope
    assert shown["solve"]["basis"] == "candidate_scope"
    assert shown["verify"]["verdict"] == "ISSUES_FOUND"
    assert shown["verify"]["original_problem_coverage"] == "DIFFERENT"
    assert shown["verify"]["remaining_obligations"] == ["Missing lemma"]


def test_partial_claim_stays_partial_even_when_review_and_level_support_it():
    item = candidate("PARTIAL", level=Level.SELF_CHECKED,
                     reviews=[review(original_problem_coverage="FULL", novelty="POTENTIALLY_NEW")])
    shown = research_outcome(run_with(item, state=State.COMPLETED))
    assert shown["solve"]["status"] == "PARTIAL"
    assert shown["verify"]["verdict"] == "NO_ISSUES_FOUND"
    assert shown["verify"]["original_problem_coverage"] == "FULL"


@pytest.mark.parametrize("claim", [
    "原始 Example #123 的 k=5 存在性目标本轮未解决。所提交的仅是固定配置的部分命题。",
    "部分结论，不是原猜想的证明或反例，也不主张新颖性：一项归约。",
    "本轮仅给出部分结果。",
    "Partial result, not a proof of the original conjecture.",
    "Partial results: a finite case and a reduction.",
    "We provide partial results for restricted parameters.",
    "This is only a partial solution. The general case is open.",
    "We did not solve the original problem. We provide a partial result.",
    "We have not solved the original problem. We provide partial results.",
    "Partial results: this is not a complete proof of the original conjecture.",
    "Partial results: this does not prove the entire original conjecture.",
    "部分结论：这不是完整证明，也不提供原猜想的反例。",
    "部分结论：此结果不证明原猜想。",
])
def test_legacy_explicit_partial_claims_are_displayed_without_mutation(claim):
    item = candidate(claim=claim, reviews=[review()])
    run = run_with(item)
    before = run.model_dump()
    shown = research_outcome(run)
    assert shown["solve"]["status"] == "PARTIAL"
    assert shown["solve"]["basis"] == "explicit_claim_text"
    assert shown["solve"]["legacy_basis"] == "explicit_claim_text"
    assert shown["solve"]["declared_scope"] == "UNKNOWN"
    assert run.model_dump() == before
    assert item.sha256 == digest(claim + "\nProof")


@pytest.mark.parametrize("claim", [
    "不是部分结论，已经完全解决原问题。",
    "原问题并非未解决。",
    "原问题不是没有解决。",
    "Not a partial result. We prove the full theorem.",
    "This is not a partial solution.",
    "Partial solution is not what we are claiming.",
    "部分结论不是本次提交的内容。",
    "No partial result is claimed.",
    "We solve the complete original problem.",
    "An open problem asks whether the property holds.",
    "The original problem remains unsolved. We discuss prior work.",
    "The original problem has not been solved in the literature.",
    "This problem was not solved by earlier researchers.",
    "该问题存在未解决情形，但本文声称证明完整结论。",
    "A source calls this a partial solution; our statement differs.",
    "A long claim about an existing theorem. Partial result appears later.",
    "We have not proved the original conjecture.",
    "We have not proven the original conjecture.",
    "This attempt could not prove the conjecture.",
    "本轮尚未给出证明。",
    "本次没有找到反例。",
    "We did not solve the original problem in the first draft.",
    "We did not solve the original problem by induction.",
    "We did not solve the original problem's stronger generalization.",
    "We provide partial results in the previous draft.",
    "本轮未能解决原问题的较强推广。",
    "本轮未能解决原问题 的较强推广。",
])
def test_legacy_ambiguous_positive_or_negated_claims_remain_unknown(claim):
    shown = research_outcome(run_with(candidate(claim=claim, reviews=[review(original_problem_coverage="FULL")]),
                                      state=State.COMPLETED))
    assert shown["solve"]["status"] == "UNKNOWN"
    assert shown["solve"]["basis"] == "undeclared_scope"


@pytest.mark.parametrize("claim", [
    "We did not solve the original problem.",
    "We have not solved the original problem.",
    "We have not yet resolved the original problem.",
    "This attempt could not resolve the conjecture.",
    "The original problem remains unsolved in this attempt.",
    "本轮未能解决原问题。没有提交证明。",
    "本次没有找到解答。",
    "原始存在性目标本轮未解决。",
])
def test_only_explicit_unsolved_self_descriptions_get_unsolved_status(claim):
    item = candidate(claim=claim)
    before = item.model_dump()
    shown = research_outcome(run_with(item))
    assert shown["solve"]["status"] == "UNSOLVED"
    assert shown["solve"]["basis"] == "explicit_claim_text"
    assert item.model_dump() == before


def test_partial_words_in_later_proof_paragraph_do_not_change_an_unsolved_claim():
    item = candidate(claim="We did not solve the original problem.\n\nWe provide a partial result cited from a paper.")
    assert research_outcome(run_with(item))["solve"]["status"] == "UNSOLVED"


@pytest.mark.parametrize("claim", [
    "We have not proved the conjecture because it is false; here is a counterexample.",
    "本轮没有给出证明，因为原猜想是错误的；下面给出完整反例。",
    "本次没有找到反例，因为下面给出了原猜想的完整证明。",
    "We provide partial results as lemmas and combine them into a complete proof of the original conjecture.",
    "部分结论：先证明以下辅助引理，再由这些引理完整证明原猜想。",
    "We did not solve the original problem in the first draft. This version proves the complete original statement.",
    "We have not proved the conjecture by induction; instead, the complete proof below uses a bijection.",
    "本轮未能解决原问题的较强推广，但原问题本身已被完整解决。",
    "Partial results: the following lemmas are preparatory.\n\nMain result: we prove the entire original conjecture.",
    "We did not solve the original problem in the first draft.\n\nFinal result: we give a counterexample to the full original statement.",
])
def test_conflicting_or_narrow_claims_never_infer_a_legacy_whole_run_outcome(claim):
    item = candidate(claim=claim)
    before = item.model_dump()
    shown = research_outcome(run_with(item))["solve"]
    assert shown["status"] == "UNKNOWN"
    assert shown["basis"] == "undeclared_scope"
    assert item.model_dump() == before


@pytest.mark.parametrize("ending", [
    "We prove the entire original conjecture.",
    "We provide a counterexample to the original conjecture.",
    "最后给出原猜想的完整证明。",
    "最后给出完整反例。",
])
def test_completion_conflicts_anywhere_in_full_claim_veto_the_display_fallback(ending):
    item = candidate(claim="Partial results: finite computations.\n\n" + "Local observations. " * 1000 + ending)
    assert len(item.claim) > 600
    assert research_outcome(run_with(item))["solve"]["status"] == "UNKNOWN"


@pytest.mark.parametrize("scope", ["COMPLETE", "PARTIAL", "COUNTEREXAMPLE"])
def test_explicit_scope_precedes_conflicting_legacy_text(scope):
    item = candidate(scope, "Partial results: auxiliary lemmas.\n\nWe prove the entire original conjecture.")
    shown = research_outcome(run_with(item))["solve"]
    assert shown["status"] == scope
    assert shown["basis"] == "candidate_scope"


def test_declared_scope_precedes_even_conflicting_opening_text():
    shown = research_outcome(run_with(candidate("COMPLETE", "Partial solution in the initial draft.")))
    assert shown["solve"]["status"] == "COMPLETE"
    assert shown["solve"]["basis"] == "candidate_scope"


def test_no_candidate_is_distinct_from_unassessed_scope_and_review():
    empty = research_outcome(run_with(state=State.COMPLETED))
    assert empty["solve"]["status"] == "NO_CANDIDATE"
    assert empty["verify"]["status"] == "NO_CANDIDATE"
    shown = research_outcome(run_with(candidate(), state=State.COMPLETED))
    assert shown["solve"]["status"] == "UNKNOWN"
    assert shown["verify"]["status"] == "UNREVIEWED"
    assert shown["verify"]["verdict"] is None
    assert shown["verify"]["novelty"] is None
    assert shown["verify"]["proof_coverage"] is None


def test_organize_inherits_the_latest_candidate_without_upgrading_it():
    old = candidate("COMPLETE", reviews=[review()])
    newest = candidate("PARTIAL", remaining_obligations=["Unproved general case"])
    run = run_with(old, workflow=Workflow.ORGANIZE, state=State.COMPLETED)
    run.candidates.append(newest)
    shown = research_outcome(run)
    assert shown["solve"]["status"] == "PARTIAL"
    assert shown["solve"]["remaining_obligations"] == ["Unproved general case"]
    assert shown["verify"]["status"] == "UNREVIEWED"


def test_proof_coverage_is_separate_and_old_default_is_unassessed():
    item = candidate("PARTIAL", reviews=[review()])
    shown = research_outcome(run_with(item))
    assert shown["verify"]["proof_coverage"]["assessed"] is False
    item.reviews.append(review("INCONCLUSIVE", proof_coverage=ProofCoverage(
        policy_version="example-v1", assessed_at="2026-01-01T00:00:00Z", total_steps=3,
        essential_steps=2, supported_steps=["step1"], unresolved_steps=["step2", "step3"],
    )))
    shown = research_outcome(run_with(item))
    assert shown["verify"]["verdict"] == "INCONCLUSIVE"
    assert shown["verify"]["proof_coverage"] == {
        "assessed": True, "proof_complete": False, "statement_aligned": False,
        "total_steps": 3, "essential_steps": 2, "supported_count": 1, "unresolved_count": 2,
    }


def test_summary_projection_is_bounded_without_losing_truncation_information():
    item = candidate("PARTIAL", "x" * 30000, remaining_obligations=["x" * 1000] * 12)
    shown = research_outcome(run_with(item))
    assert len(shown["solve"]["claim"]) == 600 and shown["solve"]["claim_truncated"]
    assert shown["solve"]["remaining_obligations_count"] == 12
    assert shown["solve"]["remaining_obligations_truncated"]
    assert len(shown["solve"]["remaining_obligations"]) == 10
    assert all(len(item) == 300 for item in shown["solve"]["remaining_obligations"])


def test_summary_and_detail_share_read_only_outcomes(tmp_path):
    service = WebService(tmp_path)
    run = run_with(candidate("PARTIAL", reviews=[review()]), workflow=Workflow.SOLVE,
                   state=State.COMPLETED)
    service.store.save(run, "test_outcome")
    before = service.store.load(run.id).model_dump()
    summary = service.summary(service.store.load(run.id))
    detail = service.detail(run.id)
    assert summary["research_outcome"] == detail["research_outcome"]
    assert summary["research_outcome"]["solve"]["status"] == "PARTIAL"
    assert service.store.load(run.id).model_dump() == before
