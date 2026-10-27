"""The three mathematical tasks, independent of the agent transport."""

from mathlottery.literature import collect_sources
from mathlottery.literature_obstacles import carry_literature
from mathlottery.models import CandidateInput, NativeCheckpoint, Phase, Run, State, Workflow
from mathlottery.sources import conservative_status
from mathlottery.storage import Store, atomic_write, json_text

ACTIVE = {Phase.FIND: State.DISCOVERING, Phase.SOLVE: State.SOLVING, Phase.VERIFY: State.VERIFYING,
          Phase.ORGANIZE: State.ORGANIZING}


def claims_complete(candidate: CandidateInput) -> bool:
    """Explicit solver scope only; proof validity and novelty remain review questions."""
    return (
        candidate.scope in {"COMPLETE", "COUNTEREXAMPLE"}
        and not candidate.remaining_obligations
    )


def full_solve_budget(run: Run) -> bool:
    return (
        run.execution == "native" and run.workflow == Workflow.SOLVE
        and run.config.get("budget", {}).get("solve_until_budget_exhausted") is True
    )


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
            "Begin with a concise expert entry: exact proven and unproved claims, original-problem "
            "scope, known prior results, the weakest proof link, and where to inspect the decisive "
            "evidence. Distinguish a recorded compiler/kernel check from untested reproduction "
            "instructions. The controller adds a deterministic handoff index separately; do not "
            "duplicate raw logs or long receipt JSON inside the mathematical exposition. "
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
            "Before recommending substantial Solve work, record source_statement (the exact original "
            "question, with its quantifiers), scope_relation (FULL_STATEMENT, EXPLICIT_SUBPROBLEM, "
            "INTERPRETATION, or UNKNOWN), scope_description explaining the chosen target, and "
            "prior_work_summary identifying what is already proved and what remains. Explicitly "
            "disclose statement_risks: id, kind, severity, description, impact, next_action, source_url "
            "and locator. Compare assumptions, all versus fixed exponents, domains, boundary cases, "
            "and source examples/errata. A chosen branch is not the whole conjecture; conflicting "
            "source quantifiers require NEEDS_CLARIFICATION, not a silent convenient interpretation. "
            "An empty risk list means no risk was reported, not certified unambiguity. These fields "
            "are final selection disclosures; keep native exploration and tool use autonomous. "
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
            "This standalone SOLVE uses the full active-time budget. All candidates, including "
            "COMPLETE or COUNTEREXAMPLE with conclude: true, are saved as checkpoints; they "
            "do not finish this task early. Use the remaining budget for useful mathematical "
            "work: critically check the strongest proof, test counterexamples and boundary "
            "cases, resolve missing justifications and improve reproducible evidence. Preserve "
            "valid earlier results and explicitly correct any gaps you discover. Do not idle "
            "or repeat identical work simply to spend time. Honest PARTIAL/UNKNOWN checkpoints "
            "are welcome during research; the harness reports the final outcome at the time "
            "limit. This is still Solve self-checking, not independent Verify. "
            if full_solve_budget(run) else
            "This is the standalone SOLVE task: save partial candidates as checkpoints and "
            "continue the same research session within the remaining budget. A candidate with "
            "scope COMPLETE or COUNTEREXAMPLE, no remaining mathematical obligations and "
            "conclude: true finishes solving and leaves verification to the separate verify "
            "command. Do not mark your own proof as verified."
            if run.workflow == Workflow.SOLVE
            else "This is the full pipeline: candidates go to a separate reviewer. After feedback, "
            "continue in the same research session. A positive review of a partial result does "
            "not end the pipeline. Use conclude: true only with scope COMPLETE or COUNTEREXAMPLE "
            "and no remaining mathematical obligations."
        )
        return (
            "Task: SOLVE the supplied mathematical problem. " + ending
            + " PARTIAL, UNKNOWN and candidates with unresolved mathematical obligations do not "
            "finish Solve, even with conclude: true. A model stop milestone also saves progress "
            "and continues Solve. A model stop is not a user stop request; explicit user "
            "cancellation remains available. "
            "The harness enforces time, iteration and token limits and handles provider failures. "
            "When a route fails, record the obstacle and reconsider assumptions, references or "
            "another approach. Do not repeat completed work merely to spend time or mislabel "
            "partial work as complete to end the task. Completeness concerns the frozen problem, "
            "not only a lemma or a restricted case; correctness and novelty belong to Verify."
        )
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


def assess_selection(problem, retrieved, previous):
    """Keep source obligations across native and structured selection attempts."""
    problem = problem.model_copy(deep=True)
    matching = [old for old in previous if old.id == problem.id or (
        old.source_url == problem.source_url
        and " ".join(old.statement.split()) == " ".join(problem.statement.split())
    )]
    problem.literature_search = carry_literature(problem.literature_search, [old.literature_search for old in matching])
    return conservative_status(problem, retrieved, previous_assessments=[old.evidence_assessment for old in matching])


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
        problem.formal_target = None
        problem.educational = False
        problem = assess_selection(problem, retrieved, previous)
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
