"""Research obstacles persist until explicit resolutions have independently checked sources."""

import pytest
from pydantic import ValidationError

from mathlottery.models import (
    Candidate,
    Citation,
    EvidenceAssessment,
    LiteratureObstacle,
    LiteratureSearch,
    PriorResultComparison,
    Review,
    digest,
    now,
)
from mathlottery.verify.auditor import audit
from mathlottery.verify.obstacles import carry_literature
from mathlottery.verify.policy import assess_novelty, assess_sources, normalized

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


def v3_generated_gap():
    return obstacle(id="gap-" + digest(GAP)[:12], kind="OTHER", source_url=None,
                    resolves_legacy_gaps=[])


def test_v3_unbound_generated_gap_is_projected_once_without_rewriting_history():
    citations, search, records = inputs()
    old = LiteratureSearch(unresolved=[GAP], obstacles=[v3_generated_gap()])
    historical = old.model_dump()
    search.obstacles, search.comparisons, search.unresolved = [], [], []
    current = carry_literature(search, [old])
    first = assess_sources(citations, current, records)
    second = assess_sources(citations, current, records, previous_assessments=[first])
    for assessment in (first, second):
        assert len(assessment.obstacles) == 1
        assert assessment.unresolved_obstacle_ids == [old.obstacles[0].id]
        assert not assessment.obstacles[0]["resolution_supported"]
        assert len(assessment.obstacle_changes) == 1
    assert second.obstacle_changes[0]["change"] == "UNCHANGED"
    assert old.model_dump() == historical
    assert current.obstacles[0].resolves_legacy_gaps == []


def test_v3_unbound_gap_can_close_only_with_the_exact_checked_explicit_binding():
    citations, search, records = inputs()
    old = LiteratureSearch(unresolved=[GAP], obstacles=[v3_generated_gap()])
    historical = old.model_dump()
    first = assess_sources([], old.model_copy(deep=True), [])
    current = carry_literature(search, [old])
    second = assess_sources(citations, current, records, previous_assessments=[first])
    generated_rows = [row for row in second.obstacles if row["id"] == old.obstacles[0].id]
    assert len(generated_rows) == 1
    assert generated_rows[0]["resolution_supported"]
    assert generated_rows[0]["change"] == "RESOLVED"
    assert second.unresolved_obstacle_ids == []
    assert old.model_dump() == historical
    assert current.unresolved == [GAP]


def test_v3_gap_deduplication_keeps_a_distinct_semantic_obligation_with_the_same_text():
    citations, search, records = inputs()
    search.comparisons = []
    search.obstacles = [v3_generated_gap(), obstacle()]
    assessment = assess_sources(citations, search, records)
    assert {row["id"] for row in assessment.obstacles} == {"paper-odd", "gap-" + digest(GAP)[:12]}
    assert len(assessment.obstacles) == 2
    assert len(assessment.unresolved_obstacle_ids) == 2
    assert not any(row["resolution_supported"] for row in assessment.obstacles)


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


def review_with_obstacle(closed):
    citations, search, records = inputs()
    if not closed:
        search.obstacles[0].status = "OPEN"
        search.obstacles[0].resolution = ""
    return Review(verdict="INCONCLUSIVE", truth_assessment="Unknown", proof_assessment="Not assessed",
                  citations=citations, literature_search=search), records


def test_first_verify_records_find_open_to_resolved_without_mutating_find_or_review():
    found, records = review_with_obstacle(False)
    found.evidence_assessment = assess_sources(found.citations, found.literature_search, records)
    frozen = found.model_dump()
    fresh, records = review_with_obstacle(True)
    submitted = fresh.model_dump()
    candidate = Candidate(id="candidate-example", claim="P(n)", proof="Proof",
                          sha256=digest("P(n)\nProof"), source_iteration=0)
    result = audit(candidate, fresh, [{"phase": "VERIFY", "result": record} for record in records],
                   prior_literature=[found.literature_search], prior_assessments=[found.evidence_assessment])
    assessment = result.reviews[-1].evidence_assessment
    change = next(item for item in assessment.obstacle_changes if item["id"] == "paper-odd")
    assert (change["from_status"], change["to_status"], change["change"]) == ("OPEN", "RESOLVED", "RESOLVED")
    assert assessment.comparisons[0]["supported"]
    assert found.model_dump() == frozen
    assert fresh.model_dump() == submitted
    assert candidate.reviews == []


