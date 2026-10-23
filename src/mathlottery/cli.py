from __future__ import annotations

import functools
import json
import shutil
import tempfile
from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer
import yaml

from mathlottery.backends import WorkBackend
from mathlottery.chat_backend import ChatBackend
from mathlottery.config import ChatConfig, Config, duration_minutes, load_config
from mathlottery.demo import DemoBackend, demo_problem
from mathlottery.execution import python_exec
from mathlottery.local_network import apply_network_environment
from mathlottery.models import (
    Candidate,
    CandidateInput,
    Problem,
    Reference,
    ReviewProvenance,
    Run,
    State,
    Workflow,
    digest,
    uid,
)
from mathlottery.native_backend import NativeWorkBackend
from mathlottery.orchestrator import Orchestrator
from mathlottery.reporting import report as generate_report
from mathlottery.sources import WebTools
from mathlottery.storage import Store, atomic_write, json_text

app = typer.Typer(
    no_args_is_help=True,
    pretty_exceptions_enable=False,
    help="MathLottery · Token Is All You Need. Local mathematical research CLI.",
)


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


@app.callback()
def main(
    ctx: typer.Context,
    root: Annotated[Path, typer.Option(help="Project/workspace root")] = Path("."),
    config: Annotated[Path | None, typer.Option(help="Alternate YAML configuration")] = None,
):
    ctx.obj = {"root": root.resolve(), "config": config}


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
        typer.echo(f"   Difficulty: {problem.difficulty_estimate}; Verification: {problem.verification_feasibility}; Lean: {problem.lean_feasibility}")
    if run.shortlist:
        typer.echo(f"Selection: {store.run_dir(run.id) / 'literature/selection.json'}")
        if run.workflow == Workflow.FIND:
            typer.echo(f"Choose a problem: mathlottery solve --from-find {run.id} --problem <problem-id>")
    if run.stop_reason:
        typer.echo(f"Reason: {run.stop_reason}")
    if run.last_error:
        typer.echo(f"Error: {run.last_error}")


def diagnostics(store, config):
    try:
        backend = NativeWorkBackend if config.backend.execution == "native" else WorkBackend
        codex = backend(config.backend, store.root).check()
    except Exception as error:
        codex = {"available": False, "reason": str(error)}
    try:
        chat = ChatBackend(config.backend).check()
    except ValueError as error:
        chat = {"configured": False, "reason": str(error)}
    with tempfile.TemporaryDirectory(dir=store.internal) as temp:
        isolation = python_exec("print('isolation ready')", Path(temp), config.tools)
    return {
        "workspace": str(store.root),
        "database": str(store.db_path),
        "codex": codex,
        "chat": chat,
        "python_isolation": isolation["status"],
        "isolation_details": isolation["stderr"],
        "lean": shutil.which(config.tools.lean_command),
        "bubblewrap": shutil.which("bwrap"),
    }


@app.command()
@friendly
def serve(
    ctx: typer.Context,
    port: Annotated[int, typer.Option(min=1, max=65535, help="Preferred port; tries the next if busy")] = 8765,
    open_browser: Annotated[bool, typer.Option("--open", help="Open the local browser interface")] = False,
    loopback_only: Annotated[bool, typer.Option(help="Keep the default loopback-only binding")] = False,
    wsl_direct: Annotated[bool, typer.Option(help="Explicitly allow direct WSL IP access from its Windows host")] = False,
):
    """Open a local browser workspace for find, solve and verify."""
    from mathlottery.web.server import serve as serve_web
    from mathlottery.web.startup import resolve_workspace

    source = ctx.find_root().get_parameter_source("root")
    root = resolve_workspace(ctx.obj["root"], explicit=source is not None and source.name != "DEFAULT")
    serve_web(root, ctx.obj["config"], port, open_browser, loopback_only, wsl_direct)


@app.command()
@friendly
def init(ctx: typer.Context):
    """Initialize local storage/configuration and check installed tools; no API key required."""
    store, config = resources(ctx)
    result = diagnostics(store, config)
    # Resolve executables for this invocation without persisting machine-specific paths.
    path = store.root / "config.yaml"
    if not path.exists():
        atomic_write(path, yaml.safe_dump(config.model_dump(mode="json"), sort_keys=False))
    typer.echo(json_text(result))


