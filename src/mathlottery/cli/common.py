"""Shared CLI options, workspace loading, and research presentation."""

from __future__ import annotations

import functools
from enum import StrEnum
from typing import Annotated

import typer

from mathlottery.config import ChatConfig, duration_minutes, load_config
from mathlottery.models import Problem, Run, State, Workflow, digest
from mathlottery.providers.network import apply_network_environment
from mathlottery.runtime.orchestrator import Orchestrator
from mathlottery.storage.core import Store


class Mode(StrEnum):
    chat = "chat"
    codex = "codex"
    manual = "manual"
    work = "work"


class Execution(StrEnum):
    native = "native"
    structured = "structured"


class ReasoningMode(StrEnum):
    standard = "standard"
    pro = "pro"


class ReportLanguage(StrEnum):
    en = "en"
    zh = "zh"


BackendOption = Annotated[
    Mode | None,
    typer.Option(
        "--backend",
        "--mode",
        help="Agent transport: codex or chat; manual/work are compatibility options",
    ),
]


ModelOption = Annotated[str | None, typer.Option(help="Agent model (required for Chat API)")]


EffortOption = Annotated[
    str | None, typer.Option(help="Reasoning effort supported by the selected model")
]


ReasoningModeOption = Annotated[
    ReasoningMode | None,
    typer.Option(help="Chat API reasoning mode; independent of reasoning effort"),
]


TimeOption = Annotated[str | None, typer.Option(help="Total active time, e.g. 3h or 60s")]


RoundsOption = Annotated[int | None, typer.Option(min=1)]


def friendly(function):
    @functools.wraps(function)
    def wrapped(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except (ValueError, OSError) as error:
            typer.echo(f"Error: {error}", err=True)
            raise typer.Exit(2) from error

    return wrapped


def resources(ctx):
    root = ctx.obj["root"]
    apply_network_environment(root)
    return Store(root), load_config(root, ctx.obj["config"])


def show_run(store: Store, run: Run):
    typer.echo(
        f"Run: {run.id}\nWorkflow: {run.workflow}\nBackend: {run.mode}\nExecution: {run.execution}\n"
        f"State: {run.state}\nPhase: {run.phase}\nRounds: {run.iteration}"
    )
    typer.echo(f"Report: {store.run_dir(run.id) / 'report.md'}")
    if run.state == State.WAITING_FOR_USER:
        typer.echo(f"Prompt: {store.run_dir(run.id) / run.prompt_path}")
        if run.execution == "native":
            typer.echo("Copy the prompt into ChatGPT; save its ordinary Markdown answer, then run:")
            typer.echo(f"  mathlottery submit --run {run.id} --file response.md")
        else:
            typer.echo("Copy the prompt into ChatGPT. Save its JSON response, then run:")
            typer.echo(f"  mathlottery submit --run {run.id} --file response.json")
    if run.execution == "native":
        typer.echo(f"Workspace: {store.run_dir(run.id) / 'workspace'}")
        if run.native.solver_session_id:
            typer.echo(f"Codex research session: {run.native.solver_session_id}")
        if run.native.reviewer_session_id:
            typer.echo(f"Codex review session: {run.native.reviewer_session_id}")
        if run.native.solver_response_id:
            typer.echo(f"Chat research response: {run.native.solver_response_id}")
        if run.native.reviewer_response_id:
            typer.echo(f"Chat review response: {run.native.reviewer_response_id}")
    for number, problem in enumerate(run.shortlist, 1):
        typer.echo(f"{number}. {problem.id} [{problem.status}] {problem.title}")
        typer.echo(
            f"   Difficulty: {problem.difficulty_estimate}; Verification: {problem.verification_feasibility}; Lean: {problem.lean_feasibility}"
        )
    if run.shortlist:
        typer.echo(f"Selection: {store.run_dir(run.id) / 'literature/selection.json'}")
        if run.workflow == Workflow.FIND:
            typer.echo(
                f"Choose a problem: mathlottery solve --from-find {run.id} --problem <problem-id>"
            )
    if run.stop_reason:
        typer.echo(f"Reason: {run.stop_reason}")
    if run.last_error:
        typer.echo(f"Error: {run.last_error}")


def apply_options(config, mode, budget_time, max_iterations):
    if mode:
        if config.backend.provider and mode.value != config.backend.mode:
            if config.backend.provider in config.model_providers:
                config.backend.chat = ChatConfig()
            config.backend.provider = None
            config.backend.model = None
            config.backend.reasoning_effort = None
            config.backend.chat.reasoning_mode = None
        config.backend.mode = mode.value
    if budget_time:
        config.budget.max_wall_time_minutes = duration_minutes(budget_time)
    if max_iterations is not None:
        config.budget.max_iterations = max_iterations


def research_options(
    config, mode, model, reasoning_effort, budget_time, max_iterations, *, reasoning_mode=None
):
    apply_options(config, mode, budget_time, max_iterations)
    if model:
        config.backend.model = model
    if reasoning_effort:
        config.backend.reasoning_effort = reasoning_effort
    if reasoning_mode is not None:
        if config.backend.mode != "chat":
            raise ValueError(
                "--reasoning-mode requires --backend chat; Codex uses --reasoning-effort"
            )
        config.backend.chat.reasoning_mode = reasoning_mode.value


def research_problem(store, problem, prompt):
    if prompt is not None and problem != "auto":
        raise ValueError("Use --prompt or --problem, not both")
    if prompt is not None:
        if not prompt.strip():
            raise ValueError("Research prompt cannot be empty")
        return store.save_problem(
            Problem(
                id=f"prompt-{digest(prompt)[:12]}",
                title=prompt[:100],
                statement=prompt,
            )
        )
    return None if problem == "auto" else store.load_problem(problem)


def start_task(store, config, *, task=None, review_source=None, **kwargs):
    engine = Orchestrator(store)
    task = task or engine.create(config, **kwargs)
    if review_source is not None:
        task.review_source = review_source
        store.save(task, "review_source_linked")
    typer.echo(
        f"Starting {task.id} ({task.workflow}, {task.mode}); artifacts: {store.run_dir(task.id)}"
    )
    result = engine.drive(task.id)
    show_run(store, result)
    if result.organization_report is not None:
        from mathlottery.organize.workflow import report_documents, report_filename

        documents = report_documents(result)
        for language, document in documents.items():
            root = store.run_dir(result.id) / "organized"
            typer.echo(
                f"Expert report ({language}): {root / report_filename(result, language, 'md')}"
            )
            if document.pdf_status == "ready":
                typer.echo(f"PDF ({language}): {root / report_filename(result, language, 'pdf')}")
            else:
                typer.echo(f"{language}: {document.pdf_error or 'PDF export is pending.'}")
        if any(document.pdf_status != "ready" for document in documents.values()):
            typer.echo(f"Retry locally: mathlottery export {result.id} --format pdf")
    if result.state in {State.FAILED, State.RATE_LIMITED}:
        raise typer.Exit(1)
