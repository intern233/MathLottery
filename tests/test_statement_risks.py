"""Selection disclosures must survive freezing without pretending to certify meaning."""

import pytest

from mathlottery.discovery import problem_fingerprint
from mathlottery.models import Problem, StatementRisk
from mathlottery.statement_risks import assess_statement, present_problem


def problem():
    return Problem(id="open-example", title="A conjecture", statement="For all positive x, P(x).",
                   source_url="https://example.org/original")


def test_legacy_problem_is_explicitly_unassessed_and_not_mutated():
    item = problem()
    before = item.model_dump()
    shown = present_problem(item)
    assert shown["statement_assessment"]["status"] == "REVIEW_RECOMMENDED"
    assert "SOURCE_STATEMENT" in shown["statement_assessment"]["missing"]
    assert item.model_dump() == before


def test_retrieved_excerpt_does_not_certify_semantic_alignment():
    item = problem()
    item.source_statement = item.statement
    item.scope_relation = "FULL_STATEMENT"
    item.scope_description = "The same positive real domain and universal quantifier."
    item.prior_work_summary = "The source lists a verified finite special case."
    item.evidence_assessment.checked_citations = [{
        "url": item.source_url, "role": "ORIGINAL_STATEMENT", "verified_excerpt": True,
    }]
    assessment = assess_statement(item)
    assert assessment["status"] == "READY_FOR_SELECTION"
    assert assessment["semantic_alignment_certified"] is False
    item.scope_relation = "INTERPRETATION"
    assert assess_statement(item)["status"] == "NEEDS_CLARIFICATION"


@pytest.mark.parametrize("source,receipt_url,expected", [
    ("https://example.org/original", "https://example.org/unrelated", False),
    (None, "https://example.org/original", False),
    ("https://example.org/original?version=2", "https://example.org/original?version=1", False),
    ("https://example.org/original#question-1", "https://example.org/original", True),
])
def test_original_source_receipt_must_match_the_registered_problem(source, receipt_url, expected):
    item = problem()
    item.source_url = source
    item.evidence_assessment.checked_citations = [{
        "url": receipt_url, "role": "ORIGINAL_STATEMENT", "verified_excerpt": True,
    }]
    assessment = assess_statement(item)
    assert assessment["original_excerpt_receipts"] == int(expected)
    assert ("ORIGINAL_SOURCE_RECEIPT" not in assessment["missing"]) is expected


@pytest.mark.parametrize("verified", [True, False])
def test_checked_redirect_endpoints_can_match_the_original_source(verified):
    item = problem()
    item.evidence_assessment.checked_citations = [{
        "url": "https://example.org/current", "requested_url": item.source_url,
        "resolved_url": "https://example.org/current", "role": "ORIGINAL_STATEMENT",
        "verified_excerpt": verified,
    }]
    assert assess_statement(item)["original_excerpt_receipts"] == int(verified)


def test_both_find_protocols_request_statement_risks():
    from mathlottery.evidence_guidance import GUIDANCE
    from mathlottery.models import Phase

    for field in ("source_statement", "scope_relation", "scope_description", "prior_work_summary", "statement_risks"):
        assert field in GUIDANCE[Phase.FIND]


@pytest.mark.parametrize("field,value", [
    ("source_statement", "Original wording"), ("scope_relation", "EXPLICIT_SUBPROBLEM"),
    ("scope_description", "Only the case n = 3"), ("prior_work_summary", "The n = 2 case is known"),
    ("statement_risks", [StatementRisk(id="quantifier", kind="QUANTIFIER_AMBIGUITY",
        severity="NEEDS_CLARIFICATION", description="The quantifier is ambiguous.",
        impact="Different quantifiers give different claims.", next_action="Compare the definition and erratum.")]),
])
def test_every_nonempty_disclosure_is_frozen(field, value):
    item = problem()
    original = problem_fingerprint(item)
    setattr(item, field, value)
    assert problem_fingerprint(item) != original


def test_legacy_obstacle_fields_do_not_change_frozen_problem_hash():
    from mathlottery.models import LiteratureObstacle, digest
    from mathlottery.storage import json_text

    item = problem()
    obstacle = LiteratureObstacle(
        id="source-access", kind="INACCESSIBLE_SOURCE", source_url=item.source_url,
        description="The original full text was unavailable.", impact="Exact statement cannot be checked.",
        next_action="Retrieve the original source.",
    )
    item.literature_search.obstacles = [obstacle]
    item.evidence_assessment.obstacles = [obstacle.model_dump() | {"resolution_supported": False}]
    legacy = item.model_dump(mode="json")
    for field in ("source_statement", "scope_relation", "scope_description", "prior_work_summary", "statement_risks"):
        legacy.pop(field)
    for field in ("literature_search", "evidence_assessment"):
        legacy[field].pop("obstacle_changes", None)
        for old in legacy[field].get("obstacles", []):
            old.pop("required_locator", None)
            old.pop("required_excerpt_sha256", None)
        for optional in ("limitations", "obstacles", "comparisons", "unresolved_obstacle_ids"):
            if optional in legacy[field] and not legacy[field][optional]:
                legacy[field].pop(optional)
    assert problem_fingerprint(item) == digest(json_text(legacy))
    item.literature_search.obstacles[0].required_locator = "Question 1"
    assert problem_fingerprint(item) != digest(json_text(legacy))