@pytest.mark.parametrize("find_closed,previous_closed,current_closed,expected", [
    (False, True, True, ("RESOLVED", "RESOLVED", "UNCHANGED")),
    (True, False, True, ("OPEN", "RESOLVED", "RESOLVED")),
    (False, True, False, ("RESOLVED", "OPEN", "REOPENED")),
])
def test_newer_candidate_review_transition_overrides_frozen_find(find_closed, previous_closed, current_closed, expected):
    found, records = review_with_obstacle(find_closed)
    found.evidence_assessment = assess_sources(found.citations, found.literature_search, records)
    previous, records = review_with_obstacle(previous_closed)
    previous.evidence_assessment = assess_sources(previous.citations, previous.literature_search, records)
    candidate = Candidate(id="candidate-example", claim="P(n)", proof="Proof",
                          sha256=digest("P(n)\nProof"), source_iteration=0, reviews=[previous])
    frozen = candidate.model_dump()
    fresh, records = review_with_obstacle(current_closed)
    result = audit(candidate, fresh, [{"phase": "VERIFY", "result": record} for record in records],
                   prior_literature=[found.literature_search], prior_assessments=[found.evidence_assessment])
    change = next(item for item in result.reviews[-1].evidence_assessment.obstacle_changes if item["id"] == "paper-odd")
    assert (change["from_status"], change["to_status"], change["change"]) == expected
    assert candidate.model_dump() == frozen
    assert result.reviews[0] == previous


@pytest.mark.parametrize("baseline", [[], [EvidenceAssessment()], [EvidenceAssessment(
    obstacles=[{"id": "paper-odd", "status": "OPEN", "resolution_supported": False}],
)]])
def test_first_verify_with_empty_or_legacy_baseline_has_no_invented_prior_status(baseline):
    fresh, records = review_with_obstacle(True)
    candidate = Candidate(id="candidate-example", claim="P(n)", proof="Proof",
                          sha256=digest("P(n)\nProof"), source_iteration=0)
    result = audit(candidate, fresh, [{"phase": "VERIFY", "result": record} for record in records],
                   prior_assessments=baseline)
    change = result.reviews[-1].evidence_assessment.obstacle_changes[0]
    assert (change["from_status"], change["to_status"], change["change"]) == (None, "RESOLVED", "NEW")


def test_find_baseline_never_replaces_current_verify_source_receipts():
    found, records = review_with_obstacle(True)
    found.evidence_assessment = assess_sources(found.citations, found.literature_search, records)
    fresh, _ = review_with_obstacle(True)
    candidate = Candidate(id="candidate-example", claim="P(n)", proof="Proof",
                          sha256=digest("P(n)\nProof"), source_iteration=0)
    result = audit(candidate, fresh, [], prior_literature=[found.literature_search],
                   prior_assessments=[found.evidence_assessment])
    assessment = result.reviews[-1].evidence_assessment
    change = next(item for item in assessment.obstacle_changes if item["id"] == "paper-odd")
    assert (change["from_status"], change["to_status"], change["change"]) == ("RESOLVED", "OPEN", "REOPENED")
    assert not assessment.supported
    assert not assessment.comparisons[0]["supported"]


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


def source_only_inputs():
    citations, search, records = inputs()
    search.obstacles, search.comparisons, search.unresolved = [], [], []
    citations[0].role = "ORIGINAL_STATEMENT"
    citations[0].relation = "UNKNOWN"
    return citations, search, records


