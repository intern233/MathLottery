from __future__ import annotations

import importlib.metadata
import platform
from pathlib import Path

import yaml

from mathlottery import __version__
from mathlottery.config import Config
from mathlottery.find import discovery
from mathlottery.models import (
    Candidate,
    CandidateInput,
    DiscoveryContext,
    LiteratureSearch,
    OrganizationContext,
    Phase,
    Problem,
    Run,
    State,
    Workflow,
    now,
    uid,
)
from mathlottery.organize import workflow as organization
from mathlottery.providers.base import AgentBackend
from mathlottery.runtime import budget
from mathlottery.runtime.resources import Coordinator, run_admission
from mathlottery.runtime.workflows import ACTIVE
from mathlottery.storage.core import Store, atomic_write
from mathlottery.telemetry.reporting import report
from mathlottery.verify.candidates import CandidateStore


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
        discovery_context: DiscoveryContext | None = None,
        discovery_files: dict[str, bytes] | None = None,
        organization_context: OrganizationContext | None = None,
        organization_files: dict[str, bytes] | None = None,
        organization_candidates: list[Candidate] | None = None,
        review_literature: list[LiteratureSearch] | None = None,
    ) -> Run:
        workflow = Workflow(workflow)
        if workflow == Workflow.SOLVE:
            from mathlottery.solve.routes import primary_config

            config = primary_config(Config.model_validate(config.model_dump(mode="json")))
            if config.solve.agent_slots:
                if mode is not None and mode != config.backend.mode:
                    raise ValueError("Solve's primary backend is selected by its first agent slot")
                if config.budget.max_external_cost_usd == 0 and any(
                    slot.backend.uses_api_key for slot in config.solve.agent_slots
                ):
                    raise ValueError("API-funded agent slots are blocked by max_external_cost_usd: 0")
        if workflow == Workflow.ORGANIZE:
            if not (problem and organization_context and organization_files and organization_candidates):
                raise ValueError("Organize requires a frozen reviewed source; use organize(config, source_run_id)")
            if proof or candidate or discovery_context:
                raise ValueError("Organize cannot submit a new candidate or change research context")
        elif any(value is not None for value in (organization_context, organization_files, organization_candidates)):
            raise ValueError("Organization context belongs only to an Organize task")
        if discovery_context is not None and (workflow != Workflow.SOLVE or discovery_files is None):
            raise ValueError("Discovery context is only attached to a selected Solve task")
        if workflow == Workflow.FIND and (problem or proof or candidate):
            raise ValueError("Finding takes selection criteria, not a problem or proof")
        if workflow == Workflow.SOLVE and (not problem or proof or candidate):
            raise ValueError("Solving requires a problem, without an input proof")
        if workflow == Workflow.VERIFY and (not problem or not (proof or candidate)):
            raise ValueError("Verification requires a problem and a proof/candidate")
        if proof and candidate:
            raise ValueError("Supply either a proof or a candidate")
        chosen_mode = mode or config.backend.mode
        if workflow == Workflow.SOLVE and config.solve.parallel_agents is not None and (
            chosen_mode not in {"codex", "work", "chat"} or config.backend.execution != "native"
        ):
            raise ValueError("Solve parallelism requires an automatic native backend")
        selected_backend = config.backend.model_copy(update={"mode": chosen_mode})
        if selected_backend.uses_api_key and config.budget.max_external_cost_usd == 0:
            raise ValueError(
                "API usage is metered; max_external_cost_usd: 0 forbids it. "
                "Set this legacy restriction to null to use your API account limits."
            )
        if chosen_mode == "chat" and config.backend.execution == "structured":
            raise ValueError(
                "Chat API uses native execution; use manual for old structured handoffs"
            )
        if workflow != Workflow.PIPELINE and config.backend.execution != "native":
            raise ValueError("Independent find/solve/verify/organize workflows require native execution")
        run = Run(
            id=uid("run"),
            mode=chosen_mode,
            interface_version=2,
            workflow=workflow,
            discovery_request=discovery_request,
            discovery_count=discovery_count,
            execution="structured" if mode == "demo" else config.backend.execution,
            problem=problem,
            discovery_context=discovery_context,
            organization_context=organization_context,
            review_literature=review_literature or [],
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
        if discovery_context is not None:
            root = self.store.run_dir(run.id)
            root.mkdir(parents=True, exist_ok=True)
            discovery.save(root, discovery_context, discovery_files)
        if organization_context is not None:
            root = self.store.run_dir(run.id)
            root.mkdir(parents=True, exist_ok=True)
            run.phase = Phase.ORGANIZE
            run.candidates = [value.model_copy(deep=True) for value in organization_candidates]
            organization.save(root, organization_context, organization_files)
        self.store.save(run, "created")
        atomic_write(self.store.run_dir(run.id) / "config.yaml", yaml.safe_dump(run.config))
        report(self.store, run)
        return run

    def solve_discovered(self, config: Config, source_run_id: str, problem_id: str, expected_sha256=None):
        """A user choice starts an independent solver with an immutable Find dossier."""
        with self.store.lock(source_run_id):
            source = self.store.load(source_run_id)
            problem = discovery.choose(source, problem_id, expected_sha256)
            context, files = discovery.capture(self.store, source, problem, config)
        return self.create(config, problem=problem, workflow=Workflow.SOLVE,
                           discovery_context=context, discovery_files=files)

    def organize(self, config: Config, source_run_id: str, language="zh", instructions=None) -> Run:
        """Start a fresh editorial session from an immutable, explicitly reviewed source."""
        if config.backend.execution != "native":
            raise ValueError("Organize requires native execution")
        with self.store.lock(source_run_id):
            source = self.store.load(source_run_id)
            context, files = organization.capture(self.store, source, config, language, instructions)
            problem = source.problem.model_copy(deep=True)
            candidates = [value.model_copy(deep=True) for value in source.candidates]
        return self.create(config, problem=problem, workflow=Workflow.ORGANIZE,
                           organization_context=context, organization_files=files,
                           organization_candidates=candidates)

    def export_organized(self, run_id: str) -> Run:
        """Retry local exports without invoking a model or changing verification."""
        with self.store.lock(run_id):
            run = self.store.load(run_id)
            if run.workflow != Workflow.ORGANIZE or run.organization_report is None:
                raise ValueError("This task has no organized report to export")
            if run.active_since or run.native.active_attempt or run.native.pending_result:
                raise ValueError("Wait for the organization task to finish before exporting")
            organization.export(self.store, run)
            report(self.store, run)
            return run

    def _cancelled(self, run: Run, config: Config) -> bool:
        return self._stop_file(run).exists() or budget.remaining(run, config) <= 0

    def _stop_file(self, run: Run) -> Path:
        return self.store.run_dir(run.id) / "stop.requested"

    def _pause(self, run: Run, reason: str, state=State.PAUSED):
        if (run.native.finalization.status == "running"
                and not (run.native.active_attempt or run.native.pending_result)):
            from mathlottery.runtime.finalization import SolveFinalizer

            SolveFinalizer(self).fallback(run, Config.model_validate(run.config), reason)
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
        organization.export(self.store, run)
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
                if run.state in (State.COMPLETED, State.CANCELLED):
                    return run
                # Settle a crashed worker before waiting; queue time is not research time.
                if run.active_since:
                    resources = Coordinator(self.store).snapshot(run.id)
                    observed = budget.interrupted_elapsed(run, resources)
                    wall_elapsed = budget.elapsed(run)
                    if observed is None:
                        budget.settle(run)
                    else:
                        run.elapsed_seconds, run.active_since = observed, None
                    self.store.save(
                        run, "resource_recovery_settled",
                        timing_basis="last_resource_sample" if observed is not None else "wall_clock",
                        excluded_unobserved_seconds=max(0, wall_elapsed - run.elapsed_seconds),
                    )
                with run_admission(self.store, run, Config.model_validate(run.config)) as admitted:
                    if not admitted:
                        return self._pause(run, "Resource wait cancelled; resume to continue")
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
            from mathlottery.runtime.native import NativeRunner

            return NativeRunner(self).drive(run)
        from mathlottery.runtime.structured import StructuredRunner

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
            with run_admission(self.store, run, Config.model_validate(run.config)) as admitted:
                if not admitted:
                    return self._pause(run, "Resource wait cancelled; response not applied")
                return self._submit(run, text)

    def _submit(self, run: Run, text: str) -> Run:
        if run.execution == "native":
            from mathlottery.runtime.native import NativeRunner

            return NativeRunner(self).submit(run, text)
        from mathlottery.runtime.structured import StructuredRunner

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
            previous_config = Config.model_validate(run.config)
            requested_config = config or previous_config
            requested_backend = requested_config.backend.model_copy(update={"mode": mode or run.mode})
            if requested_config.budget.max_external_cost_usd == 0 and (
                requested_backend.uses_api_key
                or (run.workflow == Workflow.SOLVE and any(
                    slot.backend.uses_api_key for slot in requested_config.solve.agent_slots
                ))
            ):
                raise ValueError("API usage is blocked by max_external_cost_usd: 0")
            if run.execution == "native" and run.mode in {"codex", "work"} and requested_backend.mode in {"codex", "work"}:
                before, after = previous_config.backend, requested_backend
                if (before.codex_auth, before.codex_identity, before.api_key_env_name) != (
                    after.codex_auth, after.codex_identity, after.api_key_env_name
                ):
                    raise ValueError("Start a new run to change Codex authentication or account namespace")
            if run.workflow == Workflow.SOLVE:
                from mathlottery.solve.routes import validate_resume_routes

                previous = Config.model_validate(run.config)
                if config is not None:
                    config = Config.model_validate(config.model_dump(mode="json"))
                validate_resume_routes(previous, config or previous, mode)
            if run.state == State.COMPLETED and not (message and run.execution == "native"):
                return run
            if config:
                from mathlottery.runtime.finalization import SolveFinalizer

                if (run.native.solve_team.active_attempts or run.native.solve_team.pending_receipts) and (
                    config.backend.mode != run.mode or config.backend.provider != run.config.get("backend", {}).get("provider")
                ):
                    raise ValueError("Recover all Solve team attempts before switching providers")
                SolveFinalizer(self).reset_for_extension(run, config)
            if message and run.execution == "native":
                run.native.steering = message
                if not (run.native.active_attempt or run.native.pending_result):
                    run.task_id = (run.native.finalization.task_id
                                   if run.native.finalization.status == "running" else None)
                    run.prompt_path = None
                if run.phase == Phase.REPORT:
                    if run.workflow == Workflow.FIND:
                        run.phase = Phase.FIND
                    elif run.workflow == Workflow.VERIFY:
                        run.phase = Phase.VERIFY
                    elif run.workflow == Workflow.ORGANIZE:
                        run.phase = Phase.ORGANIZE
                    else:
                        run.phase = Phase.SOLVE if run.problem else Phase.FIND
                        run.native.review_only = False
            if mode and mode != run.mode:
                if (run.native.active_attempt or run.native.pending_result
                        or run.native.solve_team.active_attempts or run.native.solve_team.pending_receipts):
                    raise ValueError("Recover the pending attempt before switching backends")
                if mode == "chat" and run.execution != "native":
                    raise ValueError("Legacy structured runs use manual or codex, not Chat API")
                effective = config or Config.model_validate(run.config)
                if effective.backend.model_copy(update={"mode": mode}).uses_api_key and effective.budget.max_external_cost_usd == 0:
                    raise ValueError("API usage is blocked by max_external_cost_usd: 0")
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
                if run.native.finalization.status == "running":
                    from mathlottery.runtime.finalization import SolveFinalizer

                    SolveFinalizer(self).fallback(run, Config.model_validate(run.config),
                                                 "Stopped by user during finalization")
                if run.mode == "chat" and run.native.active_attempt:
                    from mathlottery.runtime.native import NativeRunner

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
