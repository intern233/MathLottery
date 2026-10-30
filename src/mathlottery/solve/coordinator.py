"""Owner-thread Solve orchestration and checkpoint accounting.

Allocation, prompts, durable transport calls, and board storage are separate
components. Backend threads only return receipts; the owner thread coordinates
checkpoint mutations, accounting, and resizing between natural milestones.
"""

from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor, wait

from mathlottery.models import CandidateInput, SolveGroup, State, digest
from mathlottery.providers.base import BackendResult, BackendStatus
from mathlottery.runtime import budget
from mathlottery.runtime.workflows import claims_complete
from mathlottery.solve.allocation import parse_allocation, selected_workers
from mathlottery.solve.attempts import SolveAttempts
from mathlottery.solve.board import Message, SolveBoard
from mathlottery.solve.prompts import SolvePrompts
from mathlottery.storage.core import atomic_write, json_text, safe_path


class SolveCoordinator:
    def __init__(self, runner):
        self.runner, self.engine, self.store = runner, runner.engine, runner.store
        self.abort = threading.Event()
        self.attempts = SolveAttempts(self.engine, self.abort)
        self.prompts = SolvePrompts(self.store)

    def path(self, run, relative):
        return self.attempts.path(run, relative)

    def closing_context(self, run):
        return self.prompts.closing_context(run)

    def prepare_attempt(self, run, worker=None):
        return self.attempts.prepare(run, worker)

    def selected_workers(self, run, config, slots):
        return selected_workers(run, config, slots)

    def researcher_prompt(self, run, worker, attempt, config, board):
        return self.prompts.researcher(run, worker, attempt, config, board)

    def consume_supervisor(self, run, receipt, config):
        team = run.native.solve_team
        result = BackendResult(**receipt["result"])
        self.attempts.remember(run, receipt)
        if not result.pending:
            self.engine._account(run, result)
            counter = run.model_copy(update={"usage": team.supervisor_usage})
            self.engine._account(counter, result)
            if result.invoked:
                run.iteration += 1
        entry = {
            **receipt,
            "phase": "SOLVE",
            "mode": receipt.get("mode", run.mode),
            "status": result.status,
            "usage": result.usage,
            "runtime": result.runtime,
            "session_id": result.session_id,
            "answer": receipt["directory"] + "/answer.md",
            "events": receipt["directory"]
            + ("/response.json" if receipt.get("mode", run.mode) == "chat" else "/codex.events.jsonl"),
        }
        entry.pop("result")
        entry.pop("milestone", None)
        run.native.history.append(entry)
        if not result.pending:
            team.active_attempts = [
                a for a in team.active_attempts if a["task_id"] != receipt["task_id"]
            ]
        if result.status == BackendStatus.COMPLETED:
            try:
                plan = parse_allocation(
                    result.text, run_id=run.id, task_id=receipt["task_id"], settings=config.solve
                )
                team.groups, team.decision = plan.groups, plan.rationale
            except ValueError as error:
                team.decision = f"Allocation rejected; retain a bounded existing plan: {error}"
        self.store.save(
            run, "solve_supervision_recorded", status=result.status, decision=team.decision
        )
        if self.engine._stop_file(run).exists():
            self.engine._pause(run, "Stopped by user", State.CANCELLED)
            return False
        if result.status == BackendStatus.INTERRUPTED and not result.pending:
            # An advisory planning timeout must not end the underlying research budget.
            team.decision = "Supervision interrupted; continue with the bounded saved allocation."
            self.store.save(run, "solve_supervision_deferred")
            return True
        if result.status != BackendStatus.COMPLETED and not receipt.get("recovered"):
            run.last_error = result.error
            state = (
                State.RATE_LIMITED if result.status == BackendStatus.RATE_LIMITED else State.PAUSED
            )
            self.engine._pause(run, result.error or "Solve supervision interrupted", state)
            return False
        return True

    def poll(self, run, attempts, board):
        changed = False
        for attempt in attempts:
            changed = self.attempts.remember(run, attempt) or changed
            if attempt["role"] != "research":
                continue
            workspace = self.path(run, attempt["workspace"])
            published, errors = board.ingest(attempt["worker_id"], attempt["group"], workspace)
            changed = published or changed
            atomic_write(
                safe_path(workspace, "bulletin/publication-errors.json"), json_text(errors)
            )
        if changed:
            for attempt in attempts:
                board.project(self.path(run, attempt["workspace"]))
            self.store.save(run, "solve_board_updated")

    def publish_result(self, run, receipt, board):
        result = BackendResult(**receipt["result"])
        if not result.text.strip():
            return
        worker = run.native.solve_team.workers[receipt["worker_id"]]
        milestone = receipt.get("milestone") or {}
        workspace = self.path(run, receipt["workspace"])
        version = digest(result.text + str(result.status) + json_text(milestone))[:12]
        publication_id = f"{receipt['task_id']}-{version}"
        artifact = f"shared-checkpoints/{publication_id}.md"
        atomic_write(safe_path(workspace, artifact), result.text)
        board.publish(
            worker.id,
            worker.group,
            Message(
                id=publication_id,
                kind="result",
                title=milestone.get("summary", "")[:300] or "Research checkpoint",
                body=(milestone.get("summary") or "Full saved research answer attached.")[:30000],
                artifacts=[artifact] if len(result.text.encode()) <= 2_000_000 else [],
            ),
            workspace,
        )
        target = self.path(run, f"workspace/research-history/{receipt['task_id']}.md")
        atomic_write(target, result.text)

    def stage(self, run, receipts, board):
        team = run.native.solve_team
        for receipt in receipts:
            self.attempts.remember(run, receipt)
            result = BackendResult(**receipt["result"])
            worker = team.workers[receipt["worker_id"]]
            worker.state = (
                "completed" if result.status == BackendStatus.COMPLETED else "interrupted"
            )
            self.publish_result(run, receipt, board)

        def order(receipt):
            if receipt["result"]["status"] != BackendStatus.COMPLETED:
                return 3 if receipt["result"]["status"] == BackendStatus.RATE_LIMITED else 2
            milestone = receipt.get("milestone") or {}
            return int(
                bool(
                    milestone.get("conclude")
                    and milestone.get("candidate")
                    and claims_complete(CandidateInput.model_validate(milestone["candidate"]))
                )
            )

        # Apply all research before accepting a complete claim; failures are retained last.
        team.pending_receipts.extend(sorted(receipts, key=order))
        team.active_attempts = [
            a
            for a in team.active_attempts
            if any(r["task_id"] == a["task_id"] and r["result"].get("pending") for r in receipts)
        ]
        self.store.save(run, "solve_round_received", receipts=len(receipts))

    def queue_next(self, run):
        receipt = run.native.solve_team.pending_receipts.pop(0)
        run.task_id = receipt["task_id"]
        if receipt["result"].get("invoked") and not receipt["result"].get("pending"):
            run.native.solve_team.workers[receipt["worker_id"]].turns += 1
        # The pop, accounting and pending receipt are committed in one checkpoint.
        self.runner.queue(run, receipt)

    def recover(self, run, config):
        attempts = list(run.native.solve_team.active_attempts)
        if not attempts:
            return True
        board, receipts = SolveBoard(self.store, run.id), []
        for attempt in attempts:
            receipt = self.attempts.recover(run, attempt, config)
            if attempt["role"] == "supervision":
                if not self.consume_supervisor(run, receipt, config):
                    return False
            else:
                receipts.append(receipt)
        if receipts:
            self.poll(run, [a for a in attempts if a["role"] == "research"], board)
            self.stage(run, receipts, board)
        return True

    def round(self, run, config):
        self.abort.clear()
        team = run.native.solve_team
        board = SolveBoard(self.store, run.id)
        # Existing context/dossiers remain projected by the ordinary native workspace.
        self.runner.prepare(run, config)
        slots = config.budget.max_iterations - run.iteration
        if slots > 1:
            attempt = self.prepare_attempt(run)
            board.project(self.path(run, attempt["workspace"]))
            prompt = self.prompts.supervisor(run, attempt, config, board)
            receipt = self.attempts.invoke(run, attempt, prompt, config)
            if not self.consume_supervisor(run, receipt, config):
                return False
        if budget.exhausted(run, config) or self.engine._stop_file(run).exists():
            return True
        workers = self.selected_workers(run, config, config.budget.max_iterations - run.iteration)
        actual_groups = {}
        for worker in workers:
            if worker.group not in actual_groups:
                actual_groups[worker.group] = SolveGroup(
                    id=worker.group, agents=1, mode=worker.mode, objective=worker.objective
                )
            else:
                actual_groups[worker.group].agents += 1
        team.groups = list(actual_groups.values())
        attempts, prompts = [], []
        for worker in workers:
            attempt = self.prepare_attempt(run, worker)
            attempts.append(attempt)
            board.project(self.path(run, attempt["workspace"]))
            prompts.append(self.researcher_prompt(run, worker, attempt, config, board))
        team.rounds += 1
        self.store.save(run, "solve_round_started", researchers=len(workers))
        pool = ThreadPoolExecutor(max_workers=len(workers), thread_name_prefix="solve")
        futures = []
        try:
            futures = [
                pool.submit(self.attempts.invoke, run, attempt, prompt, config)
                for attempt, prompt in zip(attempts, prompts, strict=True)
            ]
            pending = set(futures)
            while pending:
                done, pending = wait(pending, timeout=0.5)
                for future in done:
                    receipt = future.result()
                    self.publish_result(run, receipt, board)
                    worker = team.workers[receipt["worker_id"]]
                    worker.state = (
                        "completed"
                        if receipt["result"]["status"] == BackendStatus.COMPLETED
                        else "interrupted"
                    )
                    if receipt["result"]["status"] != BackendStatus.COMPLETED:
                        self.abort.set()
                if done:
                    for attempt in attempts:
                        board.project(self.path(run, attempt["workspace"]))
                    self.store.save(run, "solve_agents_returned", count=len(done))
                self.poll(run, attempts, board)
            self.stage(run, [f.result() for f in futures], board)
        finally:
            # Do not release slots while children are still running, including Ctrl-C.
            self.abort.set()
            pool.shutdown(wait=True, cancel_futures=True)
        return True