@app.command()
@friendly
def doctor(ctx: typer.Context):
    """Check backend authentication and optional mathematical tools."""
    store, config = resources(ctx)
    typer.echo(json_text(diagnostics(store, config)))


@app.command()
@friendly
def add(
    ctx: typer.Context,
    file: Annotated[Path | None, typer.Option(help="Problem JSON or Markdown file")] = None,
    url: Annotated[str | None, typer.Option(help="Public problem page")] = None,
    statement: Annotated[str | None, typer.Option()] = None,
    title: Annotated[str | None, typer.Option()] = None,
    problem_id: Annotated[str | None, typer.Option("--id")] = None,
    formal_target: Annotated[str | None, typer.Option(help="User-pinned Lean proposition")] = None,
):
    """Import a user problem, source URL, or a local problem file."""
    store, config = resources(ctx)
    if sum(value is not None for value in (file, url, statement)) != 1:
        raise ValueError("Supply exactly one of --file, --url or --statement")
    if file:
        if file.stat().st_size > 500000:
            raise ValueError("Problem file exceeds 500 KB")
        text = file.read_text()
        if file.suffix == ".json":
            problem = Problem.model_validate_json(text)
        else:
            problem = Problem(
                id=problem_id or f"manual-{digest(text)[:12]}",
                title=title or text.splitlines()[0].lstrip("# ") or file.stem,
                statement=text,
            )
    elif url:
        result = WebTools(store.internal / "imports", config.tools).fetch(url)
        problem = (
            Problem.model_validate(result["problem"])
            if result.get("problem")
            else Problem(
                id=problem_id or f"source-{digest(url)[:12]}",
                title=title or result["title"],
                statement=result["text"],
                source_url=result["url"],
            )
        )
        problem.references = [
            Reference(
                url=result["url"],
                title=result["title"],
                retrieved_at=result["retrieved_at"],
                artifact=str(store.internal / "imports" / result["artifact"]),
                sha256=result["sha256"],
                source="web_fetch",
            )
        ]
    else:
        problem = Problem(
            id=problem_id or uid("manual"),
            title=title or "User-supplied problem",
            statement=statement,
        )
    if problem_id:
        problem.id = problem_id
    if formal_target:
        problem.formal_target = formal_target
    problem = store.save_problem(problem)
    typer.echo(
        f"Problem: {problem.id}\nFile: {store.root / 'problems' / problem.id / 'problem.json'}"
    )


@app.command()
@friendly
def problems(ctx: typer.Context):
    """List imported mathematical problems."""
    store, _ = resources(ctx)
    for problem in store.list_problems():
        typer.echo(f"{problem.id}\t{problem.status}\t{problem.title}")


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
            raise ValueError("--reasoning-mode requires --backend chat; Codex uses --reasoning-effort")
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
        typer.echo(f"Expert report: {store.run_dir(result.id) / 'organized/report.md'}")
        if result.organization_report.pdf_status == "ready":
            typer.echo(f"PDF: {store.run_dir(result.id) / 'organized/report.pdf'}")
        else:
            typer.echo(result.organization_report.pdf_error or "PDF export is pending.")
            typer.echo(f"Retry locally: mathlottery export {result.id} --format pdf")
    if result.state in {State.FAILED, State.RATE_LIMITED}:
        raise typer.Exit(1)


@app.command()
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
        config, mode, model, reasoning_effort, budget_time, max_iterations,
        reasoning_mode=reasoning_mode,
    )
    if execution:
        config.backend.execution = execution.value
    start_task(store, config, problem=research_problem(store, problem, prompt), source=source)


@app.command()
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
        config, mode, model, reasoning_effort, budget_time, max_iterations,
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


