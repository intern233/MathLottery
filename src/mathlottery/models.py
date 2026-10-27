from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import StrEnum
from typing import Annotated, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def uid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:12]}"


def digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Phase(StrEnum):
    FIND = "FIND"
    SOLVE = "SOLVE"
    VERIFY = "VERIFY"
    ORGANIZE = "ORGANIZE"
    REPORT = "REPORT"


class Workflow(StrEnum):
    FIND = "find"
    SOLVE = "solve"
    VERIFY = "verify"
    ORGANIZE = "organize"
    PIPELINE = "pipeline"


class State(StrEnum):
    CREATED = "CREATED"
    DISCOVERING = "DISCOVERING"
    SELECTING = "SELECTING"
    SOLVING = "SOLVING"
    VERIFYING = "VERIFYING"
    ORGANIZING = "ORGANIZING"
    REPORTING = "REPORTING"
    COMPLETED = "COMPLETED"
    PAUSED = "PAUSED"
    WAITING_FOR_USER = "WAITING_FOR_USER"
    RATE_LIMITED = "RATE_LIMITED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class OpenStatus(StrEnum):
    OPEN = "OPEN"
    SOLVED = "SOLVED"
    PARTIALLY_SOLVED = "PARTIALLY_SOLVED"
    DISPUTED = "DISPUTED"
    UNKNOWN = "UNKNOWN"


class Level(StrEnum):
    CANDIDATE = "CANDIDATE"
    SELF_CHECKED = "SELF_CHECKED"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
    FORMALLY_VERIFIED = "FORMALLY_VERIFIED"
    EXPERT_REVIEWED = "EXPERT_REVIEWED"
    REJECTED = "REJECTED"


class Action(StrEnum):
    REASON = "REASON"
    SEARCH = "SEARCH"
    DECOMPOSE = "DECOMPOSE"
    PROPOSE_LEMMA = "PROPOSE_LEMMA"
    PROVE_LEMMA = "PROVE_LEMMA"
    TEST_CASES = "TEST_CASES"
    FIND_COUNTEREXAMPLE = "FIND_COUNTEREXAMPLE"
    RUN_CODE = "RUN_CODE"
    FORMALIZE = "FORMALIZE"
    REVISE = "REVISE"
    CHANGE_STRATEGY = "CHANGE_STRATEGY"
    SELECT_PROBLEM = "SELECT_PROBLEM"
    SUBMIT_CANDIDATE = "SUBMIT_CANDIDATE"
    REVIEW = "REVIEW"
    STOP = "STOP"


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
    ] = Field(description="ORIGINAL_STATEMENT identifies a published problem or conjecture; "
              "EXPLICIT_OPEN identifies an open-status statement. PRIOR_RESULT and SOLUTION "
              "identify established mathematical results, not just matching conjectures. "
              "Use CORRECTION for an erratum or correction.")
    locator: str = Field(max_length=1000)
    excerpt: str = Field(min_length=1, max_length=2000)
    explanation: str = Field(max_length=5000)
    source_date: str | None = None
    relation: Literal["UNKNOWN", "EQUIVALENT", "SPECIAL_CASE", "DIFFERENT"] = Field(
        default="UNKNOWN", description="Relation of the proposed claim to the cited result. "
        "SPECIAL_CASE means the proposed claim already follows by restricting the cited result, "
        "not that the cited result proves only part of the proposed claim.",
    )


