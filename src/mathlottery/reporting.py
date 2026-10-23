import json

from mathlottery.budget import elapsed
from mathlottery.metrics import run_metrics
from mathlottery.models import Run
from mathlottery.storage import Store, atomic_write, json_text


def source_assessment(assessment) -> str:
    if not assessment.policy_version:
        return "Evidence policy: not assessed (historical or user-supplied record)."
    lines = [f"Evidence policy: `{assessment.policy_version}` · Checked: {assessment.assessed_at}"]
    lines += [f"- Gap: {reason}" for reason in assessment.reasons]
    lines += [f"- Search limitation (reported): {item}" for item in assessment.limitations]
    for citation in assessment.checked_citations:
        lines.append(
            f"- {citation['role']} · {citation['url']} · {citation['locator']} · "
            f"excerpt matched: {citation['verified_excerpt']} · "
            f"source date (reported): {citation.get('source_date') or 'unknown'} · "
            f"SHA-256: `{citation.get('sha256') or 'unavailable'}`"
        )
    lines += [f"- Observed search: {query}" for query in assessment.observed_queries]
    lines.append("Excerpt matching verifies retrieved text, not its interpretation or search completeness.")
    return "\n\n".join(lines)


def report(store: Store, run: Run):
    metrics = run_metrics(run)
    atomic_write(store.run_dir(run.id) / "metrics.json", json_text(metrics))
    problem = run.problem
    backend = run.config.get("backend", {})
    sections = [
        "# MathLottery — Mathematical Research Report",
        f"Run: `{run.id}` · Workflow: `{run.workflow}` · State: **{run.state}** · Phase: `{run.phase}`",
        "## Problem",
        f"### {problem.title}\n\n{problem.statement}" if problem else "No problem selected.",
        f"Source: {problem.source_url or 'User-provided / educational example'}" if problem else "",
        "## Open Status",
        (
            f"**{problem.status}** (agent assessment, not a certification).\n\n"
            f"Checked: {problem.status_checked_at or 'not established'}\n\n"
            + "\n".join(f"- {url}" for url in problem.status_evidence)
            + "\n\n" + source_assessment(problem.evidence_assessment)
        )
        if problem
        else "UNKNOWN",
        "## Research Configuration",
        f"Backend: `{run.mode}` · Execution: `{run.execution}` · "
        f"Requested model: `{backend.get('model') or 'inherited from Codex / unreported'}` · "
        f"Requested reasoning effort: `{backend.get('reasoning_effort') or 'inherited from Codex / unreported'}`",
        (
            f"Requested Chat reasoning mode: `{backend.get('chat', {}).get('reasoning_mode') or 'API default'}`"
            if run.mode == "chat"
            else ""
        ),
        "```json\n"
        + json.dumps({"budget": run.config.get("budget"), "environment": run.environment}, indent=2)
        + "\n```",
        "## Exploration Summary",
    ]
    if run.organization_context:
        context, document = run.organization_context, run.organization_report
        sections += [
            "## Expert Reading Report",
            f"Editorial reconstruction of source `{context.source_run_id}`, revision {context.source_revision}. "
            "This does not add an independent verification or upgrade proof, novelty or open-status claims.",
        ]
        if document:
            sections += ["[Expert report (Markdown)](organized/report.md)",
                         "[Evidence manifest](organized/manifest.json)",
                         f"PDF export: `{document.pdf_status}`."]
            if document.pdf_status == "ready":
                sections.append("[Expert report (PDF)](organized/report.pdf)")
            elif document.pdf_error:
                sections.append(document.pdf_error)
        else:
            sections.append("The expert report has not been produced yet.")
    if run.shortlist:
        sections.extend(
            ["## Ranked Problems", "Ranking is a heuristic, not a probability of success."]
        )
        for number, item in enumerate(run.shortlist, 1):
            sections.append(
                f"{number}. **{item.title}** (`{item.id}`, {item.status})\n\n"
                f"{item.statement}\n\nReason: {item.selection_reason}\n\n"
                f"Difficulty: {item.difficulty_estimate}\n\n"
                f"Verification feasibility: {item.verification_feasibility}\n\n"
                f"Source: {item.source_url or 'not established'}"
            )
        sections.append("[Selection record and agent assessments](literature/selection.json)")
        if run.workflow == "find":
            sections.append("Find has not started solving. Choose a problem from this list to start a separate Solve task with its discovery dossier.")
        for item in run.shortlist:
            sections.append(f"### Assessment: {item.title}\n\nDifficulty: {item.difficulty_estimate}\n\n"
                            f"Verification: {item.verification_feasibility}\n\nLean: {item.lean_feasibility}\n\n"
                            f"Prerequisites: {'; '.join(item.prerequisites) or 'not assessed'}\n\n"
                            f"Obstacles: {'; '.join(item.known_obstacles) or 'not assessed'}\n\n"
                            f"Initial approach: {item.initial_approach or 'not assessed'}")
    if run.discovery_context:
        context = run.discovery_context
        sections += ["## User-selected Discovery Context",
                     f"Source Find: `{context.source_run_id}` · Captured: {context.captured_at}\n\n"
                     f"Selected problem SHA-256: `{context.problem_sha256}`\n\n"
                     f"{len(context.files)} frozen research files; a new solver session, not a shared Find conversation.",
                     "[Context manifest](discovery-context/manifest.json)",
                     *[f"- Omitted: {item}" for item in context.omitted]]
    sections += [f"- Round {m.source_iteration} [{m.status}] {m.content}" for m in run.memory]
    if not run.memory and run.execution != "native":
        sections.append("No research memory recorded yet.")
    if run.execution == "native":
        sections += [
            "## Workflow Measurements",
            "[Machine-readable metrics](metrics.json). Invocation seconds cover measured client "
            "calls only; unmeasured history and recovery are not counted as zero. "
            "These are workflow measurements, not mathematical success rates.",
            "| Stage | Returns | Completed | Milestone errors | Timed returns | Invocation seconds |\n"
            "| --- | ---: | ---: | ---: | ---: | ---: |\n"
            + "\n".join(
                f"| {phase} | {values['returns']} | {values['completed']} | "
                f"{values['handoff_errors']} | {values['timed_returns']} | "
                f"{values['invocation_seconds'] if values['invocation_seconds'] is not None else 'unknown'} |"
                for phase, values in metrics["stages"].items()
            ),
        ]
        sections.extend(
            [
                "## Native Research",
                f"Codex research session: `{run.native.solver_session_id or 'not started'}`",
                f"Reviewer session: `{run.native.reviewer_session_id or 'not started'}`",
                f"Chat research response: `{run.native.solver_response_id or 'not started'}`",
                f"Chat review response: `{run.native.reviewer_response_id or 'not started'}`",
                "Native conversation history and research files replace the structured memory window. "
                "Codex may compact its own context; no unbounded context guarantee is made.",
            ]
        )
        for entry in run.native.history:
            line = f"- {entry['role']} · {entry['status']} · [Full answer]({entry['answer']})"
            if (store.run_dir(run.id) / entry["events"]).is_file():
                line += f" · [Native events]({entry['events']})"
            sections.append(line)
            if entry.get("milestone", {}).get("summary"):
                sections.append(entry["milestone"]["summary"])
            if entry.get("runtime"):
                sections.append(
                    "Observed runtime: " + json.dumps(entry["runtime"], ensure_ascii=False)
                )
    sections.append("## Candidate Results")
    for candidate in run.candidates:
        sections.extend(
            [
                f"### {candidate.id} — {candidate.level}",
                f"SHA-256: `{candidate.sha256}`",
                candidate.claim,
                "Assumptions: " + ("; ".join(candidate.assumptions) or "none stated"),
                f"Declared scope: **{candidate.scope}** (researcher assessment)",
                "Remaining obligations: " + ("; ".join(candidate.remaining_obligations) or "none listed; not a completeness certificate"),
                candidate.proof,
            ]
        )
    if not run.candidates:
        sections.append("No candidate proof was produced. This is a valid research outcome.")
    sections.append("## Verification")
    for candidate in run.candidates:
        for review in candidate.reviews:
            sections.extend(
                [
                    f"{candidate.id}: **{review.verdict}**",
                    f"Truth: {review.truth_assessment}",
                    f"Proof: {review.proof_assessment}",
                    "\n".join(f"- {issue}" for issue in review.issues),
                    "Evidence: " + "; ".join(review.evidence),
                    f"Original-problem coverage: **{review.original_problem_coverage}** (reviewer assessment). "
                    + review.coverage_explanation,
                    "Remaining obligations: " + ("; ".join(review.remaining_obligations) or "none listed"),
                    "\n".join(f"- Evidence gate: {note}" for note in review.validation_notes),
                ]
            )
            for check in review.checks:
                sections.append(
                    f"- {check.method} / {check.result} · blocking: {check.blocking}\n\n"
                    f"{check.claim}\n\n{check.reasoning}\n\n" + "; ".join(check.evidence)
                )
            if review.reported_verdict and review.reported_verdict != review.verdict:
                sections.append(f"Raw agent verdict: {review.reported_verdict}; stored verdict: {review.verdict}.")
            if review.formal_receipt:
                receipt = review.formal_receipt
                sections += [
                    f"Independent Lean check: **{receipt['status']}**. {receipt.get('reason', '')}",
                    f"[Execution receipt]({receipt.get('artifact', '')}). "
                    "This checks named declarations, not equivalence to the original problem.",
                    "```json\n" + json.dumps(receipt, indent=2, ensure_ascii=False) + "\n```",
                ]
    for observation in run.observations:
        if observation.get("tool") in ("python_exec", "sympy_compute", "lean_check"):
            result = observation["result"]
            sections.append(
                f"- `{observation['tool']}`: {result.get('status')} — "
                f"[{observation['artifact']}]({observation['artifact']})"
            )
    sections.append("## Novelty Assessment")
    for candidate in run.candidates:
        if candidate.reviews:
            review = candidate.reviews[-1]
            sections.append(f"{candidate.id}: **{review.novelty}**. {review.novelty_notes}")
            sections.append(source_assessment(review.evidence_assessment))
            if review.reported_novelty and review.reported_novelty != review.novelty:
                sections.append(f"Raw agent novelty: {review.reported_novelty}; stored assessment: {review.novelty}.")
            sections.extend(
                f"- [{ref.title or ref.url}]({ref.url})" for ref in review.novelty_references
            )
    sections.append(
        "Search coverage is limited to retrieved sources; no search hit is not proof of novelty."
    )
    sections += [
        "## Resource Usage",
        metrics["usage_warning"],
        f"Completed/attempted rounds: {run.iteration}",
        f"Active wall time: {elapsed(run):.2f} seconds (manual Chat waiting is excluded).",
        f"Measured input tokens: {run.usage.input_tokens if run.usage.input_tokens is not None else 'unknown'}",
        f"Measured output tokens: {run.usage.output_tokens if run.usage.output_tokens is not None else 'unknown'}",
        f"Calls with unknown token usage: {run.usage.unknown_calls}",
        "Chat uses explicitly selected API billing; Codex uses its configured ChatGPT login. "
        "There is no automatic backend fallback. API dollar costs, subscription balance and "
        "third-party tool costs are not measured here; use provider account spending controls.",
        "## Limitations",
        "LLM review and finite experiments do not prove a general theorem. No expert review "
        "has been recorded. Lean compilation alone is not the complete formal trust policy. "
        "Natural-language/formal-statement equivalence is not automatically certified.",
        f"Stop reason: {run.stop_reason or 'none'}",
        f"Last error: {run.last_error or 'none'}",
        "## Reproduction",
        "Run the following commands from the MathLottery project directory.",
        "```bash\nconda activate mathlottery\n"
        f"mathlottery status {run.id}\nmathlottery report {run.id}\n"
        f"mathlottery resume {run.id}\n```",
        "See config.yaml, events.jsonl, checkpoints/, literature/, experiments/, and candidates/ "
        "in this run directory. Demo responses are scripted and explicitly labelled; "
        "their Python calculations are real local executions.",
    ]
    path = store.run_dir(run.id) / "report.md"
    atomic_write(path, "\n\n".join(part for part in sections if part) + "\n")
    return path