def test_exact_missing_excerpt_closes_from_new_receipt_without_changing_historical_search():
    citations, old, records = source_only_inputs()
    first = assess_sources(citations, old, records[1:])
    historical = old.model_dump()
    registered = old.obstacles[0]
    assert registered.required_locator == citations[0].locator
    assert registered.required_excerpt_sha256 == digest(normalized(citations[0].excerpt))
    fresh = carry_literature(LiteratureSearch(queries=old.queries, conclusion=old.conclusion), [old])
    second = assess_sources(citations, fresh, records, previous_assessments=[first])
    assert second.supported
    assert second.obstacles[0]["status"] == "RESOLVED"
    assert second.obstacles[0]["reported_status"] == "OPEN"
    assert second.obstacles[0]["resolution_basis"] == "CURRENT_SOURCE_RECEIPT"
    assert second.obstacle_changes[0]["change"] == "RESOLVED"
    assert second.unresolved_obstacle_ids == []
    assert old.model_dump() == historical
    assert first.obstacles[0]["status"] == "OPEN"
    # Access to an exact passage is not evidence of novelty.
    assert assess_novelty("POTENTIALLY_NEW", second) == "UNKNOWN"


@pytest.mark.parametrize("damage", ["other_excerpt", "other_locator", "other_version", "stale", "latest_failed", "omitted"])
def test_source_goal_does_not_close_for_nearby_unrelated_or_stale_evidence(damage):
    citations, old, records = source_only_inputs()
    first = assess_sources(citations, old, records[1:])
    registered = old.obstacles[0].id
    fresh = carry_literature(LiteratureSearch(queries=old.queries, conclusion=old.conclusion), [old])
    if damage == "other_excerpt":
        citations[0].excerpt = "A different true sentence in the same paper."
        records[0]["excerpt_hashes"] = [digest(normalized(citations[0].excerpt))]
    elif damage == "other_locator":
        citations[0].locator = "Theorem 200"
    elif damage == "other_version":
        citations[0].url += "?version=2"
        records[0]["url"] = records[0]["requested_url"] = citations[0].url
    elif damage == "stale":
        records[0]["retrieved_at"] = "2000-01-01T00:00:00+00:00"
    elif damage == "latest_failed":
        records.append({"record_kind": "source_snapshot", "requested_url": URL, "status": "UNAVAILABLE"})
    else:
        citations.clear()
    second = assess_sources(citations, fresh, records, previous_assessments=[first])
    assert not second.supported
    assert registered in second.unresolved_obstacle_ids
    row = next(row for row in second.obstacles if row["id"] == registered)
    assert row["change"] == "UNCHANGED" and row["status"] == "OPEN"


def test_a_previously_closed_source_goal_reopens_on_failed_current_receipt():
    citations, search, records = source_only_inputs()
    first = assess_sources(citations, search, records[1:])
    second = assess_sources(citations, search, records, previous_assessments=[first])
    third = assess_sources(citations, search, records[1:], previous_assessments=[first, second])
    assert second.obstacles[0]["resolution_supported"]
    assert third.obstacle_changes[0]["from_status"] == "RESOLVED"
    assert third.obstacle_changes[0]["to_status"] == "OPEN"
    assert third.obstacle_changes[0]["change"] == "REOPENED"
    assert first.obstacles[0]["status"] == "OPEN"  # No rewrites of old projections.


def test_forged_model_resolved_history_is_not_treated_as_controller_history():
    from mathlottery.models import EvidenceAssessment

    citations, search, records = source_only_inputs()
    first = assess_sources(citations, search, records[1:])
    forged = EvidenceAssessment(obstacles=[dict(first.obstacles[0], resolution_supported=True)])
    second = assess_sources(citations, search, records[1:], previous_assessments=[forged])
    assert second.obstacle_changes[0]["change"] == "NEW"


def test_registered_source_target_cannot_be_replaced_in_later_submission():
    citations, old, records = source_only_inputs()
    assess_sources(citations, old, records[1:])
    original = old.obstacles[0]
    changed = original.model_copy(update={"required_locator": "A simpler theorem", "required_excerpt_sha256": "b" * 64})
    inherited = carry_literature(LiteratureSearch(obstacles=[changed]), [old])
    assert inherited.obstacles[0].required_locator == original.required_locator
    assert inherited.obstacles[0].required_excerpt_sha256 == original.required_excerpt_sha256


