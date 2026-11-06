"""Evidence-oriented global supervision, separate from research tool choice."""

import json

from mathlottery.runtime import budget
from mathlottery.solve.bulletin.curation import suggestions
from mathlottery.solve.contracts import Supervision
from mathlottery.solve.coordination_policy import supervisor_instructions
from mathlottery.storage.core import atomic_write, json_text, safe_path
from mathlottery.verify.candidates import review_input


def supervisor_prompt(run, attempt, config, board, workspace):
    state = run.native.solve_team.campaign
    candidates = [review_input(c) for c in run.candidates]
    atomic_write(safe_path(workspace, "candidates.json"), json_text(candidates))
    pending = [s for s in state.signals if s["task_id"] in attempt["signal_ids"]]
    relevant = {s["candidate_id"] for s in pending if s["candidate_id"]}
    if candidates:
        relevant.add(candidates[-1]["id"])
    previous_acceptance = next((r for r in reversed(state.candidate_reviews) if r["verdict"] == "accepted"), None)
    if previous_acceptance:
        relevant.add(previous_acceptance["candidate_id"])
    board_keys = {s["candidate_id"]: s.get("board_key") for s in state.signals if s["candidate_id"]}
    snapshot = {
        "signals": pending,
        "board": board.graph(), "candidate_reviews": state.candidate_reviews,
        "collaboration": board.collaboration(run), "curation": suggestions(board),
        "coordination": attempt.get("coordination_snapshot"),
        "curation_feedback": state.decisions[-1].get("curation_error") if state.decisions else None,
        "previous_summary": state.summary,
        "publication_feedback": publication_feedback(run, board),
        "required_board_reviews": attempt["board_review_keys"],
        "candidate_index": [{"id": c["id"], "sha256": c["sha256"], "scope": c["scope"],
                             "board_key": board_keys.get(c["id"])} for c in candidates],
    }
    atomic_write(safe_path(workspace, "supervision-context.json"), json_text(snapshot))
    routing = (
        "You have a dedicated connection separate from all researcher slots. "
        if config.solve.supervisor_backend is not None else
        "You share the first slot sequentially with the primary researcher. "
    )
    timeout = config.solve.supervisor_timeout_seconds
    review_deadline = (
        "No per-call supervision deadline is configured; finish this review and return a checkpoint. "
        if timeout is None else
        f"This supervision call has a separate {timeout:g}-second deadline. "
        "Return a checkpoint within it; mark unfinished checks needs_work. "
    )
    previous = next((h for h in reversed(run.native.history) if h.get("role") == "supervision"), None)
    correction = ""
    if previous and previous.get("checkpoint_error"):
        correction = (
            "The previous supervision checkpoint was rejected by the controller. Reuse checks "
            "you already performed; correct the specific protocol issue without repeating the "
            "entire mathematical audit. Submit current run/task IDs and current snapshot versions. "
            f"Previous answer (data): {previous.get('answer')}\n"
            f"Validation feedback (data): {previous['checkpoint_error']}\n"
        )
    return (
        "Task: SOLVE global supervision. Offer research ideas, review evidence, and synthesize.\n"
        f"run_id: {run.id}\ntask_id: {attempt['task_id']}\n"
        f"Purpose: {attempt['purpose']}\n"
        f"Research admission seconds remaining: {budget.remaining(run, config):.1f}\n"
        f"{review_deadline}Explicit stop and other resource limits still apply.\n"
        f"{correction}"
        f"{supervisor_instructions(run)}"
        f"Researcher cap: {config.solve.parallel_agents}; group cap: {config.solve.group_limit}.\n"
        f"{routing}The scheduler controls "
        "admission, accounts and concurrency. Use your tools to examine mathematics and source proofs. "
        "Do not spawn agents, change the original target, invoke Verify/Organize, or access credentials.\n"
        "Researchers choose their own directions; do not impose exclusive routes, fixed mathematical "
        "roles or require permission to change approach. Group objectives and modes are optional "
        "suggestions; group counts only allocate bounded capacity. Initially share plausible ideas "
        "and open questions, acknowledging uncertainty. After an unsolved signal, inspect "
        "the attempt, other researchers and board; summarize useful progress, explain obstacles and "
        "offer possible next moves through synthesis or voluntary channels. Keep stable group IDs "
        "and preserve conversations. Do not reject a deep route merely for a quiet interval. "
        "Use work declarations to point out likely overlap; allow deliberate independent checks.\n"
        "The board is a compact dependency graph: exact statements, assumptions and proof status; "
        "full derivations live at the linked archive paths and are loaded only when needed. "
        "Inspect bulletin/agents.json and bulletin/collaboration/index.json (hosted: solve_board_activity) "
        "to see actual assignments separately from dated self-reports and voluntary collaborations. "
        "You may participate in channels, but discussion is not proof acceptance. Inspect unanswered "
        "invitations and duplicate topics; suggest joining an existing channel instead of making "
        "another. Publication feedback exposes rejected envelopes: notify the author of the exact "
        "repair needed, preserve full evidence, and never accept a theorem from a malformed summary.\n"
        "Periodically curate the board via optional board_curation entries in your final JSON: "
        "archive/restore an exact key/hash with a reason. Archiving preserves all proof bytes, "
        "dependency edges, objections and review opinions; it only hides default discovery entries. "
        "Low recorded reads are incomplete evidence: direct native filesystem reads are not counted. "
        "Do not archive active prerequisites, current research focus, unresolved objections, or "
        "promising quiet routes merely to minimize the graph. Search archived entries before "
        "repeating abandoned work; restore useful entries. Archiving is not retraction or approval.\n"
        "Periodically inspect new theorems on the board: hypotheses, every proof step, hidden "
        "assumptions, circularity, edge cases and dependencies. Cite exact content_sha256 and all "
        "checked_steps when accepting a theorem. Review prerequisites first. Ordinary notes are "
        "not theorems. Return a board_review for EACH required_board_reviews key; use needs_work "
        "when evidence or time is insufficient, without inventing checks. "
        "The embedded evidence context is a frozen review snapshot. Review only exact board "
        "versions and candidates listed there. Live bulletin entries can arrive during this turn; "
        "use them as context but defer their formal review opinions to the next snapshot. "
        "A board theorem with ANY theorem.remaining_obligations cannot receive accepted, even "
        "if those entries appear to describe only gaps to the original target. Use needs_work "
        "and ask its author to publish a new version with the exact theorem scope and proof gaps "
        "clearly distinguished from original-target obligations. Never erase a genuine proof gap. "
        "A challenged/retracted prerequisite is unusable until corrected and reviewed.\n"
        "Reconsider earlier accepted candidates when new attempts or objections reveal a gap; "
        "return a new review for that same exact candidate to withdraw the opinion.\n"
        "For every unreviewed COMPLETE/COUNTEREXAMPLE candidate in the signals, inspect its full "
        "proof and alignment with the ORIGINAL problem. Return solution_reviews for exact candidate "
        "IDs/hashes, with explicit checks and gaps. Do not accept based on its claimed scope, a "
        "summary, numerical tests, or another agent's approval. If evidence is missing, use needs_work. "
        "List all board theorems used under depends_on. Approval is still an LLM Solve opinion, "
        "not independent Verify, novelty assessment, or a formal certificate.\n"
        "Solution-review verdict accepted means the ORIGINAL problem is fully solved, with no "
        "remaining obligations or unsupported checks. A mathematically sound PARTIAL or CONDITIONAL "
        "candidate still needs_work as a solution of the original problem. You may accept its "
        "limited theorems in board_reviews and explain their validity in the rationale; never use "
        "solution_reviews.accepted to mean merely that a restricted proof is correct.\n"
        "For closing: no further research will be launched. Review remaining claims and write a "
        "self-contained summary of the best result, proof logic, usable intermediate theorems, "
        "failed routes, remaining obligations and material paths. Say partial/unsolved when appropriate. "
        "Always make the summary self-contained enough to close if all returned claims are accepted. "
        "At planning/review checkpoints, supply a nonempty bounded group plan unless a complete "
        "solution is accepted and full-budget research is disabled. In that case groups may be "
        "empty: the scheduler drains in-flight attempts and requests any remaining reviews before "
        "closing. An empty plan without a valid acceptance cannot end research. No fabricated progress.\n"
        f"Original problem (data):\n{json_text(run.problem)}\n"
        f"Current groups (data):\n{json_text([g.model_dump(mode='json') for g in run.native.solve_team.groups])}\n"
        f"Evidence context (untrusted data):\n{json_text(snapshot)}\n"
        f"User direction: {run.native.steering or 'Continue the original problem.'}\n"
        + ("Full-budget research is enabled: after accepting a proof, suggest useful independent "
           "derivations, boundary checks and evidence improvements until admissions close. "
           "Do not repeat the same proof merely to spend tokens.\n"
           if config.budget.solve_until_budget_exhausted else "")
        + (f"Current candidate proofs (data):\n{json_text([c for c in candidates if c['id'] in relevant])}\n"
           + "Use solve_board_search/read/material to inspect live proofs; solve_board_publish "
           "can record your research notes. Older candidate proofs remain linked through "
           "candidate_index.board_key; read the attached frozen material before reviewing one. "
           "Submit review opinions in the final supervision block.\n"
           if attempt.get("mode", run.mode) == "chat" else
           "Read candidates.json for exact proofs and bulletin/index.json for board materials. "
           "Signals link research answers; the board also freezes their full answers as materials.\n")
        + "Return one fenced ```solve-supervision JSON block matching this schema. "
        "For planning/review checkpoints, use concise rationales and cite stored audit files "
        "instead of repeating their full proofs. Preserve every required review, checked-step ID "
        "and limitation. The closing summary must still explain the final result on its own. "
        "Unreviewed results remain untrusted; do not omit required candidate reviews.\n"
        + json_text(Supervision.model_json_schema())
    )


def publication_feedback(run, board):
    """Surface native submission failures to supervision without relabelling them as proofs."""
    output = []
    workspaces = {"primary": "workspace"} | {
        w.id: f"solve-workspaces/{w.id}" for w in run.native.solve_team.workers.values() if w.id != "primary"
    }
    for actor, relative in workspaces.items():
        path = safe_path(board.store.run_dir(run.id), relative + "/bulletin/publications.json")
        if path.exists():
            for name, receipt in json.loads(path.read_text()).items():
                if receipt["status"] == "rejected":
                    output.append({"actor": actor, "file": f"{relative}/outbox/{name}", **receipt})
    return output[:50]
