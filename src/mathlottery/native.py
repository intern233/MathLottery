"""Thin research lifecycle around native sessions; no per-action tool protocol."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING

from mathlottery import budget, organization
from mathlottery.agent_backend import research_backend
from mathlottery.backends import BackendResult, BackendStatus
from mathlottery.config import Config
from mathlottery.finalization import SolveFinalizer
from mathlottery.finalization import applicable as finalization_applicable
from mathlottery.literature import collect_sources
from mathlottery.milestones import answer_milestone, validate_milestone
from mathlottery.models import Phase, Run, State, Workflow, now, uid
from mathlottery.native_attempts import NativeAttempts
from mathlottery.native_workspace import NativeWorkspace
from mathlottery.reporting import report
from mathlottery.storage import atomic_write, json_text, safe_path
from mathlottery.workflows import ACTIVE, claims_complete, full_solve_budget, record_selection

if TYPE_CHECKING:
    from mathlottery.orchestrator import Orchestrator


class NativeRunner:
    def __init__(self, engine: Orchestrator):
        self.engine, self.store = engine, engine.store
        self.workspaces = NativeWorkspace(self.store, engine.candidates)
        self.attempts = NativeAttempts(engine, self.workspaces)
        self.finalizer = SolveFinalizer(engine)

    def workspace(self, run: Run) -> Path:
        return self.workspaces.path(run)

    validate_milestone = staticmethod(validate_milestone)

    def prepare(self, run: Run, config: Config) -> str:
        return self.workspaces.prepare(run, config)

    answer_milestone = staticmethod(answer_milestone)

    def queue(self, run: Run, receipt: dict):
        self.attempts.queue(run, receipt)

    def recover(self, run: Run):
        self.attempts.recover(run, self.queue)

    def apply(self, run: Run) -> bool:
        """Consume a durable receipt exactly once; return whether drive should stop."""
        receipt = run.native.pending_result
        result = BackendResult(**receipt["result"])
        directory = safe_path(self.store.run_dir(run.id), receipt["directory"])
        answer = directory / "answer.md"
        if not answer.exists():
            atomic_write(answer, result.text)
        milestone = None
        if result.status == BackendStatus.COMPLETED and receipt.get("milestone"):
            milestone = self.validate_milestone(run, receipt["milestone"])
            # Long independent checks precede receipt consumption/history mutation.
            # An interrupt retains the queued model result and must not repeat a model call.
            if milestone.kind == "selection":
                collect_sources(self.store, run, [c for p in milestone.shortlist for c in p.citations])
            elif milestone.kind == "review":
                self.engine.candidates.prepare_review(run, milestone.review)
        role = ("organization" if run.phase == Phase.ORGANIZE
                else "review" if run.phase == Phase.VERIFY else "research")
        run.native.history.append(
            {
                "task_id": run.task_id,
                "role": role,
                "phase": run.phase.value,
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
                "invocation_seconds": receipt.get("invocation_seconds"),
                "checkpoint_error": receipt.get("checkpoint_error"),
                "source_observed_at": receipt.get("source_observed_at"),
                "finalizing": receipt.get("finalizing", False),
            }
        )
        run.native.pending_result = None
        # A timed-out turn can contain completed, useful searches. Preserve only
        # transport-confirmed observations for this exact session, before pausing;
        # do not accept its unfinished milestone or refresh its original time.
        if result.status == BackendStatus.COMPLETED or (
            result.runtime.get("tool_observations_confirmed") is True
            and result.session_id
            and result.session_id == getattr(run.native, self.attempts.session_field(run))
        ):
            self._record_tool_observations(run, result, receipt)
        final = run.native.finalization
        if run.task_id == final.task_id and (
            final.status == "running" or (final.status == "incomplete" and receipt.get("finalizing"))
        ):
            return self.finalizer.consume(
                run, Config.model_validate(run.config), result, milestone, receipt,
            )
        if result.status != BackendStatus.COMPLETED:
            if result.pending:
                run.native.active_attempt = receipt["directory"]
            state = {
                BackendStatus.INTERRUPTED: State.PAUSED,
                BackendStatus.RATE_LIMITED: State.RATE_LIMITED,
            }.get(result.status, State.FAILED)
            reason, current_error = result.error or str(result.status), result.error
            # The transport cannot distinguish the two causes of cancelled().
            # Resolve expected interruptions from harness state without masking
            # independent provider failures or changing their saved diagnostics.
            if result.status == BackendStatus.INTERRUPTED:
                if self.engine._stop_file(run).exists():
                    state, reason, current_error = State.CANCELLED, "Stopped by user", None
                elif budget.remaining(run, Config.model_validate(run.config)) <= 0:
                    reason, current_error = "Active wall-time budget reached", None
            run.last_error = current_error
            self.store.save(run, "native_attempt_interrupted", error=result.error, reason=reason)
            if receipt.get("recovered"):
                # The interruption is now historical, not a failure of the new
                # invocation. Keep the event and unknown usage without a stale
                # current-error banner throughout the resumed research turn.
                run.last_error = None
                self.store.save(run, "native_recovery_ready")
                return False
            if reason == "Active wall-time budget reached" and finalization_applicable(run):
                config = Config.model_validate(run.config)
                if self.finalizer.begin(run, config):
                    return False
                self.finalizer.fallback(run, config, budget.hard_limit_reason(run, config) or reason)
            self.engine._pause(run, reason, state)
            return True
        run.native.checkpoint_error = receipt.get("checkpoint_error")
        if receipt.get("steering") == run.native.steering:
            run.native.steering = None
        run.last_error = run.native.checkpoint_error
        finish = None
        if milestone:
            if milestone.problem and run.phase == Phase.FIND:
                record_selection(self.store, run, milestone, prepared=True)
                if run.workflow == Workflow.FIND:
                    finish = "Discovery complete; ranked problems saved for a separate solve task"
                else:
                    run.phase = Phase.SOLVE
            if milestone.kind == "candidate":
                self.engine._candidate(run, milestone.candidate)
                # Completion is only a solver claim, never independent verification.
                # Preserve the submitted milestone verbatim but do not let conclude
                # turn an explicitly incomplete candidate into a completed Solve.
                complete_claim = claims_complete(milestone.candidate)
                run.native.candidate_conclude = milestone.conclude and complete_claim
                run.native.reviewer_session_id = None
                run.native.reviewer_response_id = None
                run.native.reviewer_candidate_id = None
                if run.workflow == Workflow.SOLVE:
                    if run.native.candidate_conclude and not full_solve_budget(run):
                        finish = "Solving complete; candidate saved for independent verification"
                    elif complete_claim and full_solve_budget(run):
                        run.native.history[-1]["continuation_reason"] = (
                            "Complete solution claim saved as a checkpoint. Full-budget Solve "
                            "is enabled: use the remaining active time to critically check and "
                            "improve this proof and its evidence. Preserve valid results; record "
                            "any newly discovered gaps honestly. This is not independent Verify."
                        )
                    elif not complete_claim:
                        run.native.history[-1]["continuation_reason"] = (
                            "Candidate saved as a checkpoint: the original problem is not yet "
                            "explicitly claimed complete without mathematical obligations. "
                            "Continue from the saved work within the remaining budget."
                        )
                else:
                    run.phase = Phase.VERIFY
            elif milestone.kind == "review":
                candidate = self.engine.candidates.review(
                    run,
                    milestone.review,
                    [
                        {
                            "phase": "VERIFY",
                            "tool": "native_review",
                            "artifact": str(answer.relative_to(self.store.run_dir(run.id))),
                            "result": {"status": "OK"},
                        }
                    ],
                    prepared=True,
                )
                if run.native.review_only or (
                    candidate.reviews[-1].verdict == "NO_ISSUES_FOUND"
                    and run.native.candidate_conclude and claims_complete(candidate)
                ):
                    finish = "Independent review recorded; see proof status and verification limits"
                else:
                    run.phase = Phase.SOLVE
            elif milestone.kind == "organization":
                organization.accept(run, milestone.report_markdowns or milestone.report_markdown)
                finish = "Expert reading report organized; original verification outcomes are unchanged"
            elif milestone.kind == "stop":
                if run.phase == Phase.SOLVE:
                    run.native.history[-1]["continuation_reason"] = (
                        "Researcher stop saved as progress, not a user stop request. "
                        "Reassess the recorded obstacles and pursue another useful route "
                        "within the remaining budget; do not invent a complete solution."
                    )
                else:
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
            elif run.workflow == Workflow.ORGANIZE:
                run.phase = Phase.ORGANIZE
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

    def _record_tool_observations(self, run: Run, result: BackendResult, receipt: dict) -> None:
        artifact = run.native.history[-1]["events"]
        observed_at = receipt.get("source_observed_at")
        for url in result.runtime.get("source_urls", []):
            run.observations.append({
                "phase": run.phase.value, "iteration": run.iteration, "tool": "native_source",
                "artifact": artifact,
                "result": {"status": "OK", "url": url, "retrieved_at": observed_at,
                           "scope": "Backend-reported URL, not independently fetched source text"},
            })
        if result.runtime.get("search_queries"):
            run.observations.append({
                "phase": run.phase.value, "iteration": run.iteration, "tool": "native_search",
                "artifact": artifact,
                "result": {"status": "OK", "queries": result.runtime["search_queries"], "retrieved_at": observed_at},
            })

    def drive(self, run: Run) -> Run:
        config = Config.model_validate(run.config)
        if run.mode == "chat" and config.budget.max_external_cost_usd == 0:
            raise ValueError("Chat API is blocked by max_external_cost_usd: 0")
        budget.settle(run)
        run.active_since = now()
        self.recover(run)
        config.backend.mode = run.mode
        backend = self.engine.backend_override or (
            research_backend(config.backend, self.store.root) if run.mode != "manual" else None
        )
        while True:
            if run.native.pending_result and self.apply(run):
                return run
            if self.engine._stop_file(run).exists():
                if run.native.finalization.status == "running":
                    self.finalizer.fallback(run, config, "Stopped by user during finalization")
                return self.engine._pause(run, "Stopped by user", State.CANCELLED)
            reason = budget.exhausted(run, config)
            if reason:
                if reason == "Active wall-time budget reached" and self.finalizer.begin(run, config):
                    continue
                if finalization_applicable(run) and (
                    reason == "Active wall-time budget reached" or run.native.finalization.status == "running"
                ):
                    reason = budget.hard_limit_reason(run, config) or reason
                    self.finalizer.fallback(run, config, reason)
                return self.engine._pause(run, reason)
            run.state = ACTIVE[run.phase]
            prompt = self.prepare(run, config)
            if run.mode == "manual":
                budget.settle(run)
                run.state = State.WAITING_FOR_USER
                self.store.save(run, "native_waiting_for_user", prompt=run.prompt_path)
                report(self.store, run)
                return run
            self.queue(run, self.attempts.invoke(run, backend, prompt, config))

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
