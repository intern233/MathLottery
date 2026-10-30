"""Problem statements, selection metadata, and disclosed scope risks."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from mathlottery.domain.common import Model, OpenStatus
from mathlottery.domain.literature import Citation, EvidenceAssessment, LiteratureSearch, Reference


class StatementRisk(Model):
    """A researcher's disclosed statement risk, not an independent certification."""

    id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{0,99}$")
    kind: Literal[
        "QUANTIFIER_AMBIGUITY",
        "ASSUMPTION_GAP",
        "SOURCE_CONFLICT",
        "INCOMPLETE_SOURCE",
        "SCOPE_RESTRICTION",
        "FORMALIZATION_GAP",
        "OTHER",
    ]
    severity: Literal["INFO", "CAUTION", "NEEDS_CLARIFICATION"] = "CAUTION"
    description: str = Field(min_length=1, max_length=4000)
    impact: str = Field(min_length=1, max_length=4000)
    next_action: str = Field(min_length=1, max_length=4000)
    source_url: str | None = Field(default=None, max_length=2048)
    locator: str = Field(default="", max_length=1000)


class Problem(Model):
    id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{0,99}$")
    title: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    source_url: str | None = None
    field: str = "unknown"
    status: OpenStatus = OpenStatus.UNKNOWN
    status_checked_at: str | None = None
    status_evidence: list[str] = Field(default_factory=list)
    difficulty_estimate: str = "unknown"
    verification_feasibility: str = "unknown"
    lean_feasibility: str = "unknown"
    prerequisites: list[str] = Field(default_factory=list)
    known_obstacles: list[str] = Field(default_factory=list)
    initial_approach: str = ""
    selection_reason: str = ""
    references: list[Reference] = Field(default_factory=list)
    formal_target: str | None = None
    educational: bool = False
    citations: list[Citation] = Field(default_factory=list, max_length=30)
    literature_search: LiteratureSearch = Field(default_factory=LiteratureSearch)
    evidence_assessment: EvidenceAssessment = Field(default_factory=EvidenceAssessment)
    source_statement: str = Field(default="", max_length=30000)
    scope_relation: Literal[
        "UNKNOWN", "FULL_STATEMENT", "EXPLICIT_SUBPROBLEM", "INTERPRETATION"
    ] = "UNKNOWN"
    scope_description: str = Field(default="", max_length=10000)
    prior_work_summary: str = Field(default="", max_length=10000)
    statement_risks: list[StatementRisk] = Field(default_factory=list, max_length=30)
