from __future__ import annotations

import importlib.metadata
import json
import platform
import time
from pathlib import Path

import yaml

from mathlottery import __version__, budget
from mathlottery.auditor import audit
from mathlottery.backends import AgentBackend, BackendStatus, ChatInteractiveBackend, WorkBackend
from mathlottery.config import Config
from mathlottery.models import (
    Action,
    AgentResponse,
    Candidate,
    CandidateInput,
    MemoryItem,
    Phase,
    Problem,
    Run,
    State,
    Workflow,
    digest,
    now,
    uid,
)
from mathlottery.prompts import build_prompt, output_schema
from mathlottery.reporting import report
from mathlottery.sources import conservative_status
from mathlottery.storage import Store, atomic_write, json_text
from mathlottery.tools import ToolRegistry

ACTIVE = {Phase.FIND: State.DISCOVERING, Phase.SOLVE: State.SOLVING, Phase.VERIFY: State.VERIFYING}


class Orchestrator:
    def __init__(self, store: Store, backend: AgentBackend | None = None):
        self.store = store
        self.backend_override = backend

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

    def _prepare(self, run: Run, config: Config) -> str:
        if run.phase == Phase.VERIFY:
            self._check_candidate_file(run)
        if not run.task_id:
            run.task_id = uid("task")
        directory = self.store.run_dir(run.id) / "tasks" / run.task_id
        prompt = build_prompt(run, config)
        atomic_write(directory / "prompt.md", prompt)
        atomic_write(directory / "response.schema.json", json_text(output_schema()))
        run.prompt_path = str((directory / "prompt.md").relative_to(self.store.run_dir(run.id)))
        self.store.save(run, "task_prepared", task_id=run.task_id, prompt=run.prompt_path)
        return prompt

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
        config = Config.model_validate(run.config)
        # A crashed active interval is conservatively charged through the time of recovery.
        budget.settle(run)
        run.active_since = now()
        backend = self.backend_override or (
            ChatInteractiveBackend() if run.mode == "manual" else WorkBackend(config.backend)
        )
        registry = ToolRegistry(
            self.store.run_dir(run.id), config.tools, lambda: self._cancelled(run, config)
        )
        retries = 0
        while run.state != State.COMPLETED:
            if self._stop_file(run).exists():
                return self._pause(run, "Stopped by user", State.CANCELLED)
            # Commit/replay an already accepted response before applying the next-call budget gate.
            if run.pending_response:
                self._apply(run, registry)
                if run.state == State.COMPLETED:
                    return run
            reason = budget.exhausted(run, config)
            if reason:
                return self._pause(run, reason)
            run.state = ACTIVE[run.phase]
            prompt = self._prepare(run, config)
            timeout = min(config.backend.timeout_seconds, budget.remaining(run, config))
            task_directory = self.store.run_dir(run.id) / "tasks" / run.task_id
            result = backend.invoke(
                prompt,
                output_schema(),
                task_directory / uid("attempt"),
                timeout,
                lambda: self._cancelled(run, config),
            )
            self._account(run, result)
            if result.status == BackendStatus.PENDING_USER:
                budget.settle(run)
                run.state = State.WAITING_FOR_USER
                self.store.save(run, "waiting_for_user", prompt=run.prompt_path)
                report(self.store, run)
                return run
            if result.status != BackendStatus.COMPLETED:
                if result.invoked:
                    run.iteration += 1
                run.last_error = result.error
                self.store.save(
                    run,
                    "backend_error",
                    backend_status=result.status,
                    error=result.error,
                    usage=result.usage,
                )
                if result.status == BackendStatus.FAILED and retries < config.backend.max_retries:
                    retries += 1
                    end = time.monotonic() + min(2**retries, budget.remaining(run, config))
                    while time.monotonic() < end and not self._cancelled(run, config):
                        time.sleep(0.1)
                    continue
                state = {
                    BackendStatus.RATE_LIMITED: State.RATE_LIMITED,
                    BackendStatus.INTERRUPTED: State.PAUSED,
                }.get(result.status, State.FAILED)
                if self._stop_file(run).exists():
                    state = State.CANCELLED
                return self._pause(run, result.error or result.status, state)
            atomic_write(task_directory / "response.raw.txt", result.text)
            try:
                response = self._validate(run, result.text)
            except ValueError as error:
                run.iteration += 1
                run.last_error = str(error)
                self.store.save(run, "invalid_backend_response", error=str(error))
                return self._pause(run, "Invalid structured backend response", State.FAILED)
            self._accept(run, response)
            retries = 0
        return run

    def _validate(self, run: Run, text: str) -> AgentResponse:
        if len(text) > 500000:
            raise ValueError("Response exceeds 500 KB")
        response = AgentResponse.model_validate_json(text)
        if (response.run_id, response.task_id, response.phase) != (run.id, run.task_id, run.phase):
            raise ValueError(
                "Stale/wrong response: run_id, task_id and phase must match the pending task"
            )
        if response.action == Action.SELECT_PROBLEM and run.problem:
            if response.problem.statement != run.problem.statement:
                raise ValueError(
                    "A supplied problem statement must not be changed during selection"
                )
        if response.action == Action.STOP and response.tools:
            raise ValueError("STOP cannot include tool calls")
        return response

    def _accept(self, run: Run, response: AgentResponse):
        run.iteration += 1
        run.pending_response = response.model_dump(mode="json")
        run.completed_tools = []
        run.last_error = None
        self.store.save(run, "response_accepted", action=response.action, task_id=run.task_id)
        atomic_write(
            self.store.run_dir(run.id) / "tasks" / run.task_id / "response.json",
            json_text(response),
        )

    def _apply(self, run: Run, registry: ToolRegistry):
        response = AgentResponse.model_validate(run.pending_response)
        for number, call in enumerate(response.tools):
            if number < len(run.completed_tools):
                continue
            record_path = self.store.run_dir(run.id) / f"experiments/{run.task_id}-{number}.json"
            if record_path.exists():
                record = json.loads(record_path.read_text())
            else:
                record = registry.execute(call, run, number)
            run.completed_tools.append(record)
            self.store.save(run, "tool_completed", tool=call.name, artifact=record["artifact"])
        run.observations.extend(run.completed_tools)
        for item in response.memory:
            item = item.model_copy(
                update={"source_iteration": run.iteration, "status": "unverified"}
            )
            if not any(old.kind == item.kind and old.content == item.content for old in run.memory):
                run.memory.append(item)
        if run.phase == Phase.SOLVE and not response.memory:
            run.memory.append(
                MemoryItem(
                    kind="strategy", content=response.summary[:8000], source_iteration=run.iteration
                )
            )
        run.next_actions = response.next_actions
        if response.summary:
            atomic_write(
                self.store.run_dir(run.id) / "tasks" / run.task_id / "summary.md", response.summary
            )
        if response.action == Action.SELECT_PROBLEM:
            run.state = State.SELECTING
            selected = response.problem.model_copy(deep=True)
            selected.formal_target = run.problem.formal_target if run.problem else None
            selected.educational = run.problem.educational if run.problem else False
            selected = conservative_status(selected, [o["result"] for o in run.observations])
            run.problem = self.store.save_problem(selected)
            atomic_write(
                self.store.run_dir(run.id) / "literature" / "selection.json",
                json_text(
                    {
                        "selected": run.problem.id,
                        "ordered_candidates": [
                            conservative_status(
                                p, [o["result"] for o in run.observations]
                            ).model_dump(mode="json")
                            for p in (response.shortlist or [selected])
                        ],
                        "scope": "Heuristic ranking, not a probability of solving the problem",
                    }
                ),
            )
            run.phase = Phase.SOLVE
        elif response.action == Action.SUBMIT_CANDIDATE:
            self._candidate(run, response.candidate)
            run.phase = Phase.VERIFY
        elif response.action == Action.REVIEW:
            self._check_candidate_file(run)
            candidate = audit(run.candidates[-1], response.review, self._review_observations(run))
            run.candidates[-1] = candidate
            atomic_write(
                self.store.run_dir(run.id) / "verification" / f"{candidate.id}.json",
                json_text(candidate),
            )
            if response.review.verdict in ("ISSUES_FOUND", "INCONCLUSIVE"):
                run.phase = Phase.SOLVE
            else:
                run.pending_response = None
                self._finish(run, "Candidate independently reviewed; see verification limits")
        elif response.action == Action.STOP:
            run.pending_response = None
            self._finish(run, response.summary)
        run.pending_response = None
        run.completed_tools = []
        run.task_id, run.prompt_path = None, None
        if run.state != State.COMPLETED:
            run.state = ACTIVE[run.phase]
        self.store.save(run, "iteration_completed", action=response.action)
        report(self.store, run)

    def _check_candidate_file(self, run: Run):
        candidate = run.candidates[-1]
        path = self.store.run_dir(run.id) / "candidates" / f"{candidate.id}.json"
        original = Candidate.model_validate_json(path.read_text())
        if digest(original.claim + "\n" + original.proof) != candidate.sha256:
            raise ValueError("Candidate artifact was modified; refusing verification")

    @staticmethod
    def _review_observations(run: Run) -> list[dict]:
        return [o for o in run.observations if o["iteration"] > run.candidates[-1].source_iteration]

    def _candidate(self, run: Run, content: CandidateInput):
        candidate = Candidate(
            **content.model_dump(),
            id=uid("candidate"),
            sha256=digest(content.claim + "\n" + content.proof),
            source_iteration=run.iteration,
        )
        run.candidates.append(candidate)
        path = self.store.run_dir(run.id) / "candidates" / f"{candidate.id}.json"
        if path.exists():
            raise ValueError("Candidate versions are immutable")
        atomic_write(path, json_text(candidate))

    def submit(self, run_id: str, text: str) -> Run:
        with self.store.lock(run_id):
            run = self.store.load(run_id)
            if run.state != State.WAITING_FOR_USER or run.mode != "manual":
                raise ValueError("This run is not waiting for a manual response")
            if run.execution == "native":
                from mathlottery.native import NativeRunner

                return NativeRunner(self).submit(run, text)
            response = self._validate(run, text)  # Invalid input must not change state.
            config = Config.model_validate(run.config)
            reason = budget.exhausted(run, config)
            if reason:
                return self._pause(run, reason)
            run.active_since = now()
            run.usage.unknown_calls += 1
            self._accept(run, response)
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
