"""The three mathematical tasks, independent of the agent transport."""

from mathlottery.models import NativeCheckpoint, Phase, Run, State, Workflow
from mathlottery.sources import conservative_status
from mathlottery.storage import Store, atomic_write, json_text

ACTIVE = {Phase.FIND: State.DISCOVERING, Phase.SOLVE: State.SOLVING, Phase.VERIFY: State.VERIFYING}


def task_instructions(run: Run) -> str:
    if run.phase == Phase.FIND:
        return (
            "Task: FIND worthwhile publicly stated mathematical problems. Search primary problem "
            "lists and original literature, check for later solutions and corrections, and compare "
            f"up to {run.discovery_count} promising problems. The user's selection criteria are:\n"
            + (
                run.discovery_request
                or "Prefer precise, tractable problems with checkable results."
            )
            + "\nPreferred source: "
            + (run.source or "Public problem lists and original papers")
            + "\nFor each problem record id, title, exact statement, source_url, field, status, "
            "status_evidence (URLs actually consulted), references, difficulty_estimate, "
            "verification_feasibility and selection_reason. Explain the ranking, existing partial "
            "results, and remaining uncertainty; ranking is not a probability of success. Do not "
            "infer OPEN merely from not finding a solution. Use UNKNOWN when evidence is lacking. "
            "Finish discovery with kind: selection, an ordered shortlist of Problem objects and "
            "problem equal to the recommended shortlist entry. Use progress while searching, or "
            "stop with an honest explanation if no suitable problem was found. Do not start solving "
            "in this turn."
        )
    if run.phase == Phase.SOLVE:
        ending = (
            "This is the standalone SOLVE task: save partial candidates as needed, then submit "
            "your final candidate with conclude: true. This finishes solving and leaves verification "
            "to the separate verify command. Do not mark your own proof as verified."
            if run.workflow == Workflow.SOLVE
            else "This is the full pipeline: candidates go to a separate reviewer. After feedback, "
            "continue in the same research session. Use conclude: true only for a final deliverable."
        )
        return "Task: SOLVE the supplied mathematical problem. " + ending
    return (
        "Task: VERIFY the supplied candidate independently. Assess the precise claim, proof "
        "validity and novelty separately. Check assumptions, circular reasoning, edge cases, "
        "references and counterexamples using your available tools. Supply specific evidence "
        "and use INCONCLUSIVE when appropriate. Submit kind: review with your verdict. "
        + (
            "This standalone audit ends after the review, including ISSUES_FOUND or INCONCLUSIVE. "
            "Do not take over solving or rewrite the candidate."
            if run.workflow == Workflow.VERIFY or run.native.review_only
            else "The harness will return your findings to the original research session."
        )
    )


def record_selection(store: Store, run: Run, milestone: NativeCheckpoint):
    """Save a ranked result and reusable problems; retain unsupported claims only as raw evidence."""
    retrieved = [o["result"] for o in run.observations if o.get("phase") == "FIND"]
    shortlist = []
    selected = None
    for proposed in milestone.shortlist or [milestone.problem]:
        problem = proposed.model_copy(deep=True)
        problem.formal_target = None
        problem.educational = False
        problem = conservative_status(problem, retrieved)
        saved = store.save_problem(problem)
        if not any(existing.id == saved.id for existing in shortlist):
            shortlist.append(saved)
        if proposed.id == milestone.problem.id:
            selected = saved
    run.shortlist = shortlist
    run.problem = selected
    atomic_write(
        store.run_dir(run.id) / "literature" / "selection.json",
        json_text(
            {
                "selected": run.problem.id,
                "ordered_candidates": [p.model_dump(mode="json") for p in shortlist],
                "agent_assessment": milestone.model_dump(mode="json"),
                "scope": "Heuristic ranking; source checks are not certification of open status",
            }
        ),
    )
