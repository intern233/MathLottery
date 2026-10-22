from __future__ import annotations

import importlib.metadata
import platform
from pathlib import Path

import yaml

from mathlottery import __version__, budget
from mathlottery.backends import AgentBackend
from mathlottery.candidates import CandidateStore
from mathlottery.config import Config
from mathlottery.models import (
    CandidateInput,
    Phase,
    Problem,
    Run,
    State,
    Workflow,
    now,
    uid,
)
from mathlottery.reporting import report
from mathlottery.storage import Store, atomic_write
from mathlottery.workflows import ACTIVE


class Orchestrator:
    def __init__(self, store: Store, backend: AgentBackend | None = None):
        self.store = store
        self.backend_override = backend
        self.candidates = CandidateStore(store)

    def create(
        self,
        config: Config,
        problem: Problem | None = None,
        source: str | None = None,
        mode: str | None = None,
        proof: str | None = None,
        workflow: Workflow = Workflow.PIPELINE,
        discovery_request: str | None = None,
        discovery_count: int = 5,
        candidate: CandidateInput | None = None,
    ) -> Run:
        workflow = Workflow(workflow)
        if workflow == Workflow.FIND and (problem or proof or candidate):
            raise ValueError("Finding takes selection criteria, not a problem or proof")
        if workflow == Workflow.SOLVE and (not problem or proof or candidate):
            raise ValueError("Solving requires a problem, without an input proof")
        if workflow == Workflow.VERIFY and (not problem or not (proof or candidate)):
            raise ValueError("Verification requires a problem and a proof/candidate")
        if proof and candidate:
            raise ValueError("Supply either a proof or a candidate")
        chosen_mode = mode or config.backend.mode
        if chosen_mode == "chat" and config.budget.max_external_cost_usd == 0:
            raise ValueError(
                "Chat API is metered; max_external_cost_usd: 0 forbids it. "
                "Set this legacy restriction to null to use your API account limits."
            )
        if chosen_mode == "chat" and config.backend.execution == "structured":
            raise ValueError(
                "Chat API uses native execution; use manual for old structured handoffs"
            )
        if workflow != Workflow.PIPELINE and config.backend.execution != "native":
            raise ValueError("Independent find/solve/verify workflows require native execution")
        run = Run(
            id=uid("run"),
            mode=chosen_mode,
            interface_version=2,
            workflow=workflow,
            discovery_request=discovery_request,
            discovery_count=discovery_count,
            execution="structured" if mode == "demo" else config.backend.execution,
            problem=problem,
            source=source,
            config=config.model_dump(mode="json"),
            environment={
                "python": platform.python_version(),
                "platform": platform.platform(),
                "mathlottery": __version__,
                "dependencies": {
                    name: importlib.metadata.version(name)
                    for name in ("pydantic", "typer", "httpx", "sympy")
                },
            },
        )
        if run.execution == "native":
            run.usage.external_cost_usd = None  # Inherited third-party tools are not metered here.
        if run.execution == "native" and problem:
            run.phase = Phase.SOLVE
        if proof or candidate:
            if not problem:
                raise ValueError("Verification requires a problem statement")
            self._candidate(run, candidate or CandidateInput(claim=problem.statement, proof=proof))
            run.phase = Phase.VERIFY
            run.native.review_only = True
        self.store.save(run, "created")
        atomic_write(self.store.run_dir(run.id) / "config.yaml", yaml.safe_dump(run.config))
        report(self.store, run)
        return run

    def _cancelled(self, run: Run, config: Config) -> bool:
        return self._stop_file(run).exists() or budget.remaining(run, config) <= 0

    def _stop_file(self, run: Run) -> Path:
        return self.store.run_dir(run.id) / "stop.requested"

    def _pause(self, run: Run, reason: str, state=State.PAUSED):
        budget.settle(run)
        run.state, run.stop_reason = state, reason
        self.store.save(run, "paused", reason=reason)
        report(self.store, run)
        return run

    def _finish(self, run: Run, reason: str):
        run.state, run.phase = State.REPORTING, Phase.REPORT
        run.stop_reason = reason
        budget.settle(run)
        self.store.save(run, "reporting")
        run.state = State.COMPLETED
        self.store.save(run, "completed")
        report(self.store, run)

    @staticmethod
    def _account(run: Run, result):
        if not result.invoked:
            return
        values = result.usage
        if all(isinstance(values.get(key), int) for key in ("input_tokens", "output_tokens")):
            run.usage.measured_calls += 1
            for key in ("input_tokens", "output_tokens", "cached_input_tokens"):
                if key in values:
                    setattr(run.usage, key, (getattr(run.usage, key) or 0) + values[key])
        else:
            run.usage.unknown_calls += 1

    def drive(self, run_id: str) -> Run:
        with self.store.lock(run_id):
            run = self.store.load(run_id)
            try:
                return self._drive(run)
            except KeyboardInterrupt:
                return self._pause(run, "Interrupted; resume to continue")
            except Exception as error:
                run.last_error = f"{type(error).__name__}: {error}"
                return self._pause(run, "Execution error; state preserved", State.FAILED)

    def _drive(self, run: Run) -> Run:
        if run.state in (State.COMPLETED, State.CANCELLED):
            return run
        if run.phase == Phase.REPORT:
            self._finish(run, run.stop_reason or "Recovered report generation")
            return run
        if run.execution == "native":
            from mathlottery.native import NativeRunner

            return NativeRunner(self).drive(run)
        from mathlottery.structured import StructuredRunner

        return StructuredRunner(self).drive(run)

    def _check_candidate_file(self, run: Run):
        return self.candidates.check(run)

    @staticmethod
    def _review_observations(run: Run) -> list[dict]:
        return CandidateStore.observations(run)

    def _candidate(self, run: Run, content: CandidateInput):
        return self.candidates.add(run, content)

    def submit(self, run_id: str, text: str) -> Run:
        with self.store.lock(run_id):
            run = self.store.load(run_id)
            if run.state != State.WAITING_FOR_USER or run.mode != "manual":
                raise ValueError("This run is not waiting for a manual response")
            if run.execution == "native":
                from mathlottery.native import NativeRunner

                return NativeRunner(self).submit(run, text)
            from mathlottery.structured import StructuredRunner

            runner = StructuredRunner(self)
            response = runner.validate(run, text)  # Invalid input must not change state.
            config = Config.model_validate(run.config)
            reason = budget.exhausted(run, config)
            if reason:
                return self._pause(run, reason)
            run.active_since = now()
            run.usage.unknown_calls += 1
            runner.accept(run, response)
            try:
                return self._drive(run)
            except KeyboardInterrupt:
                return self._pause(run, "Interrupted while applying response")
            except Exception as error:
                run.last_error = f"{type(error).__name__}: {error}"
                return self._pause(run, "Execution error; state preserved", State.FAILED)

    def resume(
        self,
        run_id: str,
        mode: str | None = None,
        config: Config | None = None,
        message: str | None = None,
    ) -> Run:
        with self.store.lock(run_id):
            run = self.store.load(run_id)
            if run.state == State.COMPLETED and not (message and run.execution == "native"):
                return run
            if message and run.execution == "native":
                run.native.steering = message
                if not (run.native.active_attempt or run.native.pending_result):
                    run.task_id, run.prompt_path = None, None
                if run.phase == Phase.REPORT:
                    if run.workflow == Workflow.FIND:
                        run.phase = Phase.FIND
                    elif run.workflow == Workflow.VERIFY:
                        run.phase = Phase.VERIFY
                    else:
                        run.phase = Phase.SOLVE if run.problem else Phase.FIND
                        run.native.review_only = False
            if mode and mode != run.mode:
                if run.native.active_attempt or run.native.pending_result:
                    raise ValueError("Recover the pending attempt before switching backends")
                if mode == "chat" and run.execution != "native":
                    raise ValueError("Legacy structured runs use manual or codex, not Chat API")
                effective = config or Config.model_validate(run.config)
                if mode == "chat" and effective.budget.max_external_cost_usd == 0:
                    raise ValueError("Chat API is blocked by max_external_cost_usd: 0")
                previous = run.mode
                run.mode = mode
                run.config["backend"]["mode"] = mode
                self.store.save(run, "explicit_mode_switch", previous=previous, new=mode)
            if config:
                run.config = config.model_dump(mode="json")
                run.config["backend"]["execution"] = run.execution
                run.config["backend"]["mode"] = run.mode if run.mode != "demo" else "manual"
                atomic_write(self.store.run_dir(run.id) / "config.yaml", yaml.safe_dump(run.config))
            self._stop_file(run).unlink(missing_ok=True)
            run.state = ACTIVE.get(run.phase, State.REPORTING)
            run.stop_reason = None
            run.last_error = None
            self.store.save(run, "resumed")
        return self.drive(run_id)

    def stop(self, run_id: str) -> Run:
        run = self.store.load(run_id)
        if run.state == State.COMPLETED:
            return run
        atomic_write(self._stop_file(run), now())
        try:
            with self.store.lock(run_id):
                run = self.store.load(run_id)
                if run.mode == "chat" and run.native.active_attempt:
                    from mathlottery.native import NativeRunner

                    runner = NativeRunner(self)
                    runner.recover(run)  # The stop marker makes recovery cancel the remote call.
                    if run.native.pending_result:
                        runner.apply(run)
                    if run.state == State.COMPLETED:
                        return run
                self._pause(run, "Stopped by user", State.CANCELLED)
        except ValueError:
            pass  # The active process observes the marker and writes its own checkpoint.
        return self.store.load(run_id)
