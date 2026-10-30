"""Structured responses and optional native research milestones."""

from __future__ import annotations

import json
from typing import Annotated, Literal

from pydantic import Field, model_validator

from mathlottery.domain.common import Action, Model, Phase
from mathlottery.domain.problem import Problem
from mathlottery.domain.proof import CandidateInput, Review


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


class NativeCheckpoint(Model):
    """Optional milestone, never a schema imposed on individual research/tool actions."""

    run_id: str
    task_id: str
    kind: Literal["progress", "selection", "candidate", "review", "organization", "stop"] = (
        "progress"
    )
    summary: str = ""
    conclude: bool = False
    problem: Problem | None = None
    shortlist: list[Problem] = Field(default_factory=list)
    candidate: CandidateInput | None = None
    review: Review | None = None
    report_markdown: str | None = Field(default=None, min_length=1, max_length=400000)
    report_markdowns: (
        dict[Literal["zh", "en"], Annotated[str, Field(min_length=1, max_length=400000)]] | None
    ) = None

    @model_validator(mode="after")
    def payload_matches_kind(self):
        if (self.kind == "candidate") != (self.candidate is not None):
            raise ValueError("Only a candidate milestone must contain candidate")
        if (self.kind == "review") != (self.review is not None):
            raise ValueError("Only a review milestone must contain review")
        has_report = self.report_markdown is not None or self.report_markdowns is not None
        if (self.kind == "organization") != has_report:
            raise ValueError(
                "Only an organization milestone must contain report_markdown or report_markdowns"
            )
        if self.report_markdown is not None and self.report_markdowns is not None:
            raise ValueError("Use either report_markdown or report_markdowns, not both")
        if self.report_markdowns is not None and set(self.report_markdowns) != {"zh", "en"}:
            raise ValueError(
                "report_markdowns requires complete Chinese (zh) and English (en) reports"
            )
        reports = (
            [self.report_markdown]
            if self.report_markdown is not None
            else (self.report_markdowns or {}).values()
        )
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
