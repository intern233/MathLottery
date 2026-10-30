"""Independent verification and editorial organization commands."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from mathlottery.cli.common import (
    BackendOption,
    EffortOption,
    ModelOption,
    ReasoningModeOption,
    ReportLanguage,
    RoundsOption,
    TimeOption,
    friendly,
    research_options,
    resources,
    start_task,
)
from mathlottery.models import (
    Candidate,
    CandidateInput,
    LiteratureSearch,
    Problem,
    ReviewProvenance,
    Workflow,
    digest,
    uid,
)
from mathlottery.runtime.orchestrator import Orchestrator
from mathlottery.verify.obstacles import carry_literature


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
        config,
        mode,
        model,
        reasoning_effort,
        budget_time,
        max_iterations,
        reasoning_mode=reasoning_mode,
    )
    if sum(value is not None for value in (proof, candidate, from_run)) != 1:
        raise ValueError("Supply exactly one of --proof, --candidate or --from-run")
    problem_object = store.load_problem(problem) if problem else None
    content, provenance = None, None
    prior_literature = []
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
        if isinstance(parsed, Candidate):
            prior_literature = [review.literature_search for review in parsed.reviews]
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
            prior_literature = original.review_literature + [
                review.literature_search for review in checked.reviews
            ]
            content = CandidateInput(
                **{key: getattr(checked, key) for key in CandidateInput.model_fields}
            )
            provenance = ReviewProvenance(
                source_run_id=original.id,
                source_candidate_id=checked.id,
                candidate_sha256=checked.sha256,
            )
            problem_object = problem_object or original.problem
    if not problem_object:
        problem_object = Problem(
            id=uid("claim"), title=content.claim[:100], statement=content.claim
        )
    start_task(
        store,
        config,
        workflow=Workflow.VERIFY,
        problem=problem_object,
        candidate=content,
        review_source=provenance,
        review_literature=[
            LiteratureSearch.model_validate(
                carry_literature(LiteratureSearch(), prior_literature).model_dump()
            )
        ]
        if prior_literature
        else [],
    )


@friendly
def organize(
    ctx: typer.Context,
    from_run: Annotated[str, typer.Option(help="Reviewed source task to explain and collect")],
    language: Annotated[
        ReportLanguage,
        typer.Option(help="Default export language; both Chinese and English are produced"),
    ] = ReportLanguage.zh,
    instructions: Annotated[
        str | None, typer.Option(help="Audience, emphasis or editorial requirements")
    ] = None,
    mode: BackendOption = None,
    model: ModelOption = None,
    reasoning_effort: EffortOption = None,
    reasoning_mode: ReasoningModeOption = None,
    budget_time: TimeOption = None,
    max_iterations: RoundsOption = None,
):
    """Organize reviewed research into Chinese and English expert-readable Markdown/PDF reports."""
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
    task = Orchestrator(store).organize(
        config, from_run, language=language.value, instructions=instructions
    )
    start_task(store, config, task=task)
