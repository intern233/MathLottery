"""Persistent, receipt-backed literature tasks; no checkbox can establish novelty."""

from mathlottery.models import EvidenceAssessment, LiteratureSearch, digest


def carry_literature(search: LiteratureSearch, previous: list[LiteratureSearch]) -> LiteratureSearch:
    """Carry unresolved evidence across attempts without carrying reviewer verdicts."""
    search = search.model_copy(deep=True)
    search.unresolved = list(dict.fromkeys([*search.unresolved, *(gap for prior in previous for gap in prior.unresolved)]))
    for collection, identity, links in (
        ("obstacles", ("kind", "source_url", "description"), "resolves_legacy_gaps"),
        ("comparisons", ("source_url", "locator"), "obstacle_ids"),
    ):
        oldest, latest, inherited_links = {}, {}, {}
        for prior in previous:
            for old in getattr(prior, collection):
                oldest.setdefault(old.id, old)
                latest[old.id] = old
                inherited_links.setdefault(old.id, []).extend(getattr(old, links))
        current = getattr(search, collection)
        current_ids = {item.id for item in current}
        for item_id, old in latest.items():
            if item_id not in current_ids:
                # Inherit the latest state, not the first pre-resolution snapshot.
                current.append(old.model_copy(deep=True))
        for item in current:
            if item.id not in oldest:
                continue
            # Keep the question's original identity while allowing a new answer.
            for field in identity:
                setattr(item, field, getattr(oldest[item.id], field))
            setattr(item, links, list(dict.fromkeys([*inherited_links[item.id], *getattr(item, links)])))
    # Appending to Pydantic list fields bypasses assignment validation. Fail here
    # instead of writing an oversized checkpoint that cannot be loaded later.
    return LiteratureSearch.model_validate(search.model_dump())


def assess_obstacles(search: LiteratureSearch, assessment: EvidenceAssessment) -> set[str]:
    """Return legacy gaps discharged by explicit receipt-backed resolutions."""
    verified = [citation for citation in assessment.checked_citations if citation["verified_excerpt"]]
    verified_urls = {c["url"] for c in verified}
    cited_urls = {c["url"] for c in assessment.checked_citations}
    seen_comparisons = set()
    for comparison in search.comparisons:
        substantive = all(getattr(comparison, field).strip() for field in (
            "locator", "prior_assumptions", "candidate_assumptions", "prior_conclusion", "candidate_conclusion", "reasoning",
        ))
        matching = any(c["url"] == comparison.source_url and c["locator"] == comparison.locator
                       and c["role"] in {"PRIOR_RESULT", "SOLUTION"}
                       and c["relation"] == comparison.relation for c in verified)
        supported = substantive and matching and comparison.relation != "UNKNOWN" and comparison.id not in seen_comparisons
        seen_comparisons.add(comparison.id)
        assessment.comparisons.append(comparison.model_dump() | {"supported": supported})
        if not supported:
            assessment.reasons.append(f"Prior-result comparison {comparison.id} lacks a checked matching theorem and explicit comparison")
            obstacle_id = "comparison-" + digest(comparison.id)[:12]
            assessment.obstacles.append({
                "id": obstacle_id, "kind": "UNCLEAR_COMPARISON", "source_url": comparison.source_url,
                "description": f"Prior-result comparison {comparison.id} is not supported by matching source evidence",
                "impact": "The prior theorem may already imply the proposed result",
                "next_action": f"Read {comparison.locator}, compare both hypotheses and conclusions, and attach a matching checked citation",
                "status": "OPEN", "resolution": "", "evidence_urls": [], "resolves_legacy_gaps": [],
                "resolution_supported": False, "resolution_reason": "Comparison is unresolved or lacks a matching receipt",
            })
            assessment.unresolved_obstacle_ids.append(obstacle_id)

    discharged = set()
    seen_obstacles = set()
    for obstacle in search.obstacles:
        reason = ""
        if obstacle.id in seen_obstacles:
            reason = "Duplicate obstacle ID"
        elif obstacle.status != "RESOLVED":
            reason = "Research obstacle remains open"
        elif not obstacle.resolution.strip():
            reason = "Resolution explanation is missing"
        elif missing := set(obstacle.evidence_urls) - cited_urls:
            reason = (
                "Resolution evidence URLs have no citation to check: " + ", ".join(sorted(missing))
                + ". Add a citation with a source locator and excerpt for each required URL; "
                "keep optional bibliography links outside evidence_urls"
            )
        elif not obstacle.evidence_urls or not set(obstacle.evidence_urls).issubset(verified_urls):
            reason = "Resolution needs independently retrieved, current source excerpts for every evidence URL"
        elif obstacle.source_url and obstacle.source_url not in obstacle.evidence_urls:
            reason = "Resolution has not checked the obstacle's exact source; cite an accessible mirror as the original source's verified redirect"
        elif obstacle.kind in {"UNCLEAR_COMPARISON", "CONFLICTING_STATUS"} and not any(
            comparison["supported"] and obstacle.id in comparison["obstacle_ids"]
            and comparison["source_url"] in obstacle.evidence_urls
            for comparison in assessment.comparisons
        ):
            reason = "Resolution needs a checked prior-result comparison linked to this obstacle ID"
        seen_obstacles.add(obstacle.id)
        supported = not reason
        assessment.obstacles.append(obstacle.model_dump() | {
            "resolution_supported": supported, "resolution_reason": reason,
        })
        if supported:
            discharged.update(obstacle.resolves_legacy_gaps)
        else:
            assessment.unresolved_obstacle_ids.append(obstacle.id)
            assessment.reasons.append(f"Literature obstacle {obstacle.id}: {reason}")

    for gap in search.unresolved:
        if gap in discharged:
            continue
        assessment.reasons.append(f"Unresolved literature gap: {gap}")
        if any(gap in obstacle.resolves_legacy_gaps for obstacle in search.obstacles):
            continue
        obstacle_id = "gap-" + digest(gap)[:12]
        assessment.obstacles.append({
            "id": obstacle_id, "kind": "OTHER", "source_url": None, "description": gap,
            "impact": "Blocks a supported literature assessment",
            "next_action": "Investigate this exact gap; supply a resolution, checked citations and resolves_legacy_gaps containing this description",
            "status": "OPEN", "resolution": "", "evidence_urls": [], "resolves_legacy_gaps": [gap],
            "resolution_supported": False, "resolution_reason": "Legacy literature gap remains unresolved",
        })
        assessment.unresolved_obstacle_ids.append(obstacle_id)
    assessment.unresolved_obstacle_ids = list(dict.fromkeys(assessment.unresolved_obstacle_ids))
    return discharged
