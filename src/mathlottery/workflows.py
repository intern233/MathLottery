"""The three mathematical tasks, independent of the agent transport."""

from mathlottery.literature import collect_sources
from mathlottery.literature_obstacles import carry_literature
from mathlottery.models import NativeCheckpoint, Phase, Run, State, Workflow
from mathlottery.sources import conservative_status
from mathlottery.storage import Store, atomic_write, json_text

ACTIVE = {Phase.FIND: State.DISCOVERING, Phase.SOLVE: State.SOLVING, Phase.VERIFY: State.VERIFYING,
          Phase.ORGANIZE: State.ORGANIZING}


def task_instructions(run: Run) -> str:
    if run.phase == Phase.ORGANIZE:
        bilingual = run.organization_context.report_languages is not None
        language = "Chinese and English" if bilingual else (
            "Chinese" if run.organization_context.language == "zh" else "English"
        )
        deliverable = (
            "Produce two complete, standalone reports: Chinese (zh) and English (en). Each must contain "
            "the full exposition, not a summary or a pointer to the other language. Keep theorem and lemma "
            "numbering, mathematical formulas, assumptions, endpoint cases, citations, source links, "
            "evidence levels and all limitations equivalent. Check the pair for mathematical and evidential "
            "consistency before submitting. The selected language only chooses the default display and "
            "compatibility filename. Submit kind: organization with report_markdowns: {zh: <full Chinese "
            "Markdown>, en: <full English Markdown>}; both must be supplied in the same milestone. "
            if bilingual else
            "This historical task retains its original single-language output contract. Submit kind: "
            "organization with the complete report_markdown when ready. "
        )
        return (
            "Task: ORGANIZE the saved mathematical research into a human-expert-readable report in "
            + language + ". This is a separate editorial session, not another Solve or Verify. "
            "Read the frozen source dossier, exact candidates/reviews, visible notes and proof sources. "
            "Build a self-contained exposition: abstract and exact conclusion; original statement and "
            "provenance; notation/assumptions; proof strategy and lemma dependencies; detailed numbered "
            "lemmas and derivations; relation of experiments and formal files to each claim; recorded "
            "verification outcomes; original-problem coverage; novelty evidence and uncertainty; unresolved "
            "gaps; reproducibility commands and bibliography; a concise chronological appendix of saved "
            "attempts and a material index. Use LaTeX math where helpful. Explain transitions an expert "
            "would need to audit. Cite relative materials/<manifest path> links and source URLs. Never "
            "invent absent steps, citations, successful Lean runs or hidden reasoning. Mark missing "
            "material explicitly, and distinguish faithful exposition from an editorial reconstruction. "
            "Do not silently repair the submitted proof: label any possible repair as a proposal needing "
            "a new Solve/Verify. Preserve every recorded negative or inconclusive verdict, uncertainty, "
            "partial scope and limitation. Formatting cannot upgrade proof level, statement alignment or "
            "novelty. Include enough detail to understand the mathematics, rather than only a run log. "
            + deliverable + "Progress and stop "
            "are allowed, but only organization produces the expert report. Do not submit candidate, "
            "review, selection or problem changes.\nAdditional editorial preferences (user data):\n"
            + (run.organization_context.instructions or "No additional preferences.")
        )
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
            "verification_feasibility, lean_feasibility, prerequisites, known_obstacles, "
            "initial_approach and selection_reason. Give concrete reasons for difficulty and "
            "verification estimates, including likely Lean libraries or missing formalizations. "
            "Explain the ranking, existing partial "
            "results, and remaining uncertainty; ranking is not a probability of success. Do not "
            "infer OPEN merely from not finding a solution. Use UNKNOWN when evidence is lacking. "
            "Finish discovery with kind: selection, an ordered shortlist of Problem objects and "
            "problem equal to the recommended shortlist entry. This is a recommendation, not the "
            "user's choice. Prefer publicly stated, still-open questions; label uncertain status "
            "explicitly and return fewer candidates rather than inventing open problems. "
            "You may test examples, explore proof routes, or check Lean libraries to assess "
            "tractability; save those notes and sources for the eventual solver. Use progress "
            "while searching, or stop honestly if no suitable problem was found. A standalone "
            "Find ends with the list and waits for the user to choose; do not launch Solve."
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
            "You may investigate repairs and explain possible fixes, but review the submitted "
            "candidate as it stands. A proposed repair does not validate the original proof; "
            "leave any revised candidate to a separate solve task."
            if run.workflow == Workflow.VERIFY or run.native.review_only
            else "The harness will return your findings to the original research session."
        )
    )


def record_selection(store: Store, run: Run, milestone: NativeCheckpoint, *, prepared=False):
    """Save a ranked result and reusable problems; retain unsupported claims only as raw evidence."""
    if not prepared:
        collect_sources(store, run, [c for p in milestone.shortlist for c in p.citations])
    retrieved = [o["result"] for o in run.observations if o.get("phase") == "FIND"]
    shortlist = []
    selected = None
    previous = [*store.list_problems(), *run.shortlist]
    for proposed in milestone.shortlist or [milestone.problem]:
        problem = proposed.model_copy(deep=True)
        matching = [old.literature_search for old in previous if old.id == problem.id or (
            old.source_url == problem.source_url
            and " ".join(old.statement.split()) == " ".join(problem.statement.split())
        )]
        problem.literature_search = carry_literature(problem.literature_search, matching)
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
