"""Adversarial structural controls; no test treats a model review as expert proof."""

import pytest

from mathlottery.auditor import audit
from mathlottery.models import Candidate, ProofCheck, ProofStep, Review, StatementAlignment, digest

CLAIM = "For every natural number n, n + 0 = n."


def candidate():
    proof = "By the defining zero equation of addition, n + 0 reduces to n for arbitrary n."
    return Candidate(id="candidate-example", claim=CLAIM, proof=proof, sha256=digest(CLAIM + "\n" + proof),
                     scope="COMPLETE", source_iteration=0)


def review():
    return Review(
        verdict="NO_ISSUES_FOUND", truth_assessment="The defining equation holds for all naturals.",
        proof_assessment="Unfolding the recursive definition at zero proves the claim.",
        original_problem_coverage="FULL", coverage_explanation="The domain, quantifier and equation match.",
        checks=[ProofCheck(id="zero", claim=CLAIM, method="DERIVATION", result="SUPPORTED",
                           reasoning="Addition is defined by add(n, 0) = n and add(n, k+1) = succ(add(n, k)); use the first clause."),
                ProofCheck(id="definition", claim="add(n, 0) is defined to be n", method="DERIVATION", result="SUPPORTED",
                           reasoning="This is the zero clause of the recursive definition of addition.")],
        proof_steps=[ProofStep(id="definition", statement="add(n, 0) is defined to be n", check_ids=["definition"]),
                     ProofStep(id="conclusion", kind="CONCLUSION", statement=CLAIM, dependencies=["definition"], check_ids=["zero"])],
        statement_alignment=[StatementAlignment(facet=facet, original=statement, candidate=statement,
                                               assessment="MATCHED", reasoning=reason, check_ids=["zero"])
                             for facet, statement, reason in (
                                 ("DEFINITIONS", "+ denotes natural-number addition", "Both use the same recursive operation."),
                                 ("ASSUMPTIONS", "n is natural; no further hypothesis", "The definition needs no positivity or nonzero assumption."),
                                 ("QUANTIFIERS", "For every n", "n is arbitrary in the zero defining equation."),
                                 ("DOMAIN", "The natural numbers", "No restriction to positive or bounded naturals is used."),
                                 ("BOUNDARY_CASES", "n = 0 is included", "The equation also reduces 0 + 0 to 0."),
                                 ("CONCLUSION", CLAIM, "Exactly the same equality is proved."),
                             )],
    )


def checked(proposed, observations=()):
    return audit(candidate(), proposed, list(observations), original_statement=CLAIM).reviews[-1]


def test_complete_structural_map_stays_model_checked_without_expert_certification():
    result = checked(review())
    assert result.verdict == "NO_ISSUES_FOUND"
    assert result.original_problem_coverage == "FULL"
    assert result.proof_coverage.proof_complete
    assert result.proof_coverage.statement_aligned
    assert not result.proof_coverage.formal_alignment_certified


def test_supplementary_finite_tests_do_not_block_an_actual_derivation():
    proposed = review()
    proposed.checks.append(ProofCheck(id="small", claim="The equality holds for n=0,1,2", method="FINITE_TEST",
                                      result="SUPPORTED", reasoning="Direct substitution at 0, 1 and 2 gives equality."))
    proposed.proof_steps[-1].check_ids.append("small")
    result = checked(proposed)
    assert result.verdict == "NO_ISSUES_FOUND"
    assert result.proof_coverage.proof_complete


def test_stated_missing_obligation_cannot_hide_behind_a_complete_declared_map():
    proposed = review()
    proposed.remaining_obligations = ["The induction step has not been established."]
    result = checked(proposed)
    assert result.verdict == "INCONCLUSIVE"
    assert result.original_problem_coverage == "PARTIAL"


def test_unrelated_supported_check_cannot_validate_the_declared_target():
    proposed = review()
    proposed.checks[0].claim = "1 + 1 = 2"
    proposed.checks[0].reasoning = "Direct evaluation of natural-number addition gives two."
    result = checked(proposed)
    assert result.verdict == "INCONCLUSIVE"
    assert "conclusion" in result.proof_coverage.unresolved_steps


@pytest.mark.parametrize("target", ["original", "candidate"])
def test_conclusion_alignment_cannot_substitute_a_different_statement(target):
    proposed = review()
    setattr(proposed.statement_alignment[-1], target, "The unrelated equality 1 + 1 = 2")
    result = checked(proposed)
    assert result.verdict == "NO_ISSUES_FOUND"
    assert not result.proof_coverage.statement_aligned
    assert result.original_problem_coverage == "UNKNOWN"


