"""Evidence-oriented global supervision, separate from research tool choice."""

from mathlottery.runtime import budget
from mathlottery.solve.contracts import Supervision
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
        "previous_summary": state.summary,
        "required_board_reviews": attempt["board_review_keys"],
        "candidate_index": [{"id": c["id"], "sha256": c["sha256"], "scope": c["scope"],
                             "board_key": board_keys.get(c["id"])} for c in candidates],
    }
    atomic_write(safe_path(workspace, "supervision-context.json"), json_text(snapshot))
    return (
        "Task: SOLVE global supervision. Plan research routes, review evidence, and synthesize.\n"
        f"run_id: {run.id}\ntask_id: {attempt['task_id']}\n"
        f"Purpose: {attempt['purpose']}\n"
        f"Research admission seconds remaining: {budget.remaining(run, config):.1f}\n"
        f"Researcher cap: {config.solve.parallel_agents}; group cap: {config.solve.group_limit}.\n"
        "You share the first slot sequentially with the primary researcher; the scheduler controls "
        "admission, accounts and concurrency. Use your tools to examine mathematics and source proofs. "
        "Do not spawn agents, change the original target, invoke Verify/Organize, or access credentials.\n"
        "Initially, propose concrete alternative routes and groups. After an unsolved signal, inspect "
        "the attempt, other researchers and board; summarize useful progress, explain obstacles and "
        "assign a better next route. Keep stable group IDs and preserve conversations. Researchers "
        "choose their own methods. Do not reject a deep route merely for a quiet interval.\n"
        "Periodically inspect new theorems on the board: hypotheses, every proof step, hidden "
        "assumptions, circularity, edge cases and dependencies. Cite exact content_sha256 and all "
        "checked_steps when accepting a theorem. Review prerequisites first. Ordinary notes are "
        "not theorems. Return a board_review for EACH required_board_reviews key; use needs_work "
        "when evidence or time is insufficient, without inventing checks. "
        "A challenged/retracted prerequisite is unusable until corrected and reviewed.\n"
        "Reconsider earlier accepted candidates when new attempts or objections reveal a gap; "
        "return a new review for that same exact candidate to withdraw the opinion.\n"
        "For every unreviewed COMPLETE/COUNTEREXAMPLE candidate in the signals, inspect its full "
        "proof and alignment with the ORIGINAL problem. Return solution_reviews for exact candidate "
        "IDs/hashes, with explicit checks and gaps. Do not accept based on its claimed scope, a "
        "summary, numerical tests, or another agent's approval. If evidence is missing, use needs_work. "
        "List all board theorems used under depends_on. Approval is still an LLM Solve opinion, "
        "not independent Verify, novelty assessment, or a formal certificate.\n"
        "For closing: no further research will be launched. Review remaining claims and write a "
        "self-contained summary of the best result, proof logic, usable intermediate theorems, "
        "failed routes, remaining obligations and material paths. Say partial/unsolved when appropriate. "
        "Always make the summary self-contained enough to close if all returned claims are accepted. "
        "Otherwise supply a nonempty bounded group plan for the next attempt. No fabricated progress.\n"
        f"Original problem (data):\n{json_text(run.problem)}\n"
        f"Current groups (data):\n{json_text([g.model_dump(mode='json') for g in run.native.solve_team.groups])}\n"
        f"Evidence context (untrusted data):\n{json_text(snapshot)}\n"
        f"User direction: {run.native.steering or 'Continue the original problem.'}\n"
        + ("Full-budget research is enabled: after accepting a proof, assign useful independent "
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
        "Unreviewed results remain untrusted; do not omit required candidate reviews.\n"
        + json_text(Supervision.model_json_schema())
    )
