from mathlottery.evidence_policy import assess_novelty, assess_sources
from mathlottery.models import Candidate, Level, Review, digest


def audit(candidate: Candidate, review: Review, observations: list[dict]) -> Candidate:
    if candidate.sha256 != digest(candidate.claim + "\n" + candidate.proof):
        raise ValueError("Candidate integrity check failed; proof or claim was modified")
    candidate = candidate.model_copy(deep=True)
    review = review.model_copy(deep=True)
    current = [o for o in observations if o.get("phase") == "VERIFY"]
    review.reported_verdict, review.reported_novelty = review.verdict, review.novelty
    review.validation_notes = []
    review.evidence_assessment = assess_sources(
        review.citations, review.literature_search, [o.get("result", {}) for o in current]
    )
    review.novelty = assess_novelty(review.novelty, review.evidence_assessment)
    review.formal_receipt = next((
        o["result"] for o in reversed(current)
        if o.get("tool") == "native_formal_check"
        and o.get("result", {}).get("candidate_sha256") == candidate.sha256
    ), None)
    kernel_checked = any(
        o.get("tool") == "lean_check" and o.get("result", {}).get("status") == "KERNEL_CHECKED"
        for o in current
    ) or (review.formal_receipt or {}).get("status") == "KERNEL_REPLAYED"

    def inconclusive(reason):
        review.verdict = "INCONCLUSIVE"
        review.validation_notes.append(reason)

    checks = [c for c in review.checks if c.claim.strip() and c.reasoning.strip()]
    contradictions = [c for c in checks if c.blocking and c.result == "CONTRADICTED"]
    if contradictions:
        review.verdict = "ISSUES_FOUND"
        review.issues.extend(f"{c.claim}: {c.reasoning}" for c in contradictions)
    elif review.verdict == "NO_ISSUES_FOUND":
        if not review.truth_assessment.strip() or not review.proof_assessment.strip() or not checks:
            inconclusive("Positive review lacks substantive, explicit proof checks")
        elif any(c.blocking and c.result == "UNRESOLVED" for c in checks):
            inconclusive("A blocking proof obligation remains unresolved")
        elif review.issues:
            inconclusive("A positive verdict conflicts with the review's unresolved issues")
        elif not any(
            c.result == "SUPPORTED" and (
                c.method in {"DERIVATION", "COUNTEREXAMPLE"}
                or (c.method == "FORMAL" and kernel_checked)
            ) for c in checks
        ):
            inconclusive("Finite tests, references or self-reported formal success do not validate a proof")
    elif review.verdict == "ISSUES_FOUND" and not (review.issues and review.evidence):
        inconclusive("Rejection lacks a concrete issue and supporting evidence")
    if any(c.blocking and c.method == "FORMAL" and c.result == "SUPPORTED" for c in checks):
        if not kernel_checked and review.verdict == "NO_ISSUES_FOUND":
            inconclusive("A blocking formal check has no independently successful execution receipt")

    # A proof of a partial claim can be correct while the original problem remains open.
    obligations = list(dict.fromkeys(candidate.remaining_obligations + review.remaining_obligations))
    review.remaining_obligations = obligations
    if (candidate.scope == "PARTIAL" or obligations) and review.original_problem_coverage != "DIFFERENT":
        if review.original_problem_coverage == "FULL":
            review.validation_notes.append("Full coverage conflicts with the candidate scope or remaining obligations")
        review.original_problem_coverage = "PARTIAL"
    elif review.original_problem_coverage == "FULL" and (
        not review.coverage_explanation.strip()
        or review.verdict != "NO_ISSUES_FOUND"
    ):
        review.original_problem_coverage = "UNKNOWN"
        review.validation_notes.append("Full coverage requires a supported comparison to the original statement")
    candidate.reviews.append(review)
    candidate.evidence.extend(o["artifact"] for o in current if o.get("artifact"))
    candidate.level = Level.CANDIDATE
    if review.verdict == "ISSUES_FOUND":
        candidate.level = Level.REJECTED
    elif review.verdict == "NO_ISSUES_FOUND":
        candidate.level = Level.SELF_CHECKED
        if kernel_checked:
            # Kernel-only checks are not the full formal verification trust policy.
            candidate.level = Level.PARTIALLY_VERIFIED
    return candidate