@pytest.mark.parametrize("observed_redirect", [True, False])
def test_explicit_resolution_accepts_only_a_receipt_backed_original_to_mirror_redirect(observed_redirect):
    citations, search, records = inputs()
    mirror = "https://example.org/official-current"
    citations[0].url = mirror
    records[0]["url"] = mirror
    records[0]["requested_url"] = URL if observed_redirect else mirror
    search.obstacles[0].evidence_urls = [mirror]
    assessment = assess_sources(citations, search, records)
    assert assessment.obstacles[0]["resolution_supported"] is observed_redirect
    assert assessment.supported is observed_redirect


def test_source_receipt_does_not_auto_close_semantic_problem_even_when_same_url_is_accessible():
    citations, search, records = inputs()
    search.obstacles[0].status = "OPEN"
    search.obstacles[0].resolution = ""
    assessment = assess_sources(citations, search, records)
    assert "paper-odd" in assessment.unresolved_obstacle_ids
    assert assessment.comparisons[0]["supported"]


def test_failed_comparison_is_persistent_and_closes_only_with_its_linked_checked_refinement():
    citations, old, records = inputs()
    old.obstacles, old.unresolved = [], []
    old.comparisons[0].relation = "UNKNOWN"
    first = assess_sources(citations, old, records)
    generated = old.obstacles[0]
    assert generated.id in old.comparisons[0].obstacle_ids
    new = carry_literature(LiteratureSearch(queries=old.queries, conclusion=old.conclusion), [old])
    new.comparisons[0].relation = "DIFFERENT"
    second = assess_sources(citations, new, records, previous_assessments=[first])
    assert second.supported
    assert second.obstacles[0]["resolution_basis"] == "CHECKED_LINKED_COMPARISON"
    assert second.obstacle_changes[0]["change"] == "RESOLVED"
    assert first.comparisons[0]["relation"] == "UNKNOWN"


def test_missing_structured_comparison_goal_can_be_closed_by_exact_linked_comparison():
    citations, old, records = inputs()
    old.obstacles, old.unresolved, old.comparisons = [], [], []
    first = assess_sources(citations, old, records)
    assert assess_novelty("POTENTIALLY_NEW", first, old) == "UNKNOWN"
    generated = old.obstacles[0]
    current_comparison = comparison()
    current_comparison.obstacle_ids = [generated.id]
    current = carry_literature(LiteratureSearch(
        queries=old.queries, conclusion=old.conclusion, comparisons=[current_comparison],
    ), [old])
    second = assess_sources(citations, current, records, previous_assessments=[first])
    assert assess_novelty("POTENTIALLY_NEW", second, current) == "POTENTIALLY_NEW"
    assert second.obstacle_changes[0]["change"] == "RESOLVED"


def test_generated_legacy_gap_can_be_closed_by_explicit_binding_without_erasing_text():
    citations, search, records = inputs()
    search.obstacles, search.comparisons = [], []
    first = assess_sources(citations, search, records)
    generated_id = search.obstacles[0].id
    explicit = obstacle(status="RESOLVED", resolution="The exact theorem only addresses even n.",
                        evidence_urls=[URL], resolves_legacy_gaps=[GAP])
    current = carry_literature(LiteratureSearch(
        queries=search.queries, conclusion=search.conclusion, obstacles=[explicit], comparisons=[comparison()],
    ), [search])
    second = assess_sources(citations, current, records, previous_assessments=[first])
    assert second.supported
    assert current.unresolved == [GAP]
    assert next(row for row in second.obstacles if row["id"] == generated_id)["change"] == "RESOLVED"
    assert first.unresolved_obstacle_ids == [generated_id]


def test_new_failure_at_original_url_invalidates_older_redirect_receipt():
    citations, search, records = inputs()
    mirror = "https://example.org/official-current"
    citations[0].url = mirror
    records[0]["url"] = mirror
    search.obstacles[0].evidence_urls = [mirror]
    records.append({"record_kind": "source_snapshot", "requested_url": URL, "status": "UNAVAILABLE",
                    "reason": "Source returned HTTP 403"})
    assessed = assess_sources(citations, search, records)
    assert not assessed.checked_citations[0]["verified_excerpt"]
    assert "paper-odd" in assessed.unresolved_obstacle_ids


