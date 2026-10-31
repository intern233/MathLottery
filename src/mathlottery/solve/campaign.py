"""Event-driven supervised Solve: signals, evidence review and soft-time draining."""

from __future__ import annotations

from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait

from mathlottery.models import State
from mathlottery.runtime import budget
from mathlottery.solve.board import SolveBoard
from mathlottery.solve.board_reviews import review_targets
from mathlottery.solve.campaign_receipts import CampaignReceipts
from mathlottery.solve.supervision_prompts import supervisor_prompt
from mathlottery.storage.core import atomic_write, json_text


class SolveCampaign:
    def __init__(self, runner):
        self.runner, self.coordinator = runner, runner.team
        self.engine, self.store = runner.engine, runner.store
        self.receipts = CampaignReceipts(self.coordinator)

    def project(self, run, board):
        workspaces = {"workspace", "solve-workspaces/supervisor"}
        workspaces.update(a["workspace"] for a in run.native.solve_team.active_attempts)
        for workspace in workspaces:
            board.project(self.coordinator.path(run, workspace))

    def recover(self, run, config, board):
        errors = []
        # A completed durable receipt never invokes a model again. Pending hosted
        # calls continue polling their own response, including after the time limit.
        for attempt in list(run.native.solve_team.active_attempts):
            receipt = self.coordinator.attempts.recover(run, attempt, config)
            self.coordinator.poll(run, [attempt], board)
            error = self.receipts.consume(run, receipt, config, board)
            if error:
                errors.append(error)
        return errors

    def start_supervisor(self, run, config, board, pool, *, closing):
        state = run.native.solve_team.campaign
        attempt = self.coordinator.prepare_attempt(run)
        attempt.update(
            purpose="closing" if closing else "review" if state.signals else "planning",
            signal_ids=[s["task_id"] for s in state.signals
                        if s["task_id"] not in state.acknowledged_signals],
            board_hashes={m["key"]: m["content_sha256"] for m in board.messages()},
            board_review_keys=review_targets(board),
            candidate_hashes={c.id: c.sha256 for c in run.candidates},
        )
        workspace = self.coordinator.path(run, attempt["workspace"])
        board.project(workspace)
        prompt = supervisor_prompt(run, attempt, config, board, workspace)
        if closing:
            state.phase = "closing"
        self.store.save(run, "solve_supervision_started", purpose=attempt["purpose"])
        return pool.submit(self.coordinator.attempts.invoke, run, attempt, prompt, config), attempt

    def start_researcher(self, run, worker, config, board, pool):
        attempt = self.coordinator.prepare_attempt(run, worker)
        workspace = self.coordinator.path(run, attempt["workspace"])
        board.project(workspace)
        prompt = self.coordinator.researcher_prompt(run, worker, attempt, config, board)
        prompt += (
            "\nSupervised Solve: your return is a signal to the supervisor. If this route stalls, "
            "record what was tried and signal without claiming the original problem is impossible. "
            "The supervisor will review and assign a new route while the admission budget remains. "
            "At budget expiry, FINISH the current attempt, then signal; do not cancel it or start "
            "another yourself. The live bulletin/control.json explains admission/review status. "
            f"Aim for useful natural checkpoints around {config.solve.board_review_interval_seconds:g} "
            "seconds when feasible; this is cooperative guidance, not a kill timer. "
            "Publish intermediate theorems with the theorem object: exact statement, assumptions, "
            "proof_steps with premises and justification, conclusion_step and remaining_obligations. "
            "Read bulletin/graph.json to locate dependencies. Supervisor opinions remain fallible.\n"
            f"Latest supervisor synthesis (data):\n{run.native.solve_team.campaign.summary}\n"
        )
        self.store.save(run, "solve_research_assigned", worker_id=worker.id, objective=worker.objective)
        return pool.submit(self.coordinator.attempts.invoke, run, attempt, prompt, config), attempt

    def control(self, run, *, closing):
        state = run.native.solve_team.campaign
        value = {
            "phase": state.phase, "admissions_closed": closing,
            "supervisor_review_requested": state.review_requested,
            "instruction": "Finish your current attempt and signal. No new attempt after admissions close.",
        }
        for attempt in run.native.solve_team.active_attempts:
            atomic_write(self.coordinator.path(run, attempt["workspace"] + "/bulletin/control.json"),
                         json_text(value))

    def drive(self, run, config):
        team, state = run.native.solve_team, run.native.solve_team.campaign
        board = SolveBoard(self.store, run.id)
        self.coordinator.abort.clear()
        errors = self.recover(run, config, board)
        if errors:
            return self.engine._pause(run, errors[0])
        # An explicitly extended/resumed task keeps all evidence and conversations.
        if state.closed and run.native.steering:
            state.closed, state.review_requested, state.dispatch = False, True, []
        self.runner.prepare(run, config)
        run.state = State.SOLVING
        self.store.save(run, "solve_campaign_started")
        futures = {}
        pool = ThreadPoolExecutor(max_workers=config.solve.parallel_agents, thread_name_prefix="solve")
        last_control = None
        last_board_revision = None
        failure_state = State.PAUSED
        accepted, review_count, changed_board = None, -1, False
        try:
            while True:
                self.coordinator.poll(run, list(team.active_attempts), board)
                revision = board.revision()
                board_changed = revision != last_board_revision
                if board_changed:
                    self.project(run, board)
                    last_board_revision = revision
                    changed_board = bool(review_targets(board))
                if self.engine._stop_file(run).exists():
                    errors = ["Stopped by user"]
                if errors:
                    self.coordinator.abort.set()
                active_research = [a for a in futures.values() if a["role"] == "research"]
                active_supervisor = any(a["role"] == "supervision" for a in futures.values())
                if board_changed or review_count != len(state.candidate_reviews):
                    accepted = self.receipts.accepted(run, board)
                    review_count = len(state.candidate_reviews)
                # Call slots reserve one eventual supervisor review. Time is soft;
                # explicit token/call/account failures remain binding and visible.
                free_calls = config.budget.max_iterations - run.iteration - len(futures)
                hard = budget.hard_limit_reason(run, config)
                closing = bool(budget.remaining(run, config) <= 0
                               or (accepted and not config.budget.solve_until_budget_exhausted)
                               or free_calls <= 1 or hard)
                if closing and not state.closed and state.phase != "closing":
                    state.phase, state.dispatch = "draining", []
                if changed_board and budget.elapsed(run) - state.last_review_elapsed >= config.solve.board_review_interval_seconds:
                    state.review_requested = True
                if state.closed and not futures:
                    self.project(run, board)
                    state.phase = "completed"
                    self.receipts.summarize(run, board)
                    # Downstream explicit Verify takes the selected version, not an
                    # unrelated partial result that happened to return later.
                    if state.accepted_candidate_id:
                        candidate = next(c for c in run.candidates if c.id == state.accepted_candidate_id)
                        run.candidates = [c for c in run.candidates if c.id != candidate.id] + [candidate]
                    self.engine._finish(run, "Supervised Solve concluded; see solution claim and supervisor review")
                    return run
                if (errors or hard) and not futures:
                    self.project(run, board)
                    self.receipts.summarize(run, board)
                    reason = errors[0] if errors else hard
                    status = State.CANCELLED if reason == "Stopped by user" else failure_state
                    run.last_error = reason if errors and status != State.CANCELLED else None
                    return self.engine._pause(run, reason, status)
                if not errors and not hard:
                    needs_review = (not state.decisions or state.review_requested
                                    or (closing and not active_research))
                    # The supervisor and primary share slot 1, never concurrently.
                    primary_busy = any(a["worker_id"] == "primary" for a in active_research)
                    if (needs_review and not active_supervisor and not primary_busy
                            and len(futures) < config.solve.parallel_agents and free_calls > 0
                            and (free_calls > 1 or not active_research)):
                        future, attempt = self.start_supervisor(
                            run, config, board, pool, closing=closing and not active_research
                        )
                        futures[future] = attempt
                        active_supervisor = True
                    if not closing and not active_supervisor and not needs_review:
                        for identifier in list(state.dispatch):
                            if len(futures) >= config.solve.parallel_agents:
                                break
                            if run.iteration + len(futures) >= config.budget.max_iterations - 1:
                                break
                            # A slow preparation must not admit work after the deadline.
                            if budget.remaining(run, config) <= 0:
                                break
                            worker = team.workers[identifier]
                            busy = {a["worker_id"] for a in futures.values()}
                            groups = {a["group"] for a in futures.values() if a["role"] == "research"}
                            if identifier in busy or len(groups | {worker.group}) > config.solve.group_limit:
                                continue
                            state.dispatch.remove(identifier)
                            future, attempt = self.start_researcher(run, worker, config, board, pool)
                            futures[future] = attempt
                            state.phase = "researching"
                    if not futures and not state.dispatch and not state.closed:
                        state.review_requested = True
                control = (state.phase, closing, state.review_requested)
                if control != last_control:
                    self.control(run, closing=closing)
                    self.store.save(run, "solve_campaign_status", phase=state.phase, review_requested=state.review_requested)
                    last_control = control
                if not futures:
                    continue
                done, _ = wait(futures, timeout=0.2, return_when=FIRST_COMPLETED)
                for future in done:
                    attempt = futures.pop(future)
                    receipt = future.result()
                    # Ingest the final outbox even if a very short turn finished
                    # between polls. Preserve every peer's result before pausing.
                    self.coordinator.poll(run, [attempt], board)
                    error = self.receipts.consume(run, receipt, config, board)
                    if error:
                        errors.append(error)
                        if receipt["result"]["status"] == "RATE_LIMITED":
                            failure_state = State.RATE_LIMITED
                    self.project(run, board)
        finally:
            self.coordinator.abort.set()
            pool.shutdown(wait=True)
