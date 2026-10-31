"""Durable native sessions, Solve teams, and usage accounting fields."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from mathlottery.domain.common import Model


class Usage(Model):
    input_tokens: int | None = None
    output_tokens: int | None = None
    cached_input_tokens: int | None = None
    measured_calls: int = 0
    unknown_calls: int = 0
    external_cost_usd: float | None = 0


class NativeFinalization(Model):
    status: Literal["idle", "running", "completed", "incomplete"] = "idle"
    research_limit_seconds: float = Field(default=0, ge=0)
    started_elapsed_seconds: float = Field(default=0, ge=0)
    deadline_elapsed_seconds: float = Field(default=0, ge=0)
    task_id: str | None = None
    reason: str | None = None
    summary_path: str | None = None
    candidate_id: str | None = None


class SolveGroup(Model):
    id: str = Field(pattern=r"^[a-z][a-z0-9_-]{0,39}$")
    agents: int = Field(ge=1, le=32, strict=True)
    mode: Literal["independent", "peer", "critique"] = "peer"
    objective: str = Field(min_length=1, max_length=8000)


class SolveWorker(Model):
    id: str
    group: str
    mode: str
    objective: str
    # Durable credential/transport binding, independent of changing research groups.
    slot_id: str | None = None
    session_id: str | None = None
    response_id: str | None = None
    state: Literal["idle", "running", "completed", "interrupted"] = "idle"
    turns: int = 0


class SolveCampaign(Model):
    """Checkpointed supervisor/researcher handshake, separate from Verify."""

    phase: Literal["planning", "researching", "draining", "closing", "completed"] = "planning"
    processed_tasks: list[str] = Field(default_factory=list)
    signals: list[dict] = Field(default_factory=list)
    acknowledged_signals: list[str] = Field(default_factory=list)
    dispatch: list[str] = Field(default_factory=list)
    candidate_reviews: list[dict] = Field(default_factory=list)
    decisions: list[dict] = Field(default_factory=list)
    last_review_elapsed: float = 0
    review_requested: bool = False
    accepted_candidate_id: str | None = None
    summary: str = ""
    summary_path: str | None = None
    closed: bool = False


class SolveTeam(Model):
    groups: list[SolveGroup] = Field(default_factory=list)
    workers: dict[str, SolveWorker] = Field(default_factory=dict)
    active_attempts: list[dict] = Field(default_factory=list)
    pending_receipts: list[dict] = Field(default_factory=list)
    supervisor_session_id: str | None = None
    supervisor_response_id: str | None = None
    supervisor_usage: Usage = Field(default_factory=Usage)
    decision: str | None = None
    rounds: int = 0
    campaign: SolveCampaign = Field(default_factory=SolveCampaign)


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
    solve_team: SolveTeam = Field(default_factory=SolveTeam)
