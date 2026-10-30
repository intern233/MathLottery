"""Candidate proofs, verification requests, and review coverage."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from mathlottery.domain.common import Level, Model
from mathlottery.domain.literature import Citation, EvidenceAssessment, LiteratureSearch, Reference


class CandidateInput(Model):
    claim: str = Field(min_length=1, max_length=30000)
    proof: str = Field(min_length=1, max_length=100000)
    assumptions: list[str] = Field(default_factory=list)
    references: list[Reference] = Field(default_factory=list)
    scope: Literal["UNKNOWN", "COMPLETE", "PARTIAL", "COUNTEREXAMPLE"] = "UNKNOWN"
    remaining_obligations: list[str] = Field(
        default_factory=list,
        max_length=50,
        description="Unresolved mathematical proof or original-statement coverage obligations only, "
        "such as missing lemmas or unproved cases. Use [] when none remain, not a sentence saying "
        "none remain. Describe pending tool checks, novelty questions and external certification "
        "limits separately; never hide an actual proof gap as a validation limitation.",
    )


class ProofCheck(Model):
    id: str = Field(default="", pattern=r"^(?:[A-Za-z0-9][A-Za-z0-9_-]{0,99})?$")
    claim: str = Field(min_length=1, max_length=30000)
    method: Literal["DERIVATION", "COUNTEREXAMPLE", "FINITE_TEST", "FORMAL", "REFERENCE"]
    result: Literal["SUPPORTED", "CONTRADICTED", "UNRESOLVED"]
    reasoning: str = Field(min_length=1, max_length=10000)
    evidence: list[str] = Field(default_factory=list, max_length=30)
    blocking: bool = True
    formal_declarations: list[str] = Field(default_factory=list, max_length=30)


class ProofStep(Model):
    id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{0,99}$")
    statement: str = Field(min_length=1, max_length=30000)
    kind: Literal["LEMMA", "REDUCTION", "CASE", "CONCLUSION"] = "LEMMA"
    dependencies: list[str] = Field(default_factory=list, max_length=100)
    check_ids: list[str] = Field(default_factory=list, max_length=100)
    essential: bool = True


class StatementAlignment(Model):
    facet: Literal[
        "DEFINITIONS", "ASSUMPTIONS", "QUANTIFIERS", "DOMAIN", "BOUNDARY_CASES", "CONCLUSION"
    ]
    original: str = Field(min_length=1, max_length=30000)
    candidate: str = Field(min_length=1, max_length=30000)
    assessment: Literal["MATCHED", "DIFFERENT", "UNRESOLVED"] = "UNRESOLVED"
    reasoning: str = Field(min_length=1, max_length=10000)
    check_ids: list[str] = Field(default_factory=list, max_length=100)
    formal_statement: str = Field(default="", max_length=10000)


class ProofCoverage(Model):
    """Controller-owned structural coverage, never external mathematical certification."""

    policy_version: str | None = None
    assessed_at: str | None = None
    proof_complete: bool = False
    statement_aligned: bool = False
    total_steps: int = 0
    essential_steps: int = 0
    supported_steps: list[str] = Field(default_factory=list)
    unresolved_steps: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
    formal_alignment_certified: Literal[False] = False


class FormalCheckRequest(Model):
    # Ordered modules from the explicitly submitted immutable source snapshot.
    files: list[str] = Field(min_length=1, max_length=20)
    declarations: list[str] = Field(min_length=1, max_length=30)
    module_root: str = Field(
        default="",
        max_length=300,
        description="Module root relative to the submitted workspace, e.g. proof for "
        "workspace/proof/Main.lean importing Lemmas from the same directory. "
        "Empty means workspace. All requested files must be inside this root.",
    )


class Review(Model):
    verdict: Literal["NO_ISSUES_FOUND", "ISSUES_FOUND", "INCONCLUSIVE"]
    truth_assessment: str
    proof_assessment: str
    issues: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    novelty: Literal["UNKNOWN", "KNOWN", "SPECIAL_CASE", "POTENTIALLY_NEW"] = "UNKNOWN"
    novelty_notes: str = ""
    novelty_references: list[Reference] = Field(default_factory=list)
    original_problem_coverage: Literal["UNKNOWN", "FULL", "PARTIAL", "DIFFERENT"] = "UNKNOWN"
    coverage_explanation: str = ""
    remaining_obligations: list[str] = Field(
        default_factory=list,
        max_length=50,
        description="Unresolved mathematical proof or original-statement coverage obligations only. "
        "Use [] when none remain, not a sentence saying none remain. Pending/failed formal execution "
        "belongs in FORMAL checks (blocking when essential) and proof_assessment; specific literature "
        "gaps belong in literature_search.unresolved and novelty_notes. External expert review or "
        "alignment-certification limits belong in proof_assessment or coverage_explanation. Preserve "
        "actual mathematical and statement-alignment gaps; do not relabel them to obtain FULL coverage.",
    )
    checks: list[ProofCheck] = Field(default_factory=list, max_length=100)
    proof_steps: list[ProofStep] = Field(default_factory=list, max_length=100)
    statement_alignment: list[StatementAlignment] = Field(default_factory=list, max_length=20)
    citations: list[Citation] = Field(default_factory=list, max_length=30)
    literature_search: LiteratureSearch = Field(default_factory=LiteratureSearch)
    formal_check: FormalCheckRequest | None = None
    # The controller overwrites these fields; they never establish evidence by themselves.
    evidence_assessment: EvidenceAssessment = Field(default_factory=EvidenceAssessment)
    proof_coverage: ProofCoverage = Field(default_factory=ProofCoverage)
    validation_notes: list[str] = Field(default_factory=list)
    reported_verdict: str | None = None
    reported_novelty: str | None = None
    formal_receipt: dict | None = None


class Candidate(CandidateInput):
    id: str
    sha256: str
    source_iteration: int
    level: Level = Level.CANDIDATE
    reviews: list[Review] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
