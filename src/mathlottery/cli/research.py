"""Find, Solve, and composed pipeline commands."""

from __future__ import annotations

from typing import Annotated

import typer

from mathlottery.cli.common import (
    BackendOption,
    EffortOption,
    Execution,
    ModelOption,
    ReasoningModeOption,
    RoundsOption,
    TimeOption,
    friendly,
    research_options,
    research_problem,
    resources,
    start_task,
)
from mathlottery.models import Workflow
from mathlottery.runtime.orchestrator import Orchestrator


@friendly
def run(
    ctx: typer.Context,
    mode: BackendOption = None,
    execution: Annotated[
        Execution | None, typer.Option(help="Native research or legacy structured protocol")
    ] = None,
    prompt: Annotated[
        str | None, typer.Option(help="Direct research request, in your own words")
    ] = None,
    model: ModelOption = None,
    reasoning_effort: EffortOption = None,
    reasoning_mode: ReasoningModeOption = None,
    problem: Annotated[str, typer.Option()] = "auto",
    source: Annotated[str | None, typer.Option(help="Preferred source URL for discovery")] = None,
    budget_time: Annotated[
        str | None, typer.Option(help="Active wall time, e.g. 3h or 60s")
    ] = None,
    max_iterations: Annotated[int | None, typer.Option(min=1)] = None,
):
    """Run the full find → solve → verify pipeline using the selected agent backend."""
    store, config = resources(ctx)
    research_options(
        config,
        mode,
        model,
        reasoning_effort,
        budget_time,
        max_iterations,
        reasoning_mode=reasoning_mode,
    )
    if execution:
        config.backend.execution = execution.value
    start_task(store, config, problem=research_problem(store, problem, prompt), source=source)


@friendly
def find(
    ctx: typer.Context,
    query: Annotated[
        str | None,
        typer.Option("--query", "--prompt", help="Selection criteria or mathematical field"),
    ] = None,
    source: Annotated[
        str | None, typer.Option(help="Preferred public problem list or source")
    ] = None,
    count: Annotated[int, typer.Option(min=1, max=50, help="Target shortlist size")] = 5,
    mode: BackendOption = None,
    model: ModelOption = None,
    reasoning_effort: EffortOption = None,
    reasoning_mode: ReasoningModeOption = None,
    budget_time: TimeOption = None,
    max_iterations: RoundsOption = None,
):
    """Find and rank public problems with status evidence; stop before solving."""
    store, config = resources(ctx)
    research_options(
        config,
        mode,
        model,
        reasoning_effort,
        budget_time,
        max_iterations,
        reasoning_mode=reasoning_mode,
    )
    start_task(
        store,
        config,
        workflow=Workflow.FIND,
        source=source,
        discovery_request=query,
        discovery_count=count,
    )


@friendly
def solve(
    ctx: typer.Context,
    problem: Annotated[str, typer.Option(help="Imported or discovered problem ID")] = "auto",
    prompt: Annotated[str | None, typer.Option(help="Direct mathematical research request")] = None,
    from_find: Annotated[
        str | None,
        typer.Option(help="Find run whose selected problem and research dossier to carry forward"),
    ] = None,
    mode: BackendOption = None,
    model: ModelOption = None,
    reasoning_effort: EffortOption = None,
    reasoning_mode: ReasoningModeOption = None,
    budget_time: TimeOption = None,
    max_iterations: RoundsOption = None,
    parallel_agents: Annotated[
        int | None,
        typer.Option(
            min=1,
            max=32,
            help="Maximum concurrent Solve researchers; supervision is separate overhead",
        ),
    ] = None,
    max_groups: Annotated[
        int | None,
        typer.Option(
            min=1,
            max=32,
            help="Maximum active Solve research groups; requires a configured researcher parallelism cap",
        ),
    ] = None,
):
    """Explore a supplied problem and save candidate proofs for separate verification."""
    store, config = resources(ctx)
    research_options(
        config,
        mode,
        model,
        reasoning_effort,
        budget_time,
        max_iterations,
        reasoning_mode=reasoning_mode,
    )
    if parallel_agents is not None:
        config.solve.parallel_agents = parallel_agents
    if max_groups is not None:
        config.solve.max_groups = max_groups
    if from_find:
        if prompt is not None or problem == "auto":
            raise ValueError("Use --from-find with an explicit --problem from its shortlist")
        task = Orchestrator(store).solve_discovered(config, from_find, problem)
        start_task(store, config, task=task)
    else:
        start_task(
            store, config, workflow=Workflow.SOLVE, problem=research_problem(store, problem, prompt)
        )
