"""Inspect, submit, resume, and stop existing tasks."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from mathlottery.cli.common import (
    BackendOption,
    EffortOption,
    ModelOption,
    ReasoningModeOption,
    friendly,
    research_options,
    resources,
    show_run,
)
from mathlottery.config import Config
from mathlottery.models import Workflow
from mathlottery.providers.demo import DemoBackend
from mathlottery.runtime.orchestrator import Orchestrator
from mathlottery.storage.core import json_text


@friendly
def submit(
    ctx: typer.Context,
    run_id: Annotated[str, typer.Option("--run")],
    file: Annotated[Path, typer.Option(exists=True, dir_okay=False)],
):
    """Compatibility only: submit an answer to an explicitly manual run."""
    store, _ = resources(ctx)
    if file.stat().st_size > 2_000_000:
        raise ValueError("Response exceeds 2 MB")
    show_run(store, Orchestrator(store).submit(run_id, file.read_text()))


@friendly
def status(
    ctx: typer.Context,
    run_id: Annotated[str | None, typer.Argument()] = None,
    as_json: Annotated[bool, typer.Option("--json")] = False,
):
    """Inspect a run or list all local runs."""
    store, _ = resources(ctx)
    if run_id:
        task = store.load(run_id)
        if as_json:
            typer.echo(json_text(task))
        else:
            show_run(store, task)
            typer.echo(
                f"Candidates: {len(task.candidates)}\n"
                f"Input tokens: {task.usage.input_tokens if task.usage.input_tokens is not None else 'unknown'}\n"
                f"Output tokens: {task.usage.output_tokens if task.usage.output_tokens is not None else 'unknown'}"
            )
    else:
        for task in store.list_runs():
            typer.echo(f"{task.id}\t{task.mode}\t{task.state}\t{task.phase}\t{task.iteration}")


@friendly
def resume(
    ctx: typer.Context,
    run_id: str,
    mode: BackendOption = None,
    model: ModelOption = None,
    reasoning_effort: EffortOption = None,
    reasoning_mode: ReasoningModeOption = None,
    budget_time: Annotated[str | None, typer.Option()] = None,
    max_iterations: Annotated[int | None, typer.Option(min=1)] = None,
    parallel_agents: Annotated[
        int | None, typer.Option(min=1, max=32, help="New Solve researcher concurrency cap")
    ] = None,
    max_groups: Annotated[
        int | None, typer.Option(min=1, max=32, help="New maximum active Solve research groups")
    ] = None,
    message: Annotated[
        str | None, typer.Option(help="Additional direction for the native research session")
    ] = None,
):
    """Resume a checkpoint. Budget overrides are new total limits, not added allowances."""
    store, _ = resources(ctx)
    task = store.load(run_id)
    config = Config.model_validate(task.config)
    if task.workflow != Workflow.SOLVE and (parallel_agents is not None or max_groups is not None):
        raise ValueError("Research parallelism and group limits apply only to Solve")
    if parallel_agents is not None:
        config.solve.parallel_agents = parallel_agents
    if max_groups is not None:
        config.solve.max_groups = max_groups
    research_options(
        config,
        mode,
        model,
        reasoning_effort,
        budget_time,
        max_iterations,
        reasoning_mode=reasoning_mode,
    )
    backend = (
        DemoBackend(task.environment.get("demo_case", "correct"))
        if task.mode == "demo" and not mode
        else None
    )
    show_run(
        store,
        Orchestrator(store, backend).resume(
            run_id,
            mode.value if mode else None,
            config,
            message=message,
        ),
    )


@friendly
def stop(ctx: typer.Context, run_id: str):
    """Request a graceful stop, preserving the checkpoint and report."""
    store, _ = resources(ctx)
    show_run(store, Orchestrator(store).stop(run_id))