class LiteratureObstacle(Model):
    """A stable research question; RESOLVED is a claim until receipts support it."""

    id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{0,99}$")
    kind: Literal["INACCESSIBLE_SOURCE", "UNCLEAR_COMPARISON", "CONFLICTING_STATUS", "MISSING_PROVENANCE", "OTHER"]
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
        default_factory=list, max_length=30,
        description="Material unresolved evidence, such as an inaccessible potential solution, "
        "a conflicting status claim, or an unclear equivalence. These block a supported assessment.",
    )
    limitations: list[str] = Field(
        default_factory=list, max_length=30,
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


class StatementRisk(Model):
    """A researcher's disclosed statement risk, not an independent certification."""

    id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{0,99}$")
    kind: Literal[
        "QUANTIFIER_AMBIGUITY", "ASSUMPTION_GAP", "SOURCE_CONFLICT", "INCOMPLETE_SOURCE",
        "SCOPE_RESTRICTION", "FORMALIZATION_GAP", "OTHER",
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
    scope_relation: Literal["UNKNOWN", "FULL_STATEMENT", "EXPLICIT_SUBPROBLEM", "INTERPRETATION"] = "UNKNOWN"
    scope_description: str = Field(default="", max_length=10000)
    prior_work_summary: str = Field(default="", max_length=10000)
    statement_risks: list[StatementRisk] = Field(default_factory=list, max_length=30)


class MemoryItem(Model):
    kind: Literal["lemma", "failed_attempt", "counterexample", "reference", "question", "strategy"]
    content: str = Field(min_length=1, max_length=8000)
    status: Literal["unverified", "refuted", "experiment_supported", "verified"] = "unverified"
    source_iteration: int = 0
    dependencies: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)


class ToolCall(Model):
    name: Literal[
        "web_search",
        "web_fetch",
        "python_exec",
        "sympy_compute",
        "lean_check",
        "read_artifact",
        "write_artifact",
        "search_memory",
    ]
    arguments_json: str = Field(default="{}", max_length=100000)

    @model_validator(mode="after")
    def check_arguments(self):
        if not isinstance(json.loads(self.arguments_json), dict):
            raise ValueError("arguments_json must encode a JSON object")
        return self


class CandidateInput(Model):
    claim: str = Field(min_length=1, max_length=30000)
    proof: str = Field(min_length=1, max_length=100000)
    assumptions: list[str] = Field(default_factory=list)
    references: list[Reference] = Field(default_factory=list)
    scope: Literal["UNKNOWN", "COMPLETE", "PARTIAL", "COUNTEREXAMPLE"] = "UNKNOWN"
    remaining_obligations: list[str] = Field(
        default_factory=list, max_length=50,
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
    facet: Literal["DEFINITIONS", "ASSUMPTIONS", "QUANTIFIERS", "DOMAIN", "BOUNDARY_CASES", "CONCLUSION"]
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
        default="", max_length=300,
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
        default_factory=list, max_length=50,
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


class AgentResponse(Model):
    protocol_version: Literal["1.0"] = "1.0"
    run_id: str
    task_id: str
    phase: Phase
    action: Action
    summary: str = Field(min_length=1, max_length=20000)
    tools: list[ToolCall] = Field(default_factory=list, max_length=6)
    memory: list[MemoryItem] = Field(default_factory=list, max_length=20)
    problem: Problem | None = None
    shortlist: list[Problem] = Field(default_factory=list, max_length=10)
    candidate: CandidateInput | None = None
    review: Review | None = None
    next_actions: list[str] = Field(default_factory=list, max_length=10)

    @model_validator(mode="after")
    def payload_matches_action(self):
        if self.action == Action.SELECT_PROBLEM and (not self.problem or self.phase != Phase.FIND):
            raise ValueError("SELECT_PROBLEM requires a problem and FIND phase")
        if self.action == Action.SUBMIT_CANDIDATE and (
            not self.candidate or self.phase != Phase.SOLVE
        ):
            raise ValueError("SUBMIT_CANDIDATE requires a candidate and SOLVE phase")
        if self.action == Action.REVIEW and (not self.review or self.phase != Phase.VERIFY):
            raise ValueError("REVIEW requires a review and VERIFY phase")
        if self.phase == Phase.VERIFY and self.memory:
            raise ValueError("The independent reviewer cannot change solver memory")
        return self


class Candidate(CandidateInput):
    id: str
    sha256: str
    source_iteration: int
    level: Level = Level.CANDIDATE
    reviews: list[Review] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)


class Usage(Model):
    input_tokens: int | None = None
    output_tokens: int | None = None
    cached_input_tokens: int | None = None
    measured_calls: int = 0
    unknown_calls: int = 0
    external_cost_usd: float | None = 0


class NativeCheckpoint(Model):
    """Optional milestone, never a schema imposed on individual research/tool actions."""

    run_id: str
    task_id: str
    kind: Literal["progress", "selection", "candidate", "review", "organization", "stop"] = "progress"
    summary: str = ""
    conclude: bool = False
    problem: Problem | None = None
    shortlist: list[Problem] = Field(default_factory=list)
    candidate: CandidateInput | None = None
    review: Review | None = None
    report_markdown: str | None = Field(default=None, min_length=1, max_length=400000)
    report_markdowns: dict[Literal["zh", "en"], Annotated[str, Field(min_length=1, max_length=400000)]] | None = None

    @model_validator(mode="after")
    def payload_matches_kind(self):
        if (self.kind == "candidate") != (self.candidate is not None):
            raise ValueError("Only a candidate milestone must contain candidate")
        if (self.kind == "review") != (self.review is not None):
            raise ValueError("Only a review milestone must contain review")
        has_report = self.report_markdown is not None or self.report_markdowns is not None
        if (self.kind == "organization") != has_report:
            raise ValueError("Only an organization milestone must contain report_markdown or report_markdowns")
        if self.report_markdown is not None and self.report_markdowns is not None:
            raise ValueError("Use either report_markdown or report_markdowns, not both")
        if self.report_markdowns is not None and set(self.report_markdowns) != {"zh", "en"}:
            raise ValueError("report_markdowns requires complete Chinese (zh) and English (en) reports")
        reports = [self.report_markdown] if self.report_markdown is not None else (self.report_markdowns or {}).values()
        if any(not text.strip() for text in reports):
            raise ValueError("The organized report must not be blank")
        if self.kind == "selection" and (not self.problem or not self.shortlist):
            raise ValueError("Selection requires a selected problem and an ordered shortlist")
        if self.shortlist and self.kind != "selection":
            raise ValueError("Only selection milestones contain a shortlist")
        if self.kind == "selection":
            ids = [p.id for p in self.shortlist]
            if len(ids) != len(set(ids)) or self.problem.id not in ids:
                raise ValueError("Shortlist IDs must be unique and include the selected problem")
            selected = next(p for p in self.shortlist if p.id == self.problem.id)
            if selected != self.problem:
                raise ValueError("Selected problem must match its shortlist entry")
        return self


class NativeFinalization(Model):
    status: Literal["idle", "running", "completed", "incomplete"] = "idle"
    research_limit_seconds: float = Field(default=0, ge=0)
    started_elapsed_seconds: float = Field(default=0, ge=0)
    deadline_elapsed_seconds: float = Field(default=0, ge=0)
    task_id: str | None = None
    reason: str | None = None
    summary_path: str | None = None
    candidate_id: str | None = None


class NativeSession(Model):
    solver_session_id: str | None = None
    reviewer_session_id: str | None = None
    reviewer_candidate_id: str | None = None
    solver_response_id: str | None = None
    reviewer_response_id: str | None = None
    active_attempt: str | None = None
    pending_result: dict | None = None
    history: list[dict] = Field(default_factory=list)
    steering: str | None = None
    checkpoint_error: str | None = None
    review_only: bool = False
    candidate_conclude: bool = False
    finalization: NativeFinalization = Field(default_factory=NativeFinalization)


class ReviewSource(Model):
    """An exact UTF-8 source snapshot, not a claim of successful verification."""

    path: str = Field(min_length=1, max_length=2048)
    size: int = Field(ge=0, le=1_000_000)
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    content: str = Field(max_length=1_000_000)


class ReviewEvidence(Model):
    source_run_id: str = Field(pattern=r"^run-[a-f0-9]{12}$")
    source_candidate_id: str = Field(pattern=r"^candidate-[a-f0-9]{12}$")
    candidate_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    candidate_id: str | None = Field(default=None, pattern=r"^candidate-[a-f0-9]{12}$")
    captured_at: str
    files: list[ReviewSource] = Field(min_length=1, max_length=20)


class DiscoveryFile(Model):
    path: str
    size: int = Field(ge=0)
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")


class DiscoveryContext(Model):
    """Frozen Find material selected by the user, never an inherited reviewer memory."""

    source_run_id: str = Field(pattern=r"^run-[a-f0-9]{12}$")
    problem_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    captured_at: str
    files: list[DiscoveryFile] = Field(default_factory=list)
    omitted: list[str] = Field(default_factory=list)


class ReviewProvenance(Model):
    """Exact solver linkage, including reviews with no file attachments."""

    source_run_id: str = Field(pattern=r"^run-[a-f0-9]{12}$")
    source_candidate_id: str = Field(pattern=r"^candidate-[a-f0-9]{12}$")
    candidate_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")


class OrganizationContext(Model):
    """An immutable evidence bundle for an independent editorial session."""

    source_run_id: str = Field(pattern=r"^run-[a-f0-9]{12}$")
    source_revision: int = Field(ge=0)
    source_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    problem_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    captured_at: str
    language: Literal["zh", "en"] = "zh"
    # None preserves the output contract of historical single-language checkpoints.
    report_languages: list[Literal["zh", "en"]] | None = None
    instructions: str | None = Field(default=None, max_length=30000)
    candidate_hashes: list[dict] = Field(default_factory=list)
    files: list[DiscoveryFile] = Field(default_factory=list)
    omitted: list[str] = Field(default_factory=list)
    lineage: list[dict] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def complete_report_languages(self):
        if self.report_languages is not None and (
            len(self.report_languages) != 2 or set(self.report_languages) != {"zh", "en"}
        ):
            raise ValueError("New organization tasks require both zh and en reports")
        return self


class OrganizationDocument(Model):
    """One language of an editorial report and its independently rendered PDF."""

    markdown: str = Field(min_length=1, max_length=500000)
    markdown_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    created_at: str
    pdf_status: Literal["pending", "ready", "failed"] = "pending"
    pdf_error: str | None = None
    pdf_details: dict = Field(default_factory=dict)


class OrganizationReport(OrganizationDocument):
    """Primary-language output plus translations, never a candidate or review."""

    translations: dict[Literal["zh", "en"], OrganizationDocument] = Field(default_factory=dict)


class Run(Model):
    id: str = Field(pattern=r"^run-[a-f0-9]{12}$")
    mode: Literal["chat", "codex", "work", "manual", "demo"]
    interface_version: int = 2
    workflow: Workflow = Workflow.PIPELINE
    discovery_request: str | None = None
    discovery_count: int = Field(default=5, ge=1, le=50)
    shortlist: list[Problem] = Field(default_factory=list)
    # Old checkpoints have no execution field and retain the original protocol on resume.
    execution: Literal["native", "structured"] = "structured"
    native: NativeSession = Field(default_factory=NativeSession)
    state: State = State.CREATED
    phase: Phase = Phase.FIND
    created_at: str = Field(default_factory=now)
    updated_at: str = Field(default_factory=now)
    iteration: int = 0
    revision: int = 0
    elapsed_seconds: float = 0
    active_since: str | None = None
    problem: Problem | None = None
    source: str | None = None
    memory: list[MemoryItem] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    candidates: list[Candidate] = Field(default_factory=list)
    review_evidence: ReviewEvidence | None = None
    review_literature: list[LiteratureSearch] = Field(default_factory=list, max_length=100)
    review_source: ReviewProvenance | None = None
    discovery_context: DiscoveryContext | None = None
    organization_context: OrganizationContext | None = None
    organization_report: OrganizationReport | None = None
    observations: list[dict] = Field(default_factory=list)
    task_id: str | None = None
    prompt_path: str | None = None
    stop_reason: str | None = None
    last_error: str | None = None
    usage: Usage = Field(default_factory=Usage)
    config: dict = Field(default_factory=dict)
    environment: dict = Field(default_factory=dict)
    # Pending response is committed before tools run; replay reuses recorded tool results.
    pending_response: dict | None = None
    completed_tools: list[dict] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def migrate_manual_chat(cls, value):
        # Old saved Chat runs were manual. Never turn a resume into a paid API request.
        if (
            isinstance(value, dict)
            and "interface_version" not in value
            and value.get("mode") == "chat"
        ):
            value = dict(value, mode="manual", interface_version=2)
            if value.get("config"):
                config = dict(value["config"])
                config["backend"] = dict(config.get("backend", {}), mode="manual")
                value["config"] = config
        return value
