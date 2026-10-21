from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import StrEnum
from typing import Literal
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
    REPORT = "REPORT"


class Workflow(StrEnum):
    FIND = "find"
    SOLVE = "solve"
    VERIFY = "verify"
    PIPELINE = "pipeline"


class State(StrEnum):
    CREATED = "CREATED"
    DISCOVERING = "DISCOVERING"
    SELECTING = "SELECTING"
    SOLVING = "SOLVING"
    VERIFYING = "VERIFYING"
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
    selection_reason: str = ""
    references: list[Reference] = Field(default_factory=list)
    formal_target: str | None = None
    educational: bool = False


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


class Review(Model):
    verdict: Literal["NO_ISSUES_FOUND", "ISSUES_FOUND", "INCONCLUSIVE"]
    truth_assessment: str
    proof_assessment: str
    issues: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    novelty: Literal["UNKNOWN", "KNOWN", "SPECIAL_CASE", "POTENTIALLY_NEW"] = "UNKNOWN"
    novelty_notes: str = ""
    novelty_references: list[Reference] = Field(default_factory=list)


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
    kind: Literal["progress", "selection", "candidate", "review", "stop"] = "progress"
    summary: str = ""
    conclude: bool = False
    problem: Problem | None = None
    shortlist: list[Problem] = Field(default_factory=list)
    candidate: CandidateInput | None = None
    review: Review | None = None

    @model_validator(mode="after")
    def payload_matches_kind(self):
        if (self.kind == "candidate") != (self.candidate is not None):
            raise ValueError("Only a candidate milestone must contain candidate")
        if (self.kind == "review") != (self.review is not None):
            raise ValueError("Only a review milestone must contain review")
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
