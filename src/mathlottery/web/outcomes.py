"""Bounded, read-only display of the researcher's claim and the separate review."""

from __future__ import annotations

import re

from mathlottery.models import Run


def _conflicting_completion(claim: str) -> bool:
    """A conflicting positive assertion only vetoes inference; it never proves scope."""
    clauses = re.split(
        r"[。！？!?;；\n,，:：]|\.(?=\s|$)|\b(?:but|however|instead)\b|但是|然而|不过|但|却",
        claim, flags=re.IGNORECASE,
    )
    assertions = re.compile(
        r"\b(?:complete|full|entire)\s+(?:proof|solution|resolution|counterexample)\b"
        r"|\b(?:prove[sd]?|proven|solve[sd]?|resolve[sd]?)\s+(?:the\s+)?(?:complete|full|entire)\s+(?:original\s+)?(?:problem|conjecture|statement|goal)\b"
        r"|\bwe\s+(?:prove|solve|resolve|disprove)\s+(?:the\s+)?original\s+(?:problem|conjecture|statement|goal)\b"
        r"|\bcounterexamples?\b"
        r"|(?:完整|完全)(?:的)?(?:证明|解决|解答|反例)"
        r"|(?:证明|解决|否定)(?:了)?(?:整个|完整)?(?:原问题|原猜想|原命题)"
        r"|反例", re.IGNORECASE,
    )
    for clause in clauses:
        for match in assertions.finditer(clause):
            before, after = clause[:match.start()], clause[match.end():]
            # Negative descriptions of completeness do not contradict a partial claim.
            negative_before = re.search(
                r"\b(?:not|no|never|neither|without|cannot|can't|doesn't|don't|didn't|hasn't|haven't|isn't|aren't)\b(?:\W+\w+){0,8}\W*$"
                r"|(?:并非|不是|没有|尚未|未能|不能|不构成|不提供|不主张|不宣称|不声称|不证明|非|无|不)[^。]{0,12}$",
                before, re.IGNORECASE,
            )
            negative_after = re.match(
                r"\s+(?:is|was|has|have|can|could)\s+(?:not|never)\b|(?:不存在|未给出|尚未找到)",
                after, re.IGNORECASE,
            )
            if not negative_before and not negative_after:
                return True
    return False


def _explicit_legacy_scope(claim: str) -> str | None:
    """Recognize only unambiguous opening self-descriptions in old candidates.

    This is a display fallback, not a mathematical assessment or data migration.
    In particular, never infer a complete solution from natural-language prose.
    """
    opening = claim.lstrip()[:600]
    opening = re.sub(r"^(?:#{1,6}\s+|\*\*)", "", opening).strip()
    opening = re.split(r"\n\s*\n", opening, maxsplit=1)[0]
    first_sentence = re.split(r"[。！？!?;；\n]|\.(?=\s|$)", opening, maxsplit=1)[0]
    # Descriptions of earlier drafts or an intermediate method are not whole-run outcomes.
    if re.search(
        r"\b(?:first|earlier|previous|old)\s+(?:draft|version|attempt)\b|\bas (?:auxiliary )?lemmas\b"
        r"|(?:旧稿|初稿|早期版本|先前尝试|之前的尝试|辅助引理|中间引理)",
        first_sentence, re.IGNORECASE,
    ) or _conflicting_completion(claim):
        return None
    partial_patterns = (
        r"^(?:部分(?:结论|结果|解答|进展|证明|命题)|仅有部分(?:结论|结果|解答|进展))(?:[，。；：,.;:\s*]|$)",
        r"^(?:本轮|本次|此次)(?:仅得到|仅获得|仅给出|只得到|只获得|只给出)部分(?:结论|结果|解答|进展)",
        r"^partial (?:results?|solutions?|progress|proofs?|answers?)(?:[,.;:\n*]|$)",
        r"^(?:this (?:is|result is|answer is)|we (?:provide|obtained|obtain)) (?:only )?(?:a )?partial (?:results?|solutions?|proofs?|answers?)\b",
    )
    if any(re.search(pattern, opening, re.IGNORECASE) for pattern in partial_patterns):
        return "PARTIAL"
    unsolved_patterns = (
        r"^(?:原始|原|本|该)[^。！？!?;\n]{0,180}?(?:问题|猜想|目标)(?:本轮|本次|此次)(?:仍未解决|尚未解决|未解决|没有解决|仍未求解|尚未求解)\s*(?:[。！？!?;；]|$)",
        r"^(?:本轮|本次|此次)(?:仍未|尚未|未能|没有)(?:解决|求解)(?:原问题|原猜想|该问题|该猜想)\s*(?:[。！？!?;；]|$)",
        r"^(?:本轮|本次|此次)(?:尚未|未|没有)(?:找到|得到|给出)(?:完整)?(?:解答|解法)\s*(?:[。！？!?;；]|$)",
        r"^we have not (?:yet )?(?:solved|resolved) (?:the )?(?:original )?(?:problem|conjecture|goal)(?: in this attempt)?\s*(?:[.!?;\n]|$)",
        r"^(?:we did not|we could not) (?:yet )?(?:solve|resolve) (?:the )?(?:original )?(?:problem|conjecture|goal)(?: in this attempt)?\s*(?:[.!?;\n]|$)",
        r"^this attempt (?:did not|could not) (?:solve|resolve) (?:the )?(?:original )?(?:problem|conjecture|goal)\s*(?:[.!?;\n]|$)",
        r"^(?:the )?(?:original )?(?:problem|conjecture|goal) remains (?:unsolved|unresolved) in this attempt\s*(?:[.!?;\n]|$)",
    )
    if not any(re.search(pattern, opening, re.IGNORECASE) for pattern in unsolved_patterns):
        return None
    # A failure to settle the original problem can still submit explicit partial results.
    followup_partial = (
        r"(?:所提交的|本次提交的|本轮所得|本轮给出的)(?:仅|只)(?:是)?[^。！？!?;\n]{0,100}部分(?:结论|结果|解答|命题|进展)",
        r"(?:we (?:provide|obtained|obtain)|this (?:submission|result) is) (?:only )?(?:a )?partial (?:results?|solutions?|proofs?|answers?)\b",
    )
    if any(re.search(pattern, opening, re.IGNORECASE) for pattern in followup_partial):
        return "PARTIAL"
    return "UNSOLVED"


