"""Contracts at research milestones; not a protocol for every agent action."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import Field, model_validator

from mathlottery.domain.common import Model
from mathlottery.domain.session import SolveGroup


class DerivationStep(Model):
    id: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,80}$")
    statement: str = Field(min_length=1, max_length=10000)
    justification: str = Field(min_length=1, max_length=20000)
    # Earlier step IDs; external results go in the message's depends_on/references.
    premises: list[str] = Field(default_factory=list, max_length=100)


class TheoremRecord(Model):
    statement: str = Field(min_length=1, max_length=30000)
    proof_steps: list[DerivationStep] = Field(min_length=1, max_length=100)
    conclusion_step: str
    references: list[str] = Field(default_factory=list, max_length=100)
    remaining_obligations: list[str] = Field(default_factory=list, max_length=100)

    @model_validator(mode="after")
    def ordered_derivation(self):
        seen = set()
        for step in self.proof_steps:
            if step.id in seen or not set(step.premises) <= seen:
                raise ValueError("Proof steps need unique IDs and only earlier premises")
            seen.add(step.id)
        if self.conclusion_step not in seen:
            raise ValueError("The conclusion must identify an existing proof step")
        return self


class ReviewCheck(Model):
    claim: str = Field(min_length=1, max_length=10000)
    reasoning: str = Field(min_length=1, max_length=20000)
    status: Literal["supported", "gap", "uncertain"]


class BoardReview(Model):
    key: str
    content_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    verdict: Literal["accepted", "rejected", "needs_work"]
    rationale: str = Field(min_length=1, max_length=20000)
    checked_steps: list[str] = Field(default_factory=list, max_length=100)
    addressed_objections: list[str] = Field(default_factory=list, max_length=100)


class SolutionReview(Model):
    candidate_id: str
    candidate_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    verdict: Literal["accepted", "rejected", "needs_work"]
    original_problem_coverage: Literal["full", "partial", "different", "uncertain"]
    rationale: str = Field(min_length=1, max_length=20000)
    checks: list[ReviewCheck] = Field(min_length=1, max_length=100)
    remaining_obligations: list[str] = Field(default_factory=list, max_length=100)
    depends_on: list[str] = Field(default_factory=list, max_length=100)

    @model_validator(mode="after")
    def acceptance_requires_checks(self):
        if self.verdict == "accepted" and (
            self.original_problem_coverage != "full" or self.remaining_obligations
            or any(check.status != "supported" for check in self.checks)
        ):
            raise ValueError("Accept only full original-problem coverage with no unresolved checks")
        return self


class Supervision(Model):
    run_id: str
    task_id: str
    rationale: str = Field(min_length=1, max_length=20000)
    groups: list[SolveGroup] = Field(default_factory=list, max_length=32)
    board_reviews: list[BoardReview] = Field(default_factory=list, max_length=100)
    solution_reviews: list[SolutionReview] = Field(default_factory=list, max_length=32)
    summary: str = Field(min_length=1, max_length=30000)


def parse_supervision(text, run, attempt, config):
    blocks = re.findall(r"(?ms)^```solve-supervision\s*\n(.*?)^```\s*$", text)
    if len(blocks) != 1 or len(blocks[0].encode()) > 500_000:
        raise ValueError("Return one solve-supervision block of at most 500 KB")
    value = Supervision.model_validate_json(blocks[0])
    if (value.run_id, value.task_id) != (run.id, attempt["task_id"]):
        raise ValueError("Supervision IDs do not match the current turn")
    if len({g.id for g in value.groups}) != len(value.groups):
        raise ValueError("Group IDs must be unique")
    if (len(value.groups) > config.solve.group_limit
            or sum(g.agents for g in value.groups) > (config.solve.parallel_agents or 1)):
        raise ValueError("Supervision exceeds the configured researcher/group limits")
    for field, key in ((value.board_reviews, "key"), (value.solution_reviews, "candidate_id")):
        if len({getattr(item, key) for item in field}) != len(field):
            raise ValueError("A supervision turn cannot contain conflicting duplicate reviews")
    return value
