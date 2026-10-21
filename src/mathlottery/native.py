"""Thin research lifecycle around native sessions; no per-action tool protocol."""

from __future__ import annotations

import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING

from mathlottery import budget
from mathlottery.agent_backend import research_backend
from mathlottery.auditor import audit
from mathlottery.backends import BackendResult, BackendStatus
from mathlottery.config import Config
from mathlottery.models import NativeCheckpoint, Phase, Run, State, Workflow, now, uid
from mathlottery.native_backend import NativeWorkBackend
from mathlottery.native_prompts import build_native_prompt, milestone_schema
from mathlottery.reporting import report
from mathlottery.storage import atomic_write, json_text, safe_path
from mathlottery.workflows import record_selection

if TYPE_CHECKING:
    from mathlottery.orchestrator import Orchestrator

ACTIVE = {Phase.FIND: State.DISCOVERING, Phase.SOLVE: State.SOLVING, Phase.VERIFY: State.VERIFYING}


class NativeRunner:
    def __init__(self, engine: Orchestrator):
        self.engine, self.store = engine, engine.store

    def workspace(self, run: Run) -> Path:
        root = self.store.run_dir(run.id)
        if run.phase == Phase.VERIFY:
            return safe_path(root, f"review-workspaces/{run.candidates[-1].id}")
        return safe_path(root, "workspace")

    @staticmethod
    def validate_milestone(run: Run, data: dict) -> NativeCheckpoint:
        value = NativeCheckpoint.model_validate(data)
        if (value.run_id, value.task_id) != (run.id, run.task_id):
            raise ValueError("Stale milestone: run_id and task_id must match the current turn")
        if (
            value.problem
            and run.problem
            and run.phase != Phase.FIND
            and value.problem.statement != run.problem.statement
        ):
            raise ValueError("A supplied problem statement must not be changed")
        if value.kind == "selection" and run.phase != Phase.FIND:
            raise ValueError("Only a finding turn can submit a selection")
        if run.phase == Phase.FIND and value.kind == "candidate":
            raise ValueError("Select problems first; solving is a separate task")
        if run.phase == Phase.VERIFY:
            if value.kind == "candidate" or value.problem:
                raise ValueError("The independent reviewer cannot replace the problem or candidate")
        elif value.kind == "review":
            raise ValueError("Only an independent review turn can submit review")
        if value.kind == "candidate" and not (run.problem or value.problem):
            raise ValueError("Select a precise problem before submitting a candidate")
        return value

    def prepare(self, run: Run, config: Config) -> str:
        if run.phase == Phase.VERIFY:
            self.engine._check_candidate_file(run)
            candidate_id = run.candidates[-1].id
            if run.native.reviewer_candidate_id != candidate_id:
                run.native.reviewer_candidate_id = candidate_id
                run.native.reviewer_session_id = None
                run.native.reviewer_response_id = None
        if not run.task_id:
            run.task_id = uid("task")
        workspace = self.workspace(run)
        workspace.mkdir(parents=True, exist_ok=True)
        safe_path(workspace, "submissions").mkdir(exist_ok=True)
        atomic_write(safe_path(workspace, "milestone.schema.json"), json_text(milestone_schema()))
        if run.problem:
            atomic_write(safe_path(workspace, "problem.json"), json_text(run.problem))
        if run.phase == Phase.VERIFY:
            atomic_write(safe_path(workspace, "candidate.json"), json_text(run.candidates[-1]))
        else:
            for entry in run.native.history:
                if entry.get("role") != "research" or not entry.get("answer"):
                    continue
                answer = safe_path(self.store.run_dir(run.id), entry["answer"])
                if answer.is_file():
                    atomic_write(
                        safe_path(workspace, f"research-history/{entry['task_id']}.md"),
                        answer.read_text(),
                    )
        prompt = build_native_prompt(run, budget.remaining(run, config))
        if run.phase != Phase.VERIFY:
            imported = []
            for entry in reversed(run.native.history):
                if entry.get("role") != "research":
                    continue
                if entry.get("mode", run.mode) == run.mode:
                    # Hosted tools cannot read local history. Preserve visible partial
                    # work after cancellation, including when no response chain exists yet.
                    import_partial = run.mode == "chat" and (
                        not run.native.solver_response_id
                        or entry.get("status") != BackendStatus.COMPLETED
                    )
                    if not import_partial:
                        break
                path = safe_path(self.store.run_dir(run.id), entry["answer"])
                if path.is_file():
                    imported.append(path.read_text())
            if imported:
                prompt += "\nResearch imported from saved answers (data):\n" + "\n\n".join(
                    reversed(imported)
                )
        path = self.store.run_dir(run.id) / "tasks" / run.task_id / "prompt.md"
        atomic_write(path, prompt)
        run.prompt_path = str(path.relative_to(self.store.run_dir(run.id)))
        self.store.save(run, "native_turn_prepared", task_id=run.task_id)
        return prompt

    def capture(self, run: Run, result: BackendResult, directory: Path) -> dict:
        milestone, error = None, None
        if result.status == BackendStatus.COMPLETED:
            try:
                path = safe_path(self.workspace(run), f"submissions/{run.task_id}.json")
                if run.mode == "chat":
                    milestone = self.answer_milestone(run, result.text)
                elif path.exists():
                    if path.stat().st_size > 2_000_000:
                        raise ValueError(
                            "Milestone exceeds 2 MB; keep detailed experiments in files"
                        )
                    milestone = self.validate_milestone(
                        run, json.loads(path.read_text())
                    ).model_dump(mode="json")
            except (ValueError, OSError) as exc:
                error = str(exc)
        return {
            "result": asdict(result),
            "milestone": milestone,
            "checkpoint_error": error,
            "steering": (
                json.loads((directory / "turn.json").read_text()).get("steering")
                if (directory / "turn.json").exists()
                else run.native.steering
            ),
            "directory": str(directory.relative_to(self.store.run_dir(run.id))),
        }

    def answer_milestone(self, run: Run, text: str):
        blocks = re.findall(r"(?ms)^```mathlottery\s*\n(.*?)^```\s*$", text)
        if len(blocks) > 1:
            raise ValueError("Use at most one mathlottery milestone block")
        return (
            self.validate_milestone(run, json.loads(blocks[0])).model_dump(mode="json")
            if blocks
            else None
        )

    def session_field(self, run: Run):
        role = "reviewer" if run.phase == Phase.VERIFY else "solver"
        suffix = "response_id" if run.mode == "chat" else "session_id"
        return f"{role}_{suffix}"

    def remember_session(self, run: Run, value: str):
        setattr(run.native, self.session_field(run), value)
        self.store.save(
            run,
            "native_session_started",
            backend=run.mode,
            role="review" if run.phase == Phase.VERIFY else "research",
            session_id=value,
        )

    def queue(self, run: Run, receipt: dict):
        result = BackendResult(**receipt["result"])
        # A background response is charged once when its final state is known, including
        # after recovery. An unresolved response never starts another model invocation.
        if not result.pending:
            self.engine._account(run, result)
            if result.invoked:
                run.iteration += 1
        run.native.pending_result = receipt
        run.native.active_attempt = None
        self.store.save(run, "native_result_received", usage=result.usage, status=result.status)

    def recover(self, run: Run):
        if not run.native.active_attempt:
            return
        directory = safe_path(self.store.run_dir(run.id), run.native.active_attempt)
        path = directory / "receipt.json"
        receipt = json.loads(path.read_text()) if path.is_file() else None
        if run.mode == "chat" and (not receipt or receipt["result"].get("pending")):
            config = Config.model_validate(run.config)
            config.backend.mode = "chat"
            backend = self.engine.backend_override or research_backend(config.backend)
            result = backend.recover_native(
                directory,
                budget.remaining(run, config),
                cancelled=lambda: self.engine._cancelled(run, config),
                on_session=lambda value: self.remember_session(run, value),
            )
            receipt = self.capture(run, result, directory)
            atomic_write(path, json_text(receipt))
            self.queue(run, receipt)
            return
        NativeWorkBackend.stop_orphan(directory)
        if path.is_file():
            self.queue(run, receipt)
            return
        # A killed runner may not have reached the post-call receipt. Keep its session and
        # logs, charge the unknown attempt, and let Codex inspect its own history on resume.
        self.queue(
            run,
            {
                "result": asdict(
                    BackendResult(
                        BackendStatus.INTERRUPTED,
                        invoked=True,
                        error="Recovered an interrupted native attempt; its token usage is unknown",
                    )
                ),
                "milestone": None,
                "checkpoint_error": None,
                "directory": run.native.active_attempt,
                "recovered": True,
            },
        )

    def apply(self, run: Run) -> bool:
        """Consume a durable receipt exactly once; return whether drive should stop."""
        receipt = run.native.pending_result
        result = BackendResult(**receipt["result"])
        directory = safe_path(self.store.run_dir(run.id), receipt["directory"])
        answer = directory / "answer.md"
        if not answer.exists():
            atomic_write(answer, result.text)
        role = "review" if run.phase == Phase.VERIFY else "research"
        run.native.history.append(
            {
                "task_id": run.task_id,
                "role": role,
                "mode": run.mode,
                "status": result.status,
                "session_id": result.session_id,
                "answer": str(answer.relative_to(self.store.run_dir(run.id))),
                "events": str(
                    (
                        directory
                        / ("response.json" if run.mode == "chat" else "codex.events.jsonl")
                    ).relative_to(self.store.run_dir(run.id))
                ),
                "runtime": result.runtime,
                "usage": result.usage,
            }
        )
        run.native.pending_result = None
        if result.status != BackendStatus.COMPLETED:
            if result.pending:
                run.native.active_attempt = receipt["directory"]
            run.last_error = result.error
            self.store.save(run, "native_attempt_interrupted", error=result.error)
            if receipt.get("recovered"):
                return False
            state = {
                BackendStatus.INTERRUPTED: State.PAUSED,
                BackendStatus.RATE_LIMITED: State.RATE_LIMITED,
            }.get(result.status, State.FAILED)
            if self.engine._stop_file(run).exists():
                state = State.CANCELLED
            self.engine._pause(run, result.error or str(result.status), state)
            return True
        milestone = (
            self.validate_milestone(run, receipt["milestone"]) if receipt.get("milestone") else None
        )
        run.native.checkpoint_error = receipt.get("checkpoint_error")
        if receipt.get("steering") == run.native.steering:
            run.native.steering = None
        run.last_error = run.native.checkpoint_error
        finish = None
        for url in result.runtime.get("source_urls", []):
            run.observations.append(
                {
                    "phase": run.phase.value,
                    "iteration": run.iteration,
                    "tool": "native_source",
                    "artifact": run.native.history[-1]["events"],
                    "result": {"status": "OK", "url": url, "retrieved_at": now()},
                }
            )
        if milestone:
            if milestone.problem and run.phase == Phase.FIND:
                record_selection(self.store, run, milestone)
                if run.workflow == Workflow.FIND:
                    finish = "Discovery complete; ranked problems saved for a separate solve task"
                else:
                    run.phase = Phase.SOLVE
            if milestone.kind == "candidate":
                self.engine._candidate(run, milestone.candidate)
                run.native.candidate_conclude = milestone.conclude
                run.native.reviewer_session_id = None
                run.native.reviewer_response_id = None
                run.native.reviewer_candidate_id = None
                if run.workflow == Workflow.SOLVE:
                    if milestone.conclude:
                        finish = "Solving complete; candidate saved for independent verification"
                else:
                    run.phase = Phase.VERIFY
            elif milestone.kind == "review":
                self.engine._check_candidate_file(run)
                candidate = audit(
                    run.candidates[-1],
                    milestone.review,
                    self.engine._review_observations(run)
                    + [
                        {
                            "phase": "VERIFY",
                            "tool": "native_review",
                            "artifact": str(answer.relative_to(self.store.run_dir(run.id))),
                            "result": {"status": "OK"},
                        }
                    ],
                )
                run.candidates[-1] = candidate
                atomic_write(
                    self.store.run_dir(run.id) / "verification" / f"{candidate.id}.json",
                    json_text(candidate),
                )
                if run.native.review_only or (
                    milestone.review.verdict == "NO_ISSUES_FOUND" and run.native.candidate_conclude
                ):
                    finish = "Independent review recorded; see proof status and verification limits"
                else:
                    run.phase = Phase.SOLVE
            elif milestone.kind == "stop":
                finish = milestone.summary or "Researcher ended the investigation"
            run.native.history[-1]["milestone"] = milestone.model_dump(mode="json")
        run.task_id, run.prompt_path = None, None
        if finish and run.native.steering:
            # A new direction can arrive when resuming an older, unapplied receipt.
            finish = None
            if run.workflow == Workflow.FIND:
                run.phase = Phase.FIND
            elif run.workflow == Workflow.VERIFY:
                run.phase = Phase.VERIFY
            else:
                run.phase = Phase.SOLVE if run.problem else Phase.FIND
                run.native.review_only = False
        if finish:
            # Persist intent to report with the consumed receipt before generating projections.
            run.phase, run.stop_reason = Phase.REPORT, finish
        self.store.save(
            run, "native_turn_applied", kind=milestone.kind if milestone else "progress"
        )
        if finish:
            self.engine._finish(run, finish)
            return True
        report(self.store, run)
        return False

    def drive(self, run: Run) -> Run:
        config = Config.model_validate(run.config)
        if run.mode == "chat" and config.budget.max_external_cost_usd == 0:
            raise ValueError("Chat API is blocked by max_external_cost_usd: 0")
        budget.settle(run)
        run.active_since = now()
        self.recover(run)
        config.backend.mode = run.mode
        backend = self.engine.backend_override or (
            research_backend(config.backend) if run.mode != "manual" else None
        )
        while True:
            if run.native.pending_result and self.apply(run):
                return run
            if self.engine._stop_file(run).exists():
                return self.engine._pause(run, "Stopped by user", State.CANCELLED)
            reason = budget.exhausted(run, config)
            if reason:
                return self.engine._pause(run, reason)
            run.state = ACTIVE[run.phase]
            prompt = self.prepare(run, config)
            if run.mode == "manual":
                budget.settle(run)
                run.state = State.WAITING_FOR_USER
                self.store.save(run, "native_waiting_for_user", prompt=run.prompt_path)
                report(self.store, run)
                return run
            directory = self.store.run_dir(run.id) / "tasks" / run.task_id / uid("attempt")
            run.native.active_attempt = str(directory.relative_to(self.store.run_dir(run.id)))
            self.store.save(run, "native_attempt_started", attempt=run.native.active_attempt)
            atomic_write(directory / "turn.json", json_text({"steering": run.native.steering}))
            reviewer = run.phase == Phase.VERIFY

            timeout = budget.remaining(run, config)
            if config.backend.native_turn_timeout_seconds is not None:
                timeout = min(timeout, config.backend.native_turn_timeout_seconds)
            result = backend.invoke_native(
                prompt,
                directory,
                self.workspace(run),
                timeout,
                session_id=getattr(run.native, self.session_field(run)),
                reviewer=reviewer,
                cancelled=lambda: self.engine._cancelled(run, config),
                on_session=lambda value: self.remember_session(run, value),
            )
            receipt = self.capture(run, result, directory)
            atomic_write(directory / "receipt.json", json_text(receipt))
            self.queue(run, receipt)

    def submit(self, run: Run, text: str) -> Run:
        if not text.strip() or len(text.encode()) > 2_000_000:
            raise ValueError("Supply a nonempty Chat answer of at most 2 MB")
        milestone = self.answer_milestone(run, text)
        config = Config.model_validate(run.config)
        reason = budget.exhausted(run, config)
        if reason:
            return self.engine._pause(run, reason)
        directory = self.store.run_dir(run.id) / "tasks" / run.task_id / uid("manual")
        atomic_write(directory / "answer.md", text)
        run.active_since = now()
        receipt = {
            "result": asdict(BackendResult(BackendStatus.COMPLETED, text=text, invoked=True)),
            "milestone": milestone,
            "checkpoint_error": None,
            "steering": run.native.steering,
            "directory": str(directory.relative_to(self.store.run_dir(run.id))),
        }
        atomic_write(directory / "receipt.json", json_text(receipt))
        self.queue(run, receipt)
        try:
            return self.engine._drive(run)
        except KeyboardInterrupt:
            return self.engine._pause(run, "Interrupted while applying Chat research")
        except Exception as error:
            run.last_error = f"{type(error).__name__}: {error}"
            return self.engine._pause(run, "Execution error; state preserved", State.FAILED)