def _obligations(items: list[str]) -> dict:
    return {
        "remaining_obligations": [item[:300] for item in items[:10]],
        "remaining_obligations_count": len(items),
        "remaining_obligations_truncated": len(items) > 10 or any(len(item) > 300 for item in items[:10]),
    }


def research_outcome(run: Run) -> dict:
    """Keep candidate scope independent of verdict, proof level and workflow state."""
    candidate = run.candidates[-1] if run.candidates else None
    solve = {
        "status": "NO_CANDIDATE", "basis": "no_candidate", "candidate_id": None,
        "declared_scope": None, "legacy_basis": None, "claim": "", "claim_truncated": False,
        **_obligations([]),
    }
    verify = {
        "status": "NO_CANDIDATE", "basis": "no_candidate", "candidate_id": None,
        "verdict": None, "original_problem_coverage": None, "novelty": None,
        "proof_coverage": None, **_obligations([]),
    }
    if candidate is None:
        return {"solve": solve, "verify": verify}

    status = candidate.scope
    basis = "candidate_scope" if status != "UNKNOWN" else "undeclared_scope"
    if status == "UNKNOWN" and (legacy_scope := _explicit_legacy_scope(candidate.claim)):
        status, basis = legacy_scope, "explicit_claim_text"
    solve.update(
        status=status, basis=basis, candidate_id=candidate.id,
        declared_scope=candidate.scope, claim=candidate.claim[:600],
        legacy_basis="explicit_claim_text" if basis == "explicit_claim_text" else None,
        claim_truncated=len(candidate.claim) > 600, **_obligations(candidate.remaining_obligations),
    )
    verify.update(status="UNREVIEWED", basis="no_review", candidate_id=candidate.id)
    if candidate.reviews:
        review = candidate.reviews[-1]
        coverage = review.proof_coverage
        verify.update(
            status="REVIEWED", basis="latest_candidate_review", verdict=review.verdict,
            original_problem_coverage=review.original_problem_coverage,
            novelty=review.novelty, **_obligations(review.remaining_obligations),
            proof_coverage={
                "assessed": bool(coverage.policy_version and coverage.assessed_at),
                "proof_complete": coverage.proof_complete,
                "statement_aligned": coverage.statement_aligned,
                "total_steps": coverage.total_steps, "essential_steps": coverage.essential_steps,
                "supported_count": len(coverage.supported_steps),
                "unresolved_count": len(coverage.unresolved_steps),
            },
        )
    return {"solve": solve, "verify": verify}
