"""Workspace setup, problem imports, diagnostics, and offline demonstrations."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import Annotated

import typer
import yaml

from mathlottery.cli.common import friendly, resources, show_run
from mathlottery.models import Problem, Reference, digest, uid
from mathlottery.providers.base import WorkBackend
from mathlottery.providers.chat import ChatBackend
from mathlottery.providers.codex import NativeWorkBackend
from mathlottery.providers.demo import DemoBackend, demo_problem
from mathlottery.providers.registry import isolate_credentials
from mathlottery.runtime.orchestrator import Orchestrator
from mathlottery.storage.core import atomic_write, json_text
from mathlottery.tooling.execution import python_exec
from mathlottery.tooling.sources import WebTools


def diagnostics(store, config):
    try:
        backend = NativeWorkBackend if config.backend.execution == "native" else WorkBackend
        codex = isolate_credentials(backend(config.backend, store.root), config, store.root).check()
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


@friendly
def serve(
    ctx: typer.Context,
    port: Annotated[
        int, typer.Option(min=1, max=65535, help="Preferred port; tries the next if busy")
    ] = 8765,
    open_browser: Annotated[
        bool, typer.Option("--open", help="Open the local browser interface")
    ] = False,
    loopback_only: Annotated[
        bool, typer.Option(help="Keep the default loopback-only binding")
    ] = False,
    wsl_direct: Annotated[
        bool, typer.Option(help="Explicitly allow direct WSL IP access from its Windows host")
    ] = False,
):
    """Open a local browser workspace for find, solve and verify."""
    from mathlottery.web.server import serve as serve_web
    from mathlottery.web.startup import resolve_workspace

    source = ctx.find_root().get_parameter_source("root")
    root = resolve_workspace(
        ctx.obj["root"], explicit=source is not None and source.name != "DEFAULT"
    )
    serve_web(root, ctx.obj["config"], port, open_browser, loopback_only, wsl_direct)


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


@friendly
def doctor(ctx: typer.Context):
    """Check backend authentication and optional mathematical tools."""
    store, config = resources(ctx)
    typer.echo(json_text(diagnostics(store, config)))


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


@friendly
def problems(ctx: typer.Context):
    """List imported mathematical problems."""
    store, _ = resources(ctx)
    for problem in store.list_problems():
        typer.echo(f"{problem.id}\t{problem.status}\t{problem.title}")


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