@app.command()
@friendly
def solve(
    ctx: typer.Context,
    problem: Annotated[str, typer.Option(help="Imported or discovered problem ID")] = "auto",
    prompt: Annotated[str | None, typer.Option(help="Direct mathematical research request")] = None,
    from_find: Annotated[str | None, typer.Option(help="Find run whose selected problem and research dossier to carry forward")] = None,
    mode: BackendOption = None,
    model: ModelOption = None,
    reasoning_effort: EffortOption = None,
    reasoning_mode: ReasoningModeOption = None,
    budget_time: TimeOption = None,
    max_iterations: RoundsOption = None,
):
    """Explore a supplied problem and save candidate proofs for separate verification."""
    store, config = resources(ctx)
    research_options(
        config, mode, model, reasoning_effort, budget_time, max_iterations,
        reasoning_mode=reasoning_mode,
    )
    if from_find:
        if prompt is not None or problem == "auto":
            raise ValueError("Use --from-find with an explicit --problem from its shortlist")
        task = Orchestrator(store).solve_discovered(config, from_find, problem)
        start_task(store, config, task=task)
    else:
        start_task(store, config, workflow=Workflow.SOLVE, problem=research_problem(store, problem, prompt))


@app.command()
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


@app.command()
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


@app.command()
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
    message: Annotated[
        str | None, typer.Option(help="Additional direction for the native research session")
    ] = None,
):
    """Resume a checkpoint. Budget overrides are new total limits, not added allowances."""
    store, _ = resources(ctx)
    task = store.load(run_id)
    config = Config.model_validate(task.config)
    research_options(
        config, mode, model, reasoning_effort, budget_time, max_iterations,
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


@app.command()
@friendly
def verify(
    ctx: typer.Context,
    problem: Annotated[str | None, typer.Option()] = None,
    proof: Annotated[Path | None, typer.Option(exists=True, dir_okay=False)] = None,
    candidate: Annotated[
        Path | None, typer.Option(exists=True, dir_okay=False, help="Candidate JSON file")
    ] = None,
    from_run: Annotated[
        str | None, typer.Option(help="Audit the latest candidate from this run")
    ] = None,
    mode: BackendOption = None,
    model: ModelOption = None,
    reasoning_effort: EffortOption = None,
    reasoning_mode: ReasoningModeOption = None,
    budget_time: TimeOption = None,
    max_iterations: RoundsOption = None,
):
    """Independently verify a proof or saved candidate; return the verdict without solving."""
    store, config = resources(ctx)
    research_options(
        config, mode, model, reasoning_effort, budget_time, max_iterations,
        reasoning_mode=reasoning_mode,
    )
    if sum(value is not None for value in (proof, candidate, from_run)) != 1:
        raise ValueError("Supply exactly one of --proof, --candidate or --from-run")
    problem_object = store.load_problem(problem) if problem else None
    content, provenance = None, None
    if proof:
        if not problem_object:
            raise ValueError("--proof requires --problem")
        if proof.stat().st_size > 100000:
            raise ValueError("Proof exceeds 100 KB")
        content = CandidateInput(claim=problem_object.statement, proof=proof.read_text())
    elif candidate:
        if candidate.stat().st_size > 2_000_000:
            raise ValueError("Candidate exceeds 2 MB")
        data = json.loads(candidate.read_text())
        parsed = (
            Candidate.model_validate(data)
            if "sha256" in data
            else CandidateInput.model_validate(data)
        )
        if isinstance(parsed, Candidate) and parsed.sha256 != digest(
            parsed.claim + "\n" + parsed.proof
        ):
            raise ValueError("Candidate checksum does not match its claim and proof")
        content = CandidateInput(
            **{key: getattr(parsed, key) for key in CandidateInput.model_fields}
        )
    else:
        with store.lock(from_run):
            original = store.load(from_run)
            if not original.candidates:
                raise ValueError("The source run has no candidate to verify")
            Orchestrator(store)._check_candidate_file(original)
            checked = original.candidates[-1]
            content = CandidateInput(
                **{key: getattr(checked, key) for key in CandidateInput.model_fields}
            )
            provenance = ReviewProvenance(source_run_id=original.id, source_candidate_id=checked.id,
                                          candidate_sha256=checked.sha256)
            problem_object = problem_object or original.problem
    if not problem_object:
        problem_object = Problem(
            id=uid("claim"), title=content.claim[:100], statement=content.claim
        )
    start_task(store, config, workflow=Workflow.VERIFY, problem=problem_object, candidate=content,
               review_source=provenance)


@app.command()
@friendly
def organize(
    ctx: typer.Context,
    from_run: Annotated[str, typer.Option(help="Reviewed source task to explain and collect")],
    language: Annotated[ReportLanguage, typer.Option(help="Report language")] = ReportLanguage.zh,
    instructions: Annotated[str | None, typer.Option(help="Audience, emphasis or editorial requirements")] = None,
    mode: BackendOption = None,
    model: ModelOption = None,
    reasoning_effort: EffortOption = None,
    reasoning_mode: ReasoningModeOption = None,
    budget_time: TimeOption = None,
    max_iterations: RoundsOption = None,
):
    """Organize reviewed research into an expert-readable Markdown/PDF report."""
    store, config = resources(ctx)
    research_options(config, mode, model, reasoning_effort, budget_time, max_iterations,
                     reasoning_mode=reasoning_mode)
    task = Orchestrator(store).organize(config, from_run, language=language.value,
                                        instructions=instructions)
    start_task(store, config, task=task)


@app.command()
@friendly
def report(
    ctx: typer.Context,
    run_id: str,
    show: Annotated[bool, typer.Option(help="Print Markdown to the terminal")] = False,
):
    """Generate the current research report."""
    store, _ = resources(ctx)
    path = generate_report(store, store.load(run_id))
    typer.echo(path.read_text() if show else str(path))


@app.command()
@friendly
def export(
    ctx: typer.Context,
    run_id: str,
    format: Annotated[str, typer.Option()] = "markdown",
    output: Annotated[Path | None, typer.Option(help="New destination file; no overwrite")] = None,
):
    """Export Markdown, JSON, or an organized PDF/materials bundle without model calls."""
    store, _ = resources(ctx)
    task = store.load(run_id)
    if format not in {"markdown", "json", "pdf", "bundle"}:
        raise ValueError("--format must be markdown, json, pdf or bundle")
    if format == "bundle":
        from mathlottery.organized_reports import read_report

        if output is None:
            raise ValueError("--format bundle requires --output <new-report.zip>")
        content = read_report(store, run_id, "bundle")
        with output.open("xb") as stream:
            stream.write(content)
        typer.echo(str(output.resolve()))
        return
    if format == "pdf":
        from mathlottery.organized_reports import read_report

        task = Orchestrator(store).export_organized(run_id)
        content = read_report(store, run_id, "pdf")
        if output:
            with output.open("xb") as stream:
                stream.write(content)
            typer.echo(str(output.resolve()))
        else:
            typer.echo(str(store.run_dir(run_id) / "organized/report.pdf"))
        return
    if format == "markdown" and task.workflow == Workflow.ORGANIZE:
        from mathlottery.organized_reports import read_report

        content = read_report(store, run_id, "markdown").decode("utf-8")
    else:
        content = generate_report(store, task).read_text() if format == "markdown" else json_text(task)
    if output:
        with output.open("x") as stream:
            stream.write(content)
        typer.echo(str(output.resolve()))
    else:
        typer.echo(content)


@app.command()
@friendly
def stop(ctx: typer.Context, run_id: str):
    """Request a graceful stop, preserving the checkpoint and report."""
    store, _ = resources(ctx)
    show_run(store, Orchestrator(store).stop(run_id))


@app.command()
@friendly
def demo(
    ctx: typer.Context,
    case: Annotated[
        str, typer.Option(help="correct / incorrect / hidden-assumption / finite-only")
    ] = "correct",
):
    """Run an offline educational demo with scripted responses and real isolated Python tools."""
    store, config = resources(ctx)
    problem = store.save_problem(demo_problem(case))
    config.budget.max_iterations = 10
    config.budget.max_input_tokens = config.budget.max_output_tokens = None
    engine = Orchestrator(store, DemoBackend(case))
    task = engine.create(config, problem, mode="demo")
    task.environment["demo_case"] = case
    store.save(
        task, "demo_label", description="Scripted backend; real local computations; no model quota"
    )
    show_run(store, engine.drive(task.id))
