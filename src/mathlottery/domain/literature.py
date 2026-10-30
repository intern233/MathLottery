"""Source citations, comparison obstacles, and evidence assessments."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from mathlottery.domain.common import Model


class Reference(Model):
    url: str
    title: str = ""
    authors: list[str] = Field(default_factory=list)
    published_at: str | None = None
    retrieved_at: str | None = None
    summary: str = ""
    source: str = "model_suggested"
    artifact: str | None = None
    sha256: str | None = None


class Citation(Model):
    """An agent's source claim, checked against a separate downloaded snapshot."""

    url: str = Field(max_length=2048)
    role: Literal[
        "ORIGINAL_STATEMENT", "EXPLICIT_OPEN", "SOLUTION", "CORRECTION", "PRIOR_RESULT"
    ] = Field(
        description="ORIGINAL_STATEMENT identifies a published problem or conjecture; "
        "EXPLICIT_OPEN identifies an open-status statement. PRIOR_RESULT and SOLUTION "
        "identify established mathematical results, not just matching conjectures. "
        "Use CORRECTION for an erratum or correction."
    )
    locator: str = Field(max_length=1000)
    excerpt: str = Field(min_length=1, max_length=2000)
    explanation: str = Field(max_length=5000)
    source_date: str | None = None
    relation: Literal["UNKNOWN", "EQUIVALENT", "SPECIAL_CASE", "DIFFERENT"] = Field(
        default="UNKNOWN",
        description="Relation of the proposed claim to the cited result. "
        "SPECIAL_CASE means the proposed claim already follows by restricting the cited result, "
        "not that the cited result proves only part of the proposed claim.",
    )


class LiteratureObstacle(Model):
    """A stable research question; RESOLVED is a claim until receipts support it."""

    id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{0,99}$")
    kind: Literal[
        "INACCESSIBLE_SOURCE",
        "UNCLEAR_COMPARISON",
        "CONFLICTING_STATUS",
        "MISSING_PROVENANCE",
        "OTHER",
    ]
    source_url: str | None = Field(default=None, max_length=2048)
    description: str = Field(min_length=1, max_length=4000)
    impact: str = Field(min_length=1, max_length=4000)
    next_action: str = Field(min_length=1, max_length=4000)
    status: Literal["OPEN", "RESOLVED"] = "OPEN"
    resolution: str = Field(default="", max_length=10000)
    evidence_urls: list[str] = Field(default_factory=list, max_length=30)
    resolves_legacy_gaps: list[str] = Field(default_factory=list, max_length=30)
    required_locator: str = Field(default="", max_length=1000)
    required_excerpt_sha256: str = Field(default="", pattern=r"^(?:[a-f0-9]{64})?$")


class PriorResultComparison(Model):
    id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{0,99}$")
    source_url: str = Field(min_length=1, max_length=2048)
    locator: str = Field(min_length=1, max_length=1000)
    prior_assumptions: str = Field(min_length=1, max_length=5000)
    candidate_assumptions: str = Field(min_length=1, max_length=5000)
    prior_conclusion: str = Field(min_length=1, max_length=5000)
    candidate_conclusion: str = Field(min_length=1, max_length=5000)
    relation: Literal["UNKNOWN", "EQUIVALENT", "SPECIAL_CASE", "DIFFERENT"] = "UNKNOWN"
    reasoning: str = Field(min_length=1, max_length=10000)
    obstacle_ids: list[str] = Field(default_factory=list, max_length=30)


class LiteratureSearch(Model):
    queries: list[str] = Field(default_factory=list, max_length=30)
    conclusion: str = Field(default="", max_length=10000)
    unresolved: list[str] = Field(
        default_factory=list,
        max_length=30,
        description="Material unresolved evidence, such as an inaccessible potential solution, "
        "a conflicting status claim, or an unclear equivalence. These block a supported assessment.",
    )
    limitations: list[str] = Field(
        default_factory=list,
        max_length=30,
        description="General bounds on the search, such as databases, languages and dates covered "
        "or the possibility of unindexed work. These remain visible and do not certify exhaustive "
        "coverage. Never move a specific unresolved source or comparison here.",
    )
    obstacles: list[LiteratureObstacle] = Field(default_factory=list, max_length=100)
    comparisons: list[PriorResultComparison] = Field(default_factory=list, max_length=100)


class EvidenceAssessment(Model):
    """Harness-owned projection. Inputs with this field are always recomputed."""

    policy_version: str | None = None
    assessed_at: str | None = None
    supported: bool = False
    reasons: list[str] = Field(default_factory=list)
    checked_citations: list[dict] = Field(default_factory=list)
    observed_queries: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    obstacles: list[dict] = Field(default_factory=list)
    unresolved_obstacle_ids: list[str] = Field(default_factory=list)
    comparisons: list[dict] = Field(default_factory=list)
    obstacle_changes: list[dict] = Field(default_factory=list)
