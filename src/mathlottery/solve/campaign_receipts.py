"""Exactly-once owner-thread accounting and supervisor/researcher handshakes."""

from mathlottery.models import now
from mathlottery.providers.base import BackendResult, BackendStatus
from mathlottery.runtime import budget
from mathlottery.runtime.milestones import validate_milestone
from mathlottery.runtime.workflows import claims_complete
from mathlottery.solve.contracts import parse_supervision
from mathlottery.storage.core import atomic_write, json_text


class CampaignReceipts:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.engine, self.store = coordinator.engine, coordinator.store

    def consume(self, run, receipt, config, board):
        team, state = run.native.solve_team, run.native.solve_team.campaign
        task_id = receipt["task_id"]
        if task_id in state.processed_tasks:
            team.active_attempts = [a for a in team.active_attempts if a["task_id"] != task_id]
            self.store.save(run, "solve_receipt_replayed", task_id=task_id)
            return None
        result = BackendResult(**receipt["result"])
        self.coordinator.attempts.remember(run, receipt)
        if result.pending:
            self.store.save(run, "solve_remote_pending", task_id=task_id)
            return result.error or "Remote outcome unresolved; resume the existing call"
        self.engine._account(run, result)
        if result.invoked:
            run.iteration += 1
        if receipt["role"] == "supervision":
            counter = run.model_copy(update={"usage": team.supervisor_usage})
            self.engine._account(counter, result)
        history = {
            **{key: receipt.get(key) for key in (
                "task_id", "worker_id", "group", "role", "mode", "model", "provider", "slot_id",
                "invocation_seconds", "source_observed_at", "checkpoint_error",
            )},
            "phase": "SOLVE", "status": result.status, "usage": result.usage,
            "runtime": result.runtime, "session_id": result.session_id,
            "answer": receipt["directory"] + "/answer.md",
            "events": receipt["directory"] + (
                "/response.json" if receipt.get("mode", run.mode) == "chat" else "/codex.events.jsonl"
            ),
        }
        error = None
        if receipt["role"] == "research":
            worker = team.workers[receipt["worker_id"]]
            worker.turns += int(result.invoked)
            worker.state = "completed" if result.status == BackendStatus.COMPLETED else "interrupted"
            board_key = self.coordinator.publish_result(run, receipt, board)
            signal = {
                "task_id": task_id, "worker_id": worker.id, "group": receipt["group"],
                "status": "unsolved", "summary": receipt.get("checkpoint_error") or result.error
                or "Attempt returned without a candidate.", "answer": history["answer"],
                "candidate_id": None,
                "board_key": board_key,
            }
            if result.status == BackendStatus.COMPLETED and receipt.get("milestone"):
                milestone = validate_milestone(
                    run.model_copy(update={"task_id": task_id}), receipt["milestone"]
                )
                history["milestone"] = milestone.model_dump(mode="json")
                signal["summary"] = milestone.summary
                if milestone.kind == "candidate":
                    candidate = self.engine._candidate(run, milestone.candidate)
                    signal["candidate_id"] = candidate.id
                    signal["status"] = "claimed_complete" if claims_complete(candidate) else "partial"
            state.signals.append(signal)
            # Review is a separate checkpoint, even for a COMPLETE solver claim.
            state.review_requested = True
        elif result.status == BackendStatus.COMPLETED:
            try:
                decision = parse_supervision(result.text, run, receipt, config)
                self.apply_decision(run, receipt, decision, config, board)
                history["supervision"] = decision.model_dump(mode="json")
            except ValueError as exc:
                error = f"Supervision needs correction: {exc}"
        else:
            state.review_requested = True
        if result.status != BackendStatus.COMPLETED and not receipt.get("recovered"):
            error = result.error or str(result.status)
        state.processed_tasks.append(task_id)
        team.active_attempts = [a for a in team.active_attempts if a["task_id"] != task_id]
        run.native.history.append(history)
        if result.status == BackendStatus.COMPLETED:
            self.coordinator.runner._record_tool_observations(run, result, receipt)
        run.last_error = error
        # The receipt, usage, signal, decision and active-attempt removal commit together.
        self.store.save(run, "solve_signal_recorded", task_id=task_id, role=receipt["role"], error=error)
        return error

    def apply_decision(self, run, attempt, decision, config, board):
        team, state = run.native.solve_team, run.native.solve_team.campaign
        candidates = {c.id: c for c in run.candidates}
        submitted = {r.candidate_id: r for r in decision.solution_reviews}
        required = {
            s["candidate_id"] for s in state.signals
            if s["task_id"] in attempt["signal_ids"] and s["status"] == "claimed_complete"
        }
        if not required <= submitted.keys():
            raise ValueError("Review every complete solution signal before assigning more research")
        if not set(attempt.get("board_review_keys", [])) <= {r.key for r in decision.board_reviews}:
            raise ValueError("Review each queued board theorem; use needs_work when evidence is insufficient")
        closing = attempt["purpose"] == "closing"
        if not closing and not decision.groups:
            raise ValueError("Supply research routes; only the scheduler ends research admissions")
        # Validate all exact candidate versions before recording any acceptance.
        for review in decision.solution_reviews:
            candidate = candidates.get(review.candidate_id)
            if (candidate is None or candidate.sha256 != review.candidate_sha256
                    or attempt["candidate_hashes"].get(candidate.id) != candidate.sha256):
                raise ValueError("Solution review references a different candidate version")
            if review.verdict == "accepted" and not claims_complete(candidate):
                raise ValueError("A partial/conditional candidate cannot be accepted as a full solution")
        for review in decision.board_reviews:
            board.review(review, attempt["task_id"], snapshot_hashes=attempt["board_hashes"])
        messages = {m["key"]: m for m in board.messages()}
        new_reviews = []
        for review in decision.solution_reviews:
            if any(key not in messages for key in review.depends_on):
                raise ValueError("Solution review references an unknown board prerequisite")
            if review.verdict == "accepted" and any(
                messages[key]["standing"] != "supervisor_accepted" for key in review.depends_on
            ):
                raise ValueError("Accept board prerequisites before accepting a dependent solution")
            sources = [s["board_key"] for s in state.signals if s["candidate_id"] == review.candidate_id
                       and s.get("board_key")]
            if review.verdict == "accepted" and any(
                messages[key]["standing"] in {"retracted", "needs_recheck", "supervisor_rejected"}
                for key in sources
            ):
                raise ValueError("The submitted proof was challenged; request a corrected candidate")
            new_reviews.append({
                **review.model_dump(mode="json"), "task_id": attempt["task_id"], "time": now(),
                "dependency_reviews": {
                    key: (messages[key].get("supervisor_review") or {}).get("id")
                    for key in review.depends_on
                },
                "source_keys": sources,
            })
        state.candidate_reviews.extend(new_reviews)
        state.acknowledged_signals = list(dict.fromkeys([
            *state.acknowledged_signals, *attempt["signal_ids"],
        ]))
        state.decisions.append({"task_id": attempt["task_id"], "purpose": attempt["purpose"],
                                "rationale": decision.rationale, "summary": decision.summary})
        state.summary = decision.summary
        state.last_review_elapsed = budget.elapsed(run)
        state.review_requested = any(
            s["task_id"] not in state.acknowledged_signals for s in state.signals
        )
        team.decision, team.groups = decision.rationale, decision.groups or team.groups
        # When all researchers have already returned, this successful review's
        # required synthesis is also the closing report; do not buy a redundant turn.
        state.closed = closing or bool(
            self.accepted(run, board) and not config.budget.solve_until_budget_exhausted
            and not state.review_requested
            and not any(a["task_id"] != attempt["task_id"] for a in team.active_attempts)
        )
        # Publish the synthesis itself; failed routes become accessible next-turn evidence.
        from mathlottery.solve.board import Message

        workspace = self.coordinator.path(run, attempt["workspace"])
        board.publish("supervisor", "supervision", Message(
            id=attempt["task_id"], kind="result", title="Supervisor synthesis",
            body=decision.summary,
        ), workspace)
        state.dispatch = []
        if not state.closed:
            # Do not mutate busy workers' assignments in the authoritative checkpoint.
            snapshot = run.model_copy(deep=True)
            for worker in self.coordinator.selected_workers(snapshot, config, config.solve.parallel_agents):
                existing = team.workers.get(worker.id)
                if existing is None or existing.state != "running":
                    team.workers[worker.id] = worker
                    state.dispatch.append(worker.id)
            team.rounds += 1

    def accepted(self, run, board):
        state = run.native.solve_team.campaign
        latest = {r["candidate_id"]: r for r in state.candidate_reviews}
        messages = {m["key"]: m for m in board.messages()}
        for candidate in reversed(run.candidates):
            review = latest.get(candidate.id)
            if not review or review["verdict"] != "accepted":
                continue
            if candidate.sha256 != review["candidate_sha256"]:
                continue
            if any(messages[key]["standing"] in {"retracted", "needs_recheck", "supervisor_rejected"}
                   for key in review.get("source_keys", [])):
                continue
            if all(
                messages[key]["standing"] == "supervisor_accepted"
                and (messages[key].get("supervisor_review") or {}).get("id") == version
                for key, version in review["dependency_reviews"].items()
            ):
                return candidate.id
        return None

    def summarize(self, run, board):
        state = run.native.solve_team.campaign
        state.accepted_candidate_id = self.accepted(run, board)
        state.summary_path = "solve/summary.md"
        status = "Supervisor accepted a complete claim" if state.accepted_candidate_id else (
            "Partial results; original problem not accepted as solved" if run.candidates
            else "Original problem not solved in this run"
        )
        text = f"# Solve research summary\n\n{status}.\n\n"
        text += "Supervisor opinions are Solve research, not independent Verify or formal/novelty certification.\n\n"
        text += f"## Original problem\n\n{run.problem.statement}\n\n## Synthesis\n\n{state.summary}\n\n"
        text += "## Attempts and remaining work\n\n" + "\n".join(
            f"- {s['worker_id']}: {s['status']} — {s['summary']} ({s['answer']})" for s in state.signals
        )
        text += "\n\n## Evidence\n\nSee workspace/bulletin/graph.json and the linked immutable messages/materials.\n"
        theorems = [m for m in board.messages() if m.get("theorem")]
        if theorems:
            text += "\nBoard theorem opinions (unreviewed entries remain untrusted):\n\n" + "\n".join(
                f"- {m['key']}: {m['standing']} — {m['title']}" for m in theorems
            ) + "\n"
        atomic_write(self.coordinator.path(run, state.summary_path), text)
        atomic_write(self.coordinator.path(run, "solve/supervision.json"), json_text(state))
