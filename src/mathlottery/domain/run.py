"""Authoritative workflow checkpoint, including legacy migrations."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from mathlottery.domain.common import Model, Phase, State, Workflow, now
from mathlottery.domain.literature import LiteratureSearch
from mathlottery.domain.organization import OrganizationContext, OrganizationReport
from mathlottery.domain.problem import Problem
from mathlottery.domain.proof import Candidate
from mathlottery.domain.protocol import MemoryItem
from mathlottery.domain.provenance import DiscoveryContext, ReviewEvidence, ReviewProvenance
from mathlottery.domain.session import NativeSession, Usage


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
        if isinstance(value, dict) and value.get("config"):
            config = dict(value["config"])
            solve = dict(config.get("solve", {}))
            if "coordination" not in solve:
                solve["coordination"] = "allocation"
                value = dict(value, config=dict(config, solve=solve))
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
