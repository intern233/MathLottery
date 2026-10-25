"""Research obstacles persist until explicit resolutions have independently checked sources."""

import pytest
from pydantic import ValidationError

from mathlottery.auditor import audit
from mathlottery.evidence_policy import assess_novelty, assess_sources, normalized
from mathlottery.literature_obstacles import carry_literature
from mathlottery.models import (
    Candidate,
    Citation,
    LiteratureObstacle,
    LiteratureSearch,
    PriorResultComparison,
    Review,
    digest,
    now,
)

URL = "https://example.org/paper"
GAP = "Theorem 2 may already cover the odd case; full text was unavailable."


def obstacle(**kwargs):
    return LiteratureObstacle(**{
        "id": "paper-odd", "kind": "UNCLEAR_COMPARISON", "source_url": URL,
        "description": GAP, "impact": "Could invalidate a novelty claim.",
        "next_action": "Read Theorem 2 and compare the parity hypothesis and conclusion.", **kwargs,
    })


def comparison():
    return PriorResultComparison(
        id="theorem-2", source_url=URL, locator="Theorem 2",
        prior_assumptions="n is even", candidate_assumptions="n is any natural number",
        prior_conclusion="P(n) holds", candidate_conclusion="P(n) holds",
        relation="DIFFERENT", reasoning="Theorem 2 assumes even n and contains no implication for odd n.",
        obstacle_ids=["paper-odd"],
    )


def test_inherited_obstacle_limit_fails_before_writing_an_unloadable_checkpoint():
    previous = LiteratureSearch(obstacles=[obstacle(id=f"prior-{n}") for n in range(100)])
    current = LiteratureSearch(obstacles=[obstacle(id="new-question")])
    with pytest.raises(ValidationError, match="at most 100"):
        carry_literature(current, [previous])
    assert len(previous.obstacles) == 100 and len(current.obstacles) == 1


def inputs():
    citation = Citation(url=URL, role="PRIOR_RESULT", locator="Theorem 2",
                        excerpt="For even n, P(n) holds.", explanation="Only the even case is proved.", relation="DIFFERENT")
    search = LiteratureSearch(
        queries=["P(n) odd case proof Theorem 2"], conclusion="Checked prior theorem and later references.",
        unresolved=[GAP],
        obstacles=[obstacle(status="RESOLVED", resolution="The exact theorem requires even n; the odd case is not included.",
                            evidence_urls=[URL], resolves_legacy_gaps=[GAP])],
        comparisons=[comparison()],
    )
    records = [
        {"record_kind": "source_snapshot", "status": "OK", "requested_url": URL, "url": URL,
         "retrieved_at": now(), "artifact": "literature/paper.txt", "sha256": "a" * 64,
         "excerpt_hashes": [digest(normalized(citation.excerpt))]},
        {"status": "OK", "retrieved_at": now(), "query": search.queries[0]},
    ]
    return [citation], search, records


def test_explicit_source_comparison_can_discharge_specific_legacy_gap():
    citations, search, records = inputs()
    result = assess_sources(citations, search, records)
    assert result.supported
    assert result.unresolved_obstacle_ids == []
    assert result.obstacles[0]["resolution_supported"]
    assert result.comparisons[0]["supported"]
    assert assess_novelty("POTENTIALLY_NEW", result) == "POTENTIALLY_NEW"
    assert search.unresolved == [GAP]  # Historical evidence is retained, not erased.


def test_extra_resolution_url_without_citation_is_actionable_and_still_blocks():
    citations, search, records = inputs()
    missing = "https://example.org/abstract"
    search.obstacles[0].evidence_urls.append(missing)
    result = assess_sources(citations, search, records)
    assert not result.supported
    assert "paper-odd" in result.unresolved_obstacle_ids
    reason = result.obstacles[0]["resolution_reason"]
    assert "no citation to check" in reason and missing in reason
    assert "Add a citation" in reason


