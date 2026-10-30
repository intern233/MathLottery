"""Solve allocation contracts and bounded, conversation-preserving selection.

The supervisor proposes an allocation; these deterministic rules enforce it.
"""

from __future__ import annotations

import re

from pydantic import Field, model_validator

from mathlottery.models import Model, Phase, SolveGroup, SolveWorker, Workflow


class Allocation(Model):
    run_id: str
    task_id: str
    rationale: str = Field(min_length=1, max_length=10000)
    groups: list[SolveGroup] = Field(min_length=1, max_length=32)

    @model_validator(mode="after")
    def unique_groups(self):
        if len({group.id for group in self.groups}) != len(self.groups):
            raise ValueError("Group IDs must be unique")
        return self


def enabled(run, config):
    return (
        run.workflow == Workflow.SOLVE
        and run.phase == Phase.SOLVE
        and run.execution == "native"
        and run.mode in {"codex", "work", "chat"}
        and (config.solve.parallel_agents or 1) > 1
        and run.native.finalization.status != "running"
    )


def parse_allocation(text, *, run_id, task_id, settings):
    """Validate one plan against both the current turn and the user's ceilings."""
    blocks = re.findall(r"(?ms)^```solve-plan\s*\n(.*?)^```\s*$", text)
    if len(blocks) != 1 or len(blocks[0].encode()) > 100_000:
        raise ValueError("Expected one bounded solve-plan block")
    plan = Allocation.model_validate_json(blocks[0])
    if (plan.run_id, plan.task_id) != (run_id, task_id):
        raise ValueError("Allocation IDs do not match this supervision turn")
    if sum(g.agents for g in plan.groups) > (settings.parallel_agents or 1):
        raise ValueError("Allocation exceeds the user's Solve parallelism cap")
    if len(plan.groups) > settings.group_limit:
        raise ValueError("Allocation exceeds the user's maximum research groups")
    return plan


def selected_workers(run, config, slots):
    """Clamp a saved plan to current budgets while retaining inactive conversations."""
    team = run.native.solve_team
    groups = team.groups or [SolveGroup(
        id="research", agents=len(config.solve.agent_slots) or 1, objective=run.problem.statement,
    )]
    selected = []
    # A resumed run may lower the cap even if supervision times out or returns
    # an invalid plan. Saved inactive conversations are kept, never launched.
    for group in groups[: config.solve.group_limit]:
        for index in range(group.agents):
            if len(selected) >= min(config.solve.parallel_agents or 1, slots):
                break
            slot = config.solve.agent_slots[len(selected)] if config.solve.agent_slots else None
            identifier = (
                "primary" if not selected else f"slot-{slot.id}" if slot else f"{group.id}-{index + 1}"
            )
            # Preserve every conversation even when a group is temporarily inactive.
            worker = team.workers.get(identifier) or SolveWorker(
                id=identifier,
                group=group.id,
                mode=group.mode,
                objective=group.objective,
                slot_id=slot.id if slot else None,
                session_id=run.native.solver_session_id if identifier == "primary" else None,
                response_id=run.native.solver_response_id if identifier == "primary" else None,
            )
            if worker.slot_id != (slot.id if slot else None):
                raise ValueError("A Solve conversation cannot be reassigned to another agent slot")
            worker.group, worker.mode, worker.objective = group.id, group.mode, group.objective
            if identifier == "primary":
                # A user may have continued in single-agent mode in between rounds.
                worker.session_id = run.native.solver_session_id
                worker.response_id = run.native.solver_response_id
            team.workers[identifier] = worker
            selected.append(worker)
    return selected
