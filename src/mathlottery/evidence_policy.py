"""Evidence gates, independent of the research agent and transport.

These checks establish traceability, not the truth of a source interpretation or
exhaustiveness of a literature search. Only controller-created snapshots count.
"""

import re
import unicodedata
from datetime import datetime, timezone
from urllib.parse import urldefrag

from mathlottery.models import (
    Citation,
    EvidenceAssessment,
    LiteratureSearch,
    OpenStatus,
    Problem,
    now,
)

POLICY_VERSION = "evidence-v2"


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text)).strip()


def recent(value: str | None) -> bool:
    try:
        age = (datetime.now(timezone.utc) - datetime.fromisoformat(value.replace("Z", "+00:00")))
        return -300 <= age.total_seconds() <= 7 * 86400
    except (AttributeError, TypeError, ValueError):
        return False


def assess_sources(
    citations: list[Citation], search: LiteratureSearch, records: list[dict]
) -> EvidenceAssessment:
    from mathlottery.models import digest

    assessment = EvidenceAssessment(
        policy_version=POLICY_VERSION, assessed_at=now(), limitations=list(search.limitations),
    )
    observed = {
        normalized(query)
        for record in records if record.get("status") == "OK" and recent(record.get("retrieved_at"))
        for query in [record.get("query", ""), *record.get("queries", [])]
        if isinstance(query, str) and query.strip()
    }
    assessment.observed_queries = sorted(observed)
    for citation in citations:
        snapshots = [
            record for record in records
            if record.get("record_kind") == "source_snapshot"
            and citation.url in (record.get("requested_url"), record.get("url"))
        ]
        snapshot = snapshots[-1] if snapshots else {}
        reason = ""
        if not snapshot or snapshot.get("status") != "OK":
            reason = snapshot.get("reason") or "No independently retrieved source snapshot"
        elif not recent(snapshot.get("retrieved_at")):
            reason = "Source snapshot is stale or has an invalid timestamp"
        elif not snapshot.get("sha256") or not snapshot.get("artifact"):
            reason = "Source snapshot lacks a content hash or archived artifact"
        elif digest(normalized(citation.excerpt)) not in snapshot.get("excerpt_hashes", []):
            reason = "Quoted excerpt was not found in the retrieved source text"
        elif not citation.locator.strip() or not citation.explanation.strip():
            reason = "A source locator and explanation of relevance are required"
        assessment.checked_citations.append({
            "url": citation.url, "role": citation.role, "relation": citation.relation,
            "resolved_url": snapshot.get("url"),
            "locator": citation.locator, "source_date": citation.source_date,
            "verified_excerpt": not reason, "reason": reason,
            "artifact": snapshot.get("artifact"), "sha256": snapshot.get("sha256"),
            "retrieved_at": snapshot.get("retrieved_at"),
        })
        if reason:
            assessment.reasons.append(f"{citation.url}: {reason}")
    if not citations:
        assessment.reasons.append("No source quotations and claim-specific comparisons supplied")
    if not search.queries or not search.conclusion.strip():
        assessment.reasons.append("Literature search queries and a coverage explanation are missing")
    elif any(normalized(query) not in observed for query in search.queries):
        assessment.reasons.append("Some declared search queries have no recent observed search-tool receipt")
    if search.unresolved:
        assessment.reasons.extend(f"Unresolved literature gap: {gap}" for gap in search.unresolved)
    assessment.supported = not assessment.reasons
    return assessment


def assess_problem(problem: Problem, records: list[dict]) -> Problem:
    problem = problem.model_copy(deep=True)
    assessment = assess_sources(problem.citations, problem.literature_search, records)
    verified = [c for c in assessment.checked_citations if c["verified_excerpt"]]
    source = urldefrag(problem.source_url or "")[0]
    if not source or not any(
        c["role"] == "ORIGINAL_STATEMENT" and source in {
            urldefrag(c["url"])[0], urldefrag(c.get("resolved_url") or "")[0]
        } for c in verified
    ):
        assessment.reasons.append("The exact original problem has no checked primary-source quotation")
    roles = {c["role"] for c in verified}
    solution = any(
        c["role"] in {"SOLUTION", "PRIOR_RESULT"}
        and c["relation"] in {"EQUIVALENT", "SPECIAL_CASE"} for c in verified
    )
    if problem.status == OpenStatus.OPEN:
        if "EXPLICIT_OPEN" not in roles:
            assessment.reasons.append("No checked source explicitly supports an open status")
        if any(c["role"] == "PRIOR_RESULT" and c["relation"] == "UNKNOWN" for c in verified):
            assessment.reasons.append("A cited prior result has an unresolved relationship to the original problem")
        if solution or any(
            c["role"] in {"SOLUTION", "CORRECTION"} and c["relation"] != "DIFFERENT"
            for c in verified
        ):
            assessment.reasons.append("Possible later solution or correction needs reconciliation")
    elif problem.status == OpenStatus.SOLVED and not solution:
        assessment.reasons.append("No checked solution is compared as equivalent to the original problem")
    elif problem.status in (OpenStatus.PARTIALLY_SOLVED, OpenStatus.DISPUTED):
        if not roles.intersection({"SOLUTION", "CORRECTION", "PRIOR_RESULT"}):
            assessment.reasons.append("No checked result supports the reported status")
    assessment.supported = not assessment.reasons
    if not assessment.supported:
        problem.status = OpenStatus.UNKNOWN
    if solution and "EXPLICIT_OPEN" in roles:
        problem.status = OpenStatus.DISPUTED
    problem.status_checked_at = assessment.assessed_at
    problem.status_evidence = list(dict.fromkeys(c["url"] for c in verified))
    problem.evidence_assessment = assessment
    # Keep model bibliography, but never present model-provided receipt metadata as observed.
    for ref in problem.references:
        match = next((c for c in verified if c["url"] == ref.url), None)
        ref.retrieved_at = match["retrieved_at"] if match else None
        ref.sha256 = match["sha256"] if match else None
        ref.artifact = match["artifact"] if match else None
    return problem


def assess_novelty(reported: str, assessment: EvidenceAssessment) -> str:
    checked = [c for c in assessment.checked_citations if c["verified_excerpt"]]
    prior = [c for c in checked if c["role"] in {"PRIOR_RESULT", "SOLUTION"}]
    if any(c["relation"] == "EQUIVALENT" for c in prior):
        return "KNOWN"
    if any(c["relation"] == "SPECIAL_CASE" for c in prior):
        return "SPECIAL_CASE"
    if reported == "POTENTIALLY_NEW":
        if not prior or any(c["relation"] != "DIFFERENT" for c in prior):
            assessment.reasons.append("Closest prior results lack checked claim-by-claim comparisons")
        assessment.supported = not assessment.reasons
        if assessment.supported:
            return reported
    elif reported in {"KNOWN", "SPECIAL_CASE"}:
        assessment.reasons.append("Reported prior equivalence or special case lacks checked evidence")
        assessment.supported = False
    return "UNKNOWN"