def test_existing_but_unverified_extra_resolution_citation_still_blocks():
    citations, search, records = inputs()
    extra = "https://example.org/abstract"
    search.obstacles[0].evidence_urls.append(extra)
    citations.append(Citation(url=extra, role="PRIOR_RESULT", locator="Abstract",
                              excerpt="The theorem concerns even n.", explanation="Related source."))
    result = assess_sources(citations, search, records)
    assert not result.supported
    assert "paper-odd" in result.unresolved_obstacle_ids
    assert "every evidence URL" in result.obstacles[0]["resolution_reason"]


@pytest.mark.parametrize("damage", ["no_receipt", "stale_receipt", "wrong_quote", "wrong_source", "empty_resolution", "no_comparison", "unrelated_locator", "unknown_relation", "missing_legacy_binding", "duplicate_id"])
def test_resolved_checkbox_and_unrelated_evidence_do_not_remove_obstacles(damage):
    citations, search, records = inputs()
    if damage == "no_receipt":
        records.pop(0)
    elif damage == "stale_receipt":
        records[0]["retrieved_at"] = "2000-01-01T00:00:00+00:00"
    elif damage == "wrong_quote":
        records[0]["excerpt_hashes"] = []
    elif damage == "wrong_source":
        search.obstacles[0].evidence_urls = ["https://example.org/unrelated"]
    elif damage == "empty_resolution":
        search.obstacles[0].resolution = " "
    elif damage == "no_comparison":
        search.comparisons = []
    elif damage == "unrelated_locator":
        search.comparisons[0].locator = "Theorem 99"
    elif damage == "unknown_relation":
        search.comparisons[0].relation = "UNKNOWN"
    elif damage == "missing_legacy_binding":
        search.obstacles[0].resolves_legacy_gaps = []
    else:
        search.obstacles.append(search.obstacles[0].model_copy())
    result = assess_sources(citations, search, records)
    assert not result.supported
    assert result.unresolved_obstacle_ids
    assert assess_novelty("POTENTIALLY_NEW", result) == "UNKNOWN"


def test_prior_obstacle_cannot_be_omitted_or_relabeled_as_a_general_limit():
    old = LiteratureSearch(unresolved=[GAP], obstacles=[obstacle()])
    current = LiteratureSearch(limitations=[GAP])
    merged = carry_literature(current, [old])
    assert merged.unresolved == [GAP]
    assert merged.obstacles == old.obstacles
    assert current.unresolved == []
    result = assess_sources([], merged, [])
    assert not result.supported
    assert result.unresolved_obstacle_ids == ["paper-odd"] or "paper-odd" in result.unresolved_obstacle_ids


def test_reusing_id_does_not_replace_an_old_source_with_an_easier_one():
    old = LiteratureSearch(obstacles=[obstacle()])
    new = LiteratureSearch(obstacles=[obstacle(source_url="https://example.org/easier", description="A different question")])
    merged = carry_literature(new, [old])
    assert merged.obstacles[0].source_url == URL
    assert merged.obstacles[0].description == GAP


def test_unknown_comparison_persists_without_an_explicit_model_obstacle():
    prior = comparison()
    prior.relation = "UNKNOWN"
    prior.obstacle_ids = []
    inherited = LiteratureSearch(comparisons=[prior])
    fresh = carry_literature(LiteratureSearch(), [inherited])
    assert fresh.comparisons == [prior]
    result = assess_sources([], fresh, [])
    assert not result.supported
    assert result.obstacles[0]["kind"] == "UNCLEAR_COMPARISON"
    assert result.unresolved_obstacle_ids


def test_carried_comparison_can_be_refined_but_not_changed_to_a_different_theorem():
    _, fresh, _ = inputs()
    old = comparison()
    old.relation = "UNKNOWN"
    fresh.comparisons[0].locator = "Unrelated Theorem 1"
    merged = carry_literature(fresh, [LiteratureSearch(comparisons=[old])])
    assert merged.comparisons[0].locator == "Theorem 2"
    assert merged.comparisons[0].relation == "DIFFERENT"


