"""Compatibility runner for the original structured JSON/tool protocol."""

from __future__ import annotations

import json
import time
from typing import TYPE_CHECKING

from mathlottery.config import Config
from mathlottery.models import Action, AgentResponse, MemoryItem, Phase, Run, State, now, uid
from mathlottery.providers.base import BackendStatus, ChatInteractiveBackend, WorkBackend
from mathlottery.providers.registry import isolate_credentials
from mathlottery.runtime import budget
from mathlottery.runtime.structured_prompts import build_prompt, output_schema
from mathlottery.runtime.workflows import ACTIVE, assess_selection
from mathlottery.storage.core import atomic_write, json_text
from mathlottery.telemetry.reporting import report
from mathlottery.tooling.registry import ToolRegistry
from mathlottery.verify.literature import collect_sources

if TYPE_CHECKING:
    from mathlottery.runtime.orchestrator import Orchestrator


class StructuredRunner:
    def __init__(self, engine: Orchestrator):
        self.engine, self.store = engine, engine.store

    def prepare(self, run: Run, config: Config) -> str:
        if run.phase == Phase.VERIFY:
            self.engine._check_candidate_file(run)
        if not run.task_id:
            run.task_id = uid("task")
        directory = self.store.run_dir(run.id) / "tasks" / run.task_id
        prompt = build_prompt(run, config)
        atomic_write(directory / "prompt.md", prompt)
        atomic_write(directory / "response.schema.json", json_text(output_schema()))
        run.prompt_path = str((directory / "prompt.md").relative_to(self.store.run_dir(run.id)))
        self.store.save(run, "task_prepared", task_id=run.task_id, prompt=run.prompt_path)
        return prompt

    def drive(self, run: Run) -> Run:
        config = Config.model_validate(run.config)
        # A crashed active interval is conservatively charged through the time of recovery.
        budget.settle(run)
        run.active_since = now()
        backend = isolate_credentials(self.engine.backend_override or (
            ChatInteractiveBackend()
            if run.mode == "manual" else WorkBackend(config.backend, self.store.root)
        ), config, self.store.root)
        registry = ToolRegistry(
            self.store.run_dir(run.id), config.tools, lambda: self.engine._cancelled(run, config)
        )
        retries = 0
        while run.state != State.COMPLETED:
            if self.engine._stop_file(run).exists():
                return self.engine._pause(run, "Stopped by user", State.CANCELLED)
            # Commit/replay an already accepted response before applying the next-call budget gate.
            if run.pending_response:
                self.apply(run, registry)
                if run.state == State.COMPLETED:
                    return run
            reason = budget.exhausted(run, config)
            if reason:
                return self.engine._pause(run, reason)
            run.state = ACTIVE[run.phase]
            prompt = self.prepare(run, config)
            timeout = min(config.backend.timeout_seconds, budget.remaining(run, config))
            task_directory = self.store.run_dir(run.id) / "tasks" / run.task_id
            result = backend.invoke(
                prompt,
                output_schema(),
                task_directory / uid("attempt"),
                timeout,
                lambda: self.engine._cancelled(run, config),
            )
            self.engine._account(run, result)
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
                    while time.monotonic() < end and not self.engine._cancelled(run, config):
                        time.sleep(0.1)
                    continue
                state = {
                    BackendStatus.RATE_LIMITED: State.RATE_LIMITED,
                    BackendStatus.INTERRUPTED: State.PAUSED,
                }.get(result.status, State.FAILED)
                if self.engine._stop_file(run).exists():
                    state = State.CANCELLED
                return self.engine._pause(run, result.error or result.status, state)
            atomic_write(task_directory / "response.raw.txt", result.text)
            try:
                response = self.validate(run, result.text)
            except ValueError as error:
                run.iteration += 1
                run.last_error = str(error)
                self.store.save(run, "invalid_backend_response", error=str(error))
                return self.engine._pause(run, "Invalid structured backend response", State.FAILED)
            self.accept(run, response)
            retries = 0
        return run

    def validate(self, run: Run, text: str) -> AgentResponse:
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

    def accept(self, run: Run, response: AgentResponse):
        run.iteration += 1
        run.pending_response = response.model_dump(mode="json")
        run.completed_tools = []
        run.last_error = None
        self.store.save(run, "response_accepted", action=response.action, task_id=run.task_id)
        atomic_write(
            self.store.run_dir(run.id) / "tasks" / run.task_id / "response.json",
            json_text(response),
        )

    def apply(self, run: Run, registry: ToolRegistry):
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
            collect_sources(self.store, run, [
                c for p in [response.problem, *response.shortlist] for c in p.citations
            ])
            selected = response.problem.model_copy(deep=True)
            selected.formal_target = run.problem.formal_target if run.problem else None
            selected.educational = run.problem.educational if run.problem else False
            previous = [*self.store.list_problems(), *run.shortlist, *([run.problem] if run.problem else [])]
            retrieved = [o["result"] for o in run.observations]
            selected = assess_selection(selected, retrieved, previous)
            run.shortlist = [assess_selection(p, retrieved, previous) for p in (response.shortlist or [selected])]
            run.problem = self.store.save_problem(selected)
            atomic_write(
                self.store.run_dir(run.id) / "literature" / "selection.json",
                json_text(
                    {
                        "selected": run.problem.id,
                        "ordered_candidates": [p.model_dump(mode="json") for p in run.shortlist],
                        "scope": "Heuristic ranking, not a probability of solving the problem",
                    }
                ),
            )
            run.phase = Phase.SOLVE
        elif response.action == Action.SUBMIT_CANDIDATE:
            self.engine._candidate(run, response.candidate)
            run.phase = Phase.VERIFY
        elif response.action == Action.REVIEW:
            candidate = self.engine.candidates.review(run, response.review)
            if candidate.reviews[-1].verdict in ("ISSUES_FOUND", "INCONCLUSIVE"):
                run.phase = Phase.SOLVE
            else:
                run.pending_response = None
                self.engine._finish(
                    run, "Candidate independently reviewed; see verification limits"
                )
        elif response.action == Action.STOP:
            run.pending_response = None
            self.engine._finish(run, response.summary)
        run.pending_response = None
        run.completed_tools = []
        run.task_id, run.prompt_path = None, None
        if run.state != State.COMPLETED:
            run.state = ACTIVE[run.phase]
        self.store.save(run, "iteration_completed", action=response.action)
        report(self.store, run)
