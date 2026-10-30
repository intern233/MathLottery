"""Read-only selection warnings; source retrieval is not semantic certification."""

from urllib.parse import urldefrag

from mathlottery.models import Problem


def assess_statement(problem: Problem) -> dict:
    risks = [risk.model_dump(mode="json") for risk in problem.statement_risks]
    missing = []
    if not problem.source_statement.strip():
        missing.append("SOURCE_STATEMENT")
    if problem.scope_relation == "UNKNOWN" or not problem.scope_description.strip():
        missing.append("SCOPE_MAPPING")
    if not problem.prior_work_summary.strip():
        missing.append("PRIOR_WORK")
    source = urldefrag(problem.source_url or "")[0]
    original_receipts = [item for item in problem.evidence_assessment.checked_citations
                         if source and item.get("role") == "ORIGINAL_STATEMENT" and item.get("verified_excerpt")
                         and source in {urldefrag(item.get(field) or "")[0]
                                        for field in ("url", "requested_url", "resolved_url")}]
    if not original_receipts:
        missing.append("ORIGINAL_SOURCE_RECEIPT")
    needs_clarification = any(risk["severity"] == "NEEDS_CLARIFICATION" for risk in risks)
    if problem.scope_relation == "INTERPRETATION":
        needs_clarification = True
    status = "NEEDS_CLARIFICATION" if needs_clarification else (
        "REVIEW_RECOMMENDED" if missing or risks or problem.scope_relation == "EXPLICIT_SUBPROBLEM"
        else "READY_FOR_SELECTION"
    )
    return {
        "policy_version": "statement-selection-v1", "status": status,
        "missing": missing, "risks": risks, "scope_relation": problem.scope_relation,
        "original_excerpt_receipts": len(original_receipts),
        "semantic_alignment_certified": False,
        "scope": "Selection guidance only; disclosures are researcher claims and matching source excerpts do not certify statement equivalence or open status",
    }


def present_problem(problem: Problem) -> dict:
    return problem.model_dump(mode="json") | {"statement_assessment": assess_statement(problem)}