@pytest.mark.parametrize("latest_status", ["OPEN", "RESOLVED"])
def test_omitted_obstacle_inherits_latest_resolution_or_reopening(latest_status):
    old = obstacle(status="RESOLVED" if latest_status == "OPEN" else "OPEN")
    latest = obstacle(status=latest_status, resolution="Latest source assessment", evidence_urls=[URL])
    result = carry_literature(LiteratureSearch(), [LiteratureSearch(obstacles=[old]), LiteratureSearch(obstacles=[latest])])
    assert result.obstacles[0].status == latest_status
    assert result.obstacles[0].resolution == "Latest source assessment"
    explicit = obstacle(status="OPEN", resolution="Current reviewer questions the comparison")
    current = carry_literature(LiteratureSearch(obstacles=[explicit]), [LiteratureSearch(obstacles=[old]), LiteratureSearch(obstacles=[latest])])
    assert current.obstacles[0].resolution == explicit.resolution


def test_omitted_comparison_inherits_latest_refinement_not_old_unknown_relation():
    old, latest = comparison(), comparison()
    old.relation = "UNKNOWN"
    result = carry_literature(LiteratureSearch(), [LiteratureSearch(comparisons=[old]), LiteratureSearch(comparisons=[latest])])
    assert result.comparisons[0].relation == "DIFFERENT"


def test_legacy_gap_has_stable_actionable_projection_even_without_model_obstacles():
    source = LiteratureSearch(unresolved=[GAP])
    first, second = (assess_sources([], source, []) for _ in range(2))
    assert first.obstacles[0]["id"] == second.obstacles[0]["id"]
    assert first.obstacles[0]["next_action"]
    assert first.obstacles[0]["resolves_legacy_gaps"] == [GAP]


def test_audit_preserves_prior_and_inherited_literature_without_mutating_old_reviews():
    old = Review(verdict="INCONCLUSIVE", truth_assessment="Unknown", proof_assessment="Not assessed",
                 literature_search=LiteratureSearch(obstacles=[obstacle()]))
    candidate = Candidate(id="candidate-example", claim="P(n)", proof="Proof", sha256=digest("P(n)\nProof"),
                          source_iteration=0, reviews=[old])
    fresh = Review(verdict="INCONCLUSIVE", truth_assessment="Unknown", proof_assessment="Not assessed")
    result = audit(candidate, fresh, [], prior_literature=[LiteratureSearch(unresolved=[GAP])])
    assert result.reviews[-1].literature_search.obstacles[0].id == "paper-odd"
    assert result.reviews[-1].literature_search.unresolved == [GAP]
    assert candidate.reviews == [old]
    assert fresh.literature_search.obstacles == []


def test_structured_comparison_required_for_new_positive_novelty_assessment():
    citations, search, records = inputs()
    search.obstacles, search.unresolved, search.comparisons = [], [], []
    result = assess_sources(citations, search, records)
    assert assess_novelty("POTENTIALLY_NEW", result) == "UNKNOWN"
    assert any("structured" in reason for reason in result.reasons)
    assert result.obstacles[0]["source_url"] == URL
    assert result.obstacles[0]["next_action"]


def test_controller_discovered_comparison_gap_survives_later_citation_omission():
    citations, search, records = inputs()
    search.obstacles, search.unresolved, search.comparisons = [], [], []
    review = Review(verdict="INCONCLUSIVE", truth_assessment="Unknown", proof_assessment="Not assessed",
                    novelty="POTENTIALLY_NEW", citations=citations, literature_search=search)
    candidate = Candidate(id="candidate-example", claim="P(n)", proof="Proof", sha256=digest("P(n)\nProof"), source_iteration=0)
    first = audit(candidate, review, [{"phase": "VERIFY", "result": record} for record in records])
    generated = first.reviews[-1].literature_search.obstacles[0]
    assert generated.kind == "UNCLEAR_COMPARISON"
    fresh = Review(verdict="INCONCLUSIVE", truth_assessment="Unknown", proof_assessment="Not assessed")
    second = audit(first, fresh, [])
    assert second.reviews[-1].literature_search.obstacles[0].id == generated.id
    assert generated.id in second.reviews[-1].evidence_assessment.unresolved_obstacle_ids