def test_a_new_unknown_comparison_does_not_keep_an_older_supported_resolution():
    citations, old, records = inputs()
    old.obstacles, old.unresolved = [], []
    old.comparisons[0].relation = "UNKNOWN"
    first = assess_sources(citations, old, records)
    current = carry_literature(LiteratureSearch(queries=old.queries, conclusion=old.conclusion), [old])
    current.comparisons[0].relation = "DIFFERENT"
    second = assess_sources(citations, current, records, previous_assessments=[first])
    newer = carry_literature(LiteratureSearch(queries=old.queries, conclusion=old.conclusion), [old, current])
    newer.comparisons[0].relation = "UNKNOWN"
    third = assess_sources(citations, newer, records, previous_assessments=[first, second])
    assert third.obstacle_changes[0]["change"] == "REOPENED"
    assert not third.supported


def test_a_linked_comparison_of_another_source_cannot_close_the_registered_goal():
    citations, old, records = inputs()
    old.obstacles, old.unresolved, old.comparisons = [], [], []
    first = assess_sources(citations, old, records)
    assess_novelty("POTENTIALLY_NEW", first, old)
    generated = old.obstacles[0]
    different = "https://example.org/different-paper"
    citations[0].url = different
    records[0]["url"] = records[0]["requested_url"] = different
    newer = comparison()
    newer.source_url = different
    newer.obstacle_ids = [generated.id]
    current = carry_literature(LiteratureSearch(
        queries=old.queries, conclusion=old.conclusion, comparisons=[newer],
    ), [old])
    second = assess_sources(citations, current, records, previous_assessments=[first])
    assert second.comparisons[0]["supported"]
    assert generated.id in second.unresolved_obstacle_ids


def test_canonical_legacy_id_does_not_bypass_exact_source_resolution_checks():
    citations, search, records = inputs()
    search.unresolved, search.comparisons = [], []
    search.obstacles = [obstacle(
        id="gap-" + digest(GAP)[:12], kind="OTHER", status="RESOLVED", resolution="Read a source.",
        source_url="https://example.org/another-source", evidence_urls=[URL], resolves_legacy_gaps=[GAP],
    )]
    assessed = assess_sources(citations, search, records)
    assert not assessed.supported
    assert not assessed.obstacles[0]["resolution_supported"]
    assert "exact source" in assessed.obstacles[0]["resolution_reason"]


def test_duplicate_generated_legacy_ids_do_not_get_supported_closure():
    citations, search, records = inputs()
    search.obstacles, search.comparisons = [], []
    assess_sources(citations, search, records)
    generated = search.obstacles[0]
    generated.status, generated.resolution, generated.evidence_urls = "RESOLVED", "Exact gap checked.", [URL]
    search.obstacles.append(generated.model_copy())
    assessed = assess_sources(citations, search, records)
    assert not assessed.supported
    assert generated.id in assessed.unresolved_obstacle_ids


@pytest.mark.parametrize("observed_redirect", [True, False])
def test_novelty_uses_same_checked_redirect_identity_as_obstacle_resolution(observed_redirect):
    citations, search, records = inputs()
    mirror = "https://example.org/current"
    citations[0].url = mirror
    records[0]["url"] = mirror
    records[0]["requested_url"] = URL if observed_redirect else mirror
    search.obstacles[0].evidence_urls = [mirror]
    assessment = assess_sources(citations, search, records)
    assert assess_novelty("POTENTIALLY_NEW", assessment, search) == (
        "POTENTIALLY_NEW" if observed_redirect else "UNKNOWN"
    )
    if observed_redirect:
        assert not assessment.unresolved_obstacle_ids


def test_changed_redirect_destination_does_not_verify_a_previous_mirror_citation():
    citations, search, records = inputs()
    old_mirror, new_mirror = "https://example.org/version-1", "https://example.org/version-2"
    citations[0].url = old_mirror
    records[0]["url"] = old_mirror
    search.obstacles[0].evidence_urls = [old_mirror]
    records.append({**records[0], "url": new_mirror})
    result = assess_sources(citations, search, records)
    assert not result.checked_citations[0]["verified_excerpt"]
    assert "no longer resolves" in result.checked_citations[0]["reason"]
    assert not result.supported
    assert assess_novelty("POTENTIALLY_NEW", result, search) == "UNKNOWN"
