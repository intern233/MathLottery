"""Persistent, receipt-backed literature tasks; no checkbox can establish novelty."""

from mathlottery.models import EvidenceAssessment, LiteratureObstacle, LiteratureSearch, digest


def carry_literature(search: LiteratureSearch, previous: list[LiteratureSearch]) -> LiteratureSearch:
    """Carry unresolved evidence across attempts without carrying reviewer verdicts."""
    search = search.model_copy(deep=True)
    search.unresolved = list(dict.fromkeys([*search.unresolved, *(gap for prior in previous for gap in prior.unresolved)]))
    for collection, identity, links in (
        ("obstacles", ("kind", "source_url", "description", "required_locator", "required_excerpt_sha256"), "resolves_legacy_gaps"),
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


def source_obstacle_id(url: str, locator: str, excerpt_sha256: str) -> str:
    return "source-" + digest(url + "\n" + locator + "\n" + excerpt_sha256)[:20]


def persist_obstacle(search: LiteratureSearch, obstacle: dict) -> LiteratureObstacle:
    """Persist a controller-discovered obligation in this new assessment only."""
    existing = next((item for item in search.obstacles if item.id == obstacle["id"]), None)
    if existing is not None:
        return existing
    item = LiteratureObstacle.model_validate({
        key: value for key, value in obstacle.items() if key in LiteratureObstacle.model_fields
    })
    search.obstacles = [*search.obstacles, item]
    return item


def retain_source_obstacles(search: LiteratureSearch, checked: list[dict]) -> None:
    """A missing exact excerpt cannot disappear when a later submission omits it."""
    for citation in checked:
        if citation["verified_excerpt"]:
            continue
        persist_obstacle(search, {
            "id": source_obstacle_id(citation["url"], citation["locator"], citation["excerpt_sha256"]),
            "kind": "MISSING_PROVENANCE", "source_url": citation["url"],
            "description": f"Independent source excerpt is missing at {citation['locator']}",
            "impact": "This exact source passage has not been independently retrieved and matched",
            "next_action": f"Retry the original URL and exact citation at {citation['locator']}; "
                           "provide a current checked excerpt, or explain an explicit correction with source evidence",
            "required_locator": citation["locator"], "required_excerpt_sha256": citation["excerpt_sha256"],
        })


def matches_source(citation: dict, source_url: str) -> bool:
    # These are endpoints of ONE observed retrieval, never guessed mirror aliases.
    return source_url in {citation["url"], citation.get("requested_url"), citation.get("resolved_url")}


def obstacle_changes(assessment: EvidenceAssessment, previous: list[EvidenceAssessment]) -> None:
    """Compare effective controller verdicts; raw agent RESOLVED claims are not history."""
    latest = {}
    for prior in previous:
        if prior.policy_version:
            for item in prior.obstacles:
                latest[item["id"]] = "RESOLVED" if item.get("resolution_supported") else "OPEN"
    assessment.obstacle_changes = []
    for item in assessment.obstacles:
        before = latest.get(item["id"])
        after = "RESOLVED" if item.get("resolution_supported") else "OPEN"
        change = ("RESOLVED" if after == "RESOLVED" else "REOPENED") if before and before != after else (
            "NEW" if before is None else "UNCHANGED"
        )
        item.update(previous_status=before, change=change)
        assessment.obstacle_changes.append({
            "id": item["id"], "from_status": before, "to_status": after,
            "change": change, "reason": item.get("resolution_reason", ""),
        })


def _comparison_obstacle(comparison) -> dict:
    return {
        "id": "comparison-" + digest(comparison.id)[:12], "kind": "UNCLEAR_COMPARISON",
        "source_url": comparison.source_url,
        "description": f"Prior-result comparison {comparison.id} is not supported by matching source evidence",
        "impact": "The prior theorem may already imply the proposed result",
        "next_action": f"Read {comparison.locator}, compare both hypotheses and conclusions, and attach a matching checked citation",
        "required_locator": comparison.locator,
    }


def _generated_comparison(obstacle, comparison: dict) -> bool:
    return obstacle.id in {
        "comparison-" + digest(comparison["id"])[:12],
        "comparison-" + digest(comparison["source_url"] + "\n" + comparison["locator"])[:12],
    } and (not obstacle.required_locator or obstacle.required_locator == comparison["locator"])


def assess_obstacles(search: LiteratureSearch, assessment: EvidenceAssessment) -> set[str]:
    """Recheck exact source obligations; semantic resolutions still need explicit evidence."""
    verified = [citation for citation in assessment.checked_citations if citation["verified_excerpt"]]
    verified_urls = {c["url"] for c in verified}
    cited_urls = {c["url"] for c in assessment.checked_citations}
    seen_comparisons = set()
    for comparison in search.comparisons:
        substantive = all(getattr(comparison, field).strip() for field in (
            "locator", "prior_assumptions", "candidate_assumptions", "prior_conclusion", "candidate_conclusion", "reasoning",
        ))
        matching = any(matches_source(c, comparison.source_url) and c["locator"] == comparison.locator
                       and c["role"] in {"PRIOR_RESULT", "SOLUTION"}
                       and c["relation"] == comparison.relation for c in verified)
        supported = substantive and matching and comparison.relation != "UNKNOWN" and comparison.id not in seen_comparisons
        seen_comparisons.add(comparison.id)
        if not supported:
            assessment.reasons.append(f"Prior-result comparison {comparison.id} lacks a checked matching theorem and explicit comparison")
            generated = persist_obstacle(search, _comparison_obstacle(comparison))
            # This controller-created obligation refers to this exact comparison.
            comparison.obstacle_ids = list(dict.fromkeys([*comparison.obstacle_ids, generated.id]))
        assessment.comparisons.append(comparison.model_dump() | {"supported": supported})

    discharged = set()
    seen_obstacles = set()
    legacy_generated = []
    for obstacle in search.obstacles:
        if (obstacle.id == "gap-" + digest(obstacle.description)[:12] and obstacle.kind == "OTHER"
            and obstacle.source_url is None and not obstacle.required_locator and not obstacle.required_excerpt_sha256
            and (obstacle.description in obstacle.resolves_legacy_gaps or (
                # v3 persisted this exact generated ID without the later binding
                # field. Defer its one projection to the gap loop without
                # rewriting the historical object or inferring a resolution.
                not obstacle.resolves_legacy_gaps and obstacle.description in search.unresolved
            ))
            and sum(item.id == obstacle.id for item in search.obstacles) == 1):
            legacy_generated.append(obstacle)
            continue
        reason, basis, effective_resolution = "", "EXPLICIT_RESOLUTION", obstacle.resolution
        matching_receipts = [c for c in verified if obstacle.source_url and matches_source(c, obstacle.source_url)
                             and c["locator"] == obstacle.required_locator
                             and c.get("excerpt_sha256") == obstacle.required_excerpt_sha256]
        exact_source_goal = bool(
            obstacle.kind == "MISSING_PROVENANCE" and obstacle.required_excerpt_sha256
            and obstacle.id == source_obstacle_id(
                obstacle.source_url or "", obstacle.required_locator, obstacle.required_excerpt_sha256,
            )
        )
        linked_comparisons = [c for c in assessment.comparisons if c["supported"] and obstacle.id in c["obstacle_ids"]
                              and c["source_url"] == obstacle.source_url
                              and (not obstacle.required_locator or c["locator"] == obstacle.required_locator)]
        if obstacle.id in seen_obstacles:
            reason = "Duplicate obstacle ID"
        elif exact_source_goal and matching_receipts:
            basis = "CURRENT_SOURCE_RECEIPT"
            effective_resolution = "The registered source URL, locator and exact excerpt now have a current independently checked receipt"
        elif (obstacle.kind == "UNCLEAR_COMPARISON" and linked_comparisons
              and any(_generated_comparison(obstacle, c) for c in linked_comparisons)):
            basis = "CHECKED_LINKED_COMPARISON"
            effective_resolution = "The original comparison now has matching current source evidence and explicit hypotheses/conclusions"
        elif exact_source_goal and obstacle.status != "RESOLVED":
            attempted = next((c for c in assessment.checked_citations
                              if c["url"] == obstacle.source_url and c["locator"] == obstacle.required_locator
                              and c.get("excerpt_sha256") == obstacle.required_excerpt_sha256), None)
            reason = (attempted.get("reason") if attempted else None) or (
                "No current checked citation matches this exact source, locator and excerpt; resubmit the registered citation"
            )
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
        elif obstacle.source_url and not any(
            c["url"] in obstacle.evidence_urls and matches_source(c, obstacle.source_url) for c in verified
        ):
            reason = "Resolution has not checked the obstacle's exact source; cite an accessible mirror as the original source's verified redirect"
        elif obstacle.required_locator and not any(
            c["url"] in obstacle.evidence_urls and matches_source(c, obstacle.source_url)
            and c["locator"] == obstacle.required_locator for c in verified
        ):
            reason = "Resolution has not checked the exact registered source locator"
        elif obstacle.kind in {"UNCLEAR_COMPARISON", "CONFLICTING_STATUS"} and not any(
            comparison in linked_comparisons and any(
                c["url"] in obstacle.evidence_urls and matches_source(c, comparison["source_url"])
                for c in verified
            ) for comparison in assessment.comparisons
        ):
            reason = "Resolution needs a checked prior-result comparison linked to this obstacle ID"
        seen_obstacles.add(obstacle.id)
        supported = not reason
        evidence_urls = list(obstacle.evidence_urls)
        if supported and basis == "CURRENT_SOURCE_RECEIPT":
            evidence_urls = list(dict.fromkeys(c["url"] for c in matching_receipts))
        elif supported and basis == "CHECKED_LINKED_COMPARISON":
            evidence_urls = list(dict.fromkeys(c["url"] for c in verified if matches_source(c, obstacle.source_url)))
        assessment.obstacles.append(obstacle.model_dump() | {
            "reported_status": obstacle.status, "status": "RESOLVED" if supported else "OPEN",
            "resolution": effective_resolution if supported else obstacle.resolution,
            "evidence_urls": evidence_urls, "resolution_supported": supported,
            "resolution_basis": basis if supported else "UNRESOLVED",
            "resolution_reason": effective_resolution if supported else reason,
        })
        if supported:
            discharged.update(obstacle.resolves_legacy_gaps)
        else:
            assessment.unresolved_obstacle_ids.append(obstacle.id)
            assessment.reasons.append(f"Literature obstacle {obstacle.id}: {reason}")

    # Preserve legacy text and stable IDs. Another explicitly bound, checked
    # resolution can close its projection without deleting the old question.
    gaps = list(dict.fromkeys([*search.unresolved, *(o.description for o in legacy_generated)]))
    for gap in gaps:
        generated = next((o for o in legacy_generated if o.description == gap), None)
        bound = any(gap in obstacle.resolves_legacy_gaps and obstacle not in legacy_generated for obstacle in search.obstacles)
        if gap not in discharged:
            assessment.reasons.append(f"Unresolved literature gap: {gap}")
        if bound and generated is None:
            continue
        generated = generated or persist_obstacle(search, {
            "id": "gap-" + digest(gap)[:12], "kind": "OTHER", "description": gap,
            "impact": "Blocks a supported literature assessment",
            "next_action": "Investigate this exact gap; supply a resolution, checked citations and resolves_legacy_gaps containing this description",
            "resolves_legacy_gaps": [gap],
        })
        supported = gap in discharged
        # A newly supplied explicit answer to the generated gap itself is allowed.
        if not supported and generated.status == "RESOLVED" and generated.resolution.strip() and generated.evidence_urls:
            supported = set(generated.evidence_urls).issubset(verified_urls)
            if supported:
                discharged.add(gap)
                assessment.reasons.remove(f"Unresolved literature gap: {gap}")
        assessment.obstacles.append(generated.model_dump() | {
            "reported_status": generated.status, "status": "RESOLVED" if supported else "OPEN",
            "resolution_supported": supported, "resolution_basis": "EXPLICIT_GAP_BINDING" if supported else "UNRESOLVED",
            "resolution_reason": "Exact legacy gap is bound to a current checked resolution" if supported else "Legacy literature gap remains unresolved",
        })
        if not supported:
            assessment.unresolved_obstacle_ids.append(generated.id)
    assessment.unresolved_obstacle_ids = list(dict.fromkeys(assessment.unresolved_obstacle_ids))
    return discharged
