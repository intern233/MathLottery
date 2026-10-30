"""Local report generation and artifact export commands."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from mathlottery.cli.common import ReportLanguage, friendly, resources
from mathlottery.models import Workflow
from mathlottery.runtime.orchestrator import Orchestrator
from mathlottery.storage.core import json_text
from mathlottery.telemetry.reporting import report as generate_report


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


@friendly
def export(
    ctx: typer.Context,
    run_id: str,
    format: Annotated[str, typer.Option()] = "markdown",
    output: Annotated[Path | None, typer.Option(help="New destination file; no overwrite")] = None,
    language: Annotated[
        ReportLanguage | None, typer.Option(help="Organized Markdown/PDF language: zh or en")
    ] = None,
):
    """Export Markdown, JSON, or an organized PDF/materials bundle without model calls."""
    store, _ = resources(ctx)
    task = store.load(run_id)
    if format not in {"markdown", "json", "pdf", "bundle", "public_bundle"}:
        raise ValueError("--format must be markdown, json, pdf, bundle or public_bundle")
    selected = language.value if language is not None else None
    if selected is not None and (
        task.workflow != Workflow.ORGANIZE or format in {"json", "bundle", "public_bundle"}
    ):
        raise ValueError(
            "--language applies only to organized Markdown/PDF exports; bundles include both languages"
        )
    if format in {"bundle", "public_bundle"}:
        from mathlottery.organize.downloads import read_report

        if output is None:
            raise ValueError(f"--format {format} requires --output <new-report.zip>")
        content = read_report(store, run_id, format)
        with output.open("xb") as stream:
            stream.write(content)
        typer.echo(str(output.resolve()))
        return
    if format == "pdf":
        from mathlottery.organize.downloads import read_report
        from mathlottery.organize.workflow import report_documents, report_filename

        if selected is not None and selected not in report_documents(task):
            raise ValueError("This saved task does not contain the requested report language")
        task = Orchestrator(store).export_organized(run_id)
        content = read_report(store, run_id, "pdf", language=selected)
        if output:
            with output.open("xb") as stream:
                stream.write(content)
            typer.echo(str(output.resolve()))
        else:
            filename = (
                report_filename(task, selected, "pdf") if selected is not None else "report.pdf"
            )
            typer.echo(str(store.run_dir(run_id) / "organized" / filename))
        return
    if format == "markdown" and task.workflow == Workflow.ORGANIZE:
        from mathlottery.organize.downloads import read_report

        content = read_report(store, run_id, "markdown", language=selected).decode("utf-8")
    else:
        content = (
            generate_report(store, task).read_text() if format == "markdown" else json_text(task)
        )
    if output:
        with output.open("x") as stream:
            stream.write(content)
        typer.echo(str(output.resolve()))
    else:
        typer.echo(content)
