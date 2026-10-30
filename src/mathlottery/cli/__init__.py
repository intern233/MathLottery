"""Public CLI entry point; command implementations live in focused modules."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from mathlottery.cli.common import Execution, Mode, ReasoningMode, ReportLanguage, apply_options
from mathlottery.cli.exports import export, report
from mathlottery.cli.research import find, run, solve
from mathlottery.cli.review import organize, verify
from mathlottery.cli.tasks import resume, status, stop, submit
from mathlottery.cli.workspace import add, demo, doctor, init, problems, serve

__all__ = [
    "app",
    "serve",
    "init",
    "doctor",
    "add",
    "problems",
    "run",
    "find",
    "solve",
    "submit",
    "status",
    "resume",
    "verify",
    "organize",
    "report",
    "export",
    "stop",
    "demo",
    "Mode",
    "Execution",
    "ReasoningMode",
    "ReportLanguage",
    "apply_options",
]

app = typer.Typer(
    no_args_is_help=True,
    pretty_exceptions_enable=False,
    help="MathLottery · Token Is All You Need. Local mathematical research CLI.",
)


@app.callback()
def main(
    ctx: typer.Context,
    root: Annotated[Path, typer.Option(help="Project/workspace root")] = Path("."),
    config: Annotated[Path | None, typer.Option(help="Alternate YAML configuration")] = None,
):
    ctx.obj = {"root": root.resolve(), "config": config}


for command in (
    serve,
    init,
    doctor,
    add,
    problems,
    run,
    find,
    solve,
    submit,
    status,
    resume,
    verify,
    organize,
    report,
    export,
    stop,
    demo,
):
    app.command()(command)