def test_no_original_statement_cannot_certify_original_problem_coverage():
    result = audit(candidate(), review(), []).reviews[-1]
    assert result.verdict == "NO_ISSUES_FOUND"
    assert result.original_problem_coverage == "UNKNOWN"


@pytest.mark.parametrize("damage", ["empty", "missing_lemma", "missing_check", "duplicate_step", "duplicate_check", "cycle", "unrelated_conclusion", "optional_dependency", "all_optional", "finite_test"])
def test_incomplete_or_forged_proof_maps_fail_closed(damage):
    proposed = review()
    if damage == "empty":
        proposed.proof_steps = []
    elif damage == "missing_lemma":
        proposed.proof_steps.pop(0)
    elif damage == "missing_check":
        proposed.proof_steps[0].check_ids = ["imaginary-check"]
    elif damage == "duplicate_step":
        proposed.proof_steps.append(proposed.proof_steps[0].model_copy())
    elif damage == "duplicate_check":
        proposed.checks.append(proposed.checks[0].model_copy())
    elif damage == "cycle":
        proposed.proof_steps[0].dependencies = ["conclusion"]
    elif damage == "unrelated_conclusion":
        proposed.proof_steps[-1].statement = "For every natural n, 0 + n = n."
    elif damage == "optional_dependency":
        proposed.proof_steps[0].essential = False
        proposed.proof_steps[0].check_ids = []
    elif damage == "all_optional":
        for step in proposed.proof_steps:
            step.essential = False
    else:
        proposed.checks[0].method = "FINITE_TEST"
    result = checked(proposed)
    assert result.verdict == "INCONCLUSIVE"
    assert not result.proof_coverage.proof_complete
    assert result.original_problem_coverage == "UNKNOWN"


@pytest.mark.parametrize("damage", ["missing", "duplicate", "unresolved", "bad_check", "extra_assumption"])
def test_incomplete_statement_alignment_never_becomes_full_solution(damage):
    proposed = review()
    if damage == "missing":
        proposed.statement_alignment.pop()
    elif damage == "duplicate":
        proposed.statement_alignment[-1] = proposed.statement_alignment[0].model_copy()
    elif damage == "unresolved":
        proposed.statement_alignment[0].assessment = "UNRESOLVED"
    elif damage == "bad_check":
        proposed.statement_alignment[0].check_ids = ["absent"]
    else:
        proposed.statement_alignment[1].candidate = "n must be positive"
        proposed.statement_alignment[1].assessment = "DIFFERENT"
    result = checked(proposed)
    assert result.verdict == "NO_ISSUES_FOUND"  # Validity of submitted claim is separate.
    assert not result.proof_coverage.statement_aligned
    assert result.original_problem_coverage == "UNKNOWN"


@pytest.mark.parametrize("damage", [None, "different_candidate", "different_theorem", "self_report", "empty_declarations"])
def test_formal_evidence_is_bound_to_exact_candidate_and_theorem(damage):
    proposed = review()
    proposed.checks[0].method = "FORMAL"
    proposed.checks[0].formal_declarations = ["Nat.add_zero"]
    receipt = {"status": "KERNEL_REPLAYED", "candidate_sha256": candidate().sha256,
               "declarations": [{"name": "Nat.add_zero"}]}
    if damage == "different_candidate":
        receipt["candidate_sha256"] = "0" * 64
    elif damage == "different_theorem":
        receipt["declarations"] = [{"name": "Nat.zero_add"}]
    elif damage == "empty_declarations":
        proposed.checks[0].formal_declarations = []
    observations = [{"phase": "VERIFY", "tool": "native_formal_check", "result": receipt}]
    if damage == "self_report":
        proposed.formal_receipt = receipt
        observations = []
    result = checked(proposed, observations)
    assert result.verdict == ("NO_ISSUES_FOUND" if damage is None else "INCONCLUSIVE")
    assert result.proof_coverage.proof_complete is (damage is None)


def test_old_reviews_load_unchanged_but_new_audit_requires_mapping():
    legacy = {"verdict": "NO_ISSUES_FOUND", "truth_assessment": "Old finding", "proof_assessment": "Old review"}
    restored = Review.model_validate(legacy)
    assert restored.verdict == "NO_ISSUES_FOUND"
    assert restored.proof_coverage.policy_version is None
    assert checked(restored).verdict == "INCONCLUSIVE"
