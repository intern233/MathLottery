"""Browser workflow commands using the existing orchestrator and job lifecycle."""

from __future__ import annotations

from typing import Callable

from mathlottery.config import Config
from mathlottery.models import (
    CandidateInput,
    LiteratureSearch,
    Problem,
    ReviewProvenance,
    Run,
    Workflow,
    digest,
)
from mathlottery.providers.agent_roster import AgentRosterStore
from mathlottery.runtime.orchestrator import Orchestrator
from mathlottery.storage.core import Store
from mathlottery.verify.candidates import CandidateStore
from mathlottery.verify.evidence import capture as capture_review_evidence
from mathlottery.verify.obstacles import carry_literature
from mathlottery.web.jobs import BusyError, Jobs
from mathlottery.web.requests import Overrides, ResumeRequest, StartRequest


class WorkflowOperations:
    """Validate state transitions, persist checkpoints, then dispatch workers.

    Commands return domain runs. Browser formatting belongs to RunQueries, and
    account/model preflight callbacks remain controlled by the HTTP boundary.
    """

    def __init__(self, store: Store, jobs: Jobs, config_loader: Callable[[], Config]):
        self.store = store
        self.jobs = jobs
        self._config = config_loader

    def start(
        self,
        request: StartRequest,
        *,
        ensure_backend: Callable[[str, str], None] | None = None,
        validate_model: Callable[[Config], None] | None = None,
        ensure_agent_slots: Callable[[Config], None] | None = None,
        ensure_config: Callable[[Config], None] | None = None,
    ) -> Run:
        if request.options.use_agent_slots and request.workflow != "solve":
            raise ValueError("The configured agent pool applies only to Solve")
        if request.workflow != "solve" and any(
            value is not None
            for value in (
                request.options.solve_parallel_agents,
                request.options.solve_max_groups,
            )
        ):
            raise ValueError("Research parallelism and group limits apply only to Solve")
        base = self._config()
        if request.options.use_agent_slots:
            base = AgentRosterStore(self.store.root).load().apply(base)
        elif base.solve.agent_slots:
            # Browser routing is an explicit form choice. A CLI-only YAML pool
            # must not invisibly override the displayed default model/account.
            data = base.model_dump()
            data["solve"]["agent_slots"] = []
            base = Config.model_validate(data)
        if request.workflow == "solve" and base.solve.agent_slots:
            conflicting = request.options.model_fields_set & {
                "backend", "provider", "model", "reasoning_effort", "reasoning_mode",
                "native_multi_agent", "native_memories",
                "codex_auth", "codex_api_key_env",
            }
            if conflicting:
                raise ValueError("Edit per-agent models and connections on the Agents page")
        config = request.options.apply(base)
        if config.backend.mode not in {"codex", "chat"} or config.backend.execution != "native":
            raise ValueError(
                "The browser starts native codex/chat tasks; select these in config.yaml"
            )
        has_slots = request.workflow == "solve" and bool(config.solve.agent_slots)
        if validate_model is not None and not has_slots:
            validate_model(config)
        if has_slots and ensure_agent_slots is not None:
            ensure_agent_slots(config)
        elif not has_slots and ensure_config is not None:
            ensure_config(config)
        elif ensure_backend is not None and not has_slots:
            ensure_backend(config.backend.mode, config.backend.execution)
        if request.workflow == "organize":
            self.ensure_review_source_idle(request.from_run)
            run = Orchestrator(self.store).organize(
                config,
                request.from_run,
                language=request.language or "zh",
                instructions=request.instructions,
            )
            self.jobs.launch(run.id, "drive")
            return self.store.load(run.id)
        if request.from_discovery:
            self.ensure_review_source_idle(request.from_discovery)
            run = Orchestrator(self.store).solve_discovered(
                config,
                request.from_discovery,
                request.problem_id,
                request.discovery_problem_sha256,
            )
            if request.instructions and request.instructions.strip():
                run.native.steering = request.instructions.strip()
                self.store.save(run, "web_direction_added")
            self.jobs.launch(run.id, "drive")
            return self.store.load(run.id)
        problem, candidate, evidence, provenance = None, None, None, None
        review_literature = []
        if request.from_run:
            self.ensure_review_source_idle(request.from_run)
            with self.store.lock(request.from_run):
                self.ensure_review_source_idle(request.from_run, include_run_lock=False)
                original = self.store.load(request.from_run)
                if not original.candidates:
                    raise ValueError("The selected run has no candidate to verify")
                checked = CandidateStore(self.store).check(original)
                if request.from_candidate_id and (
                    request.from_candidate_id != checked.id
                    or request.from_candidate_sha256 != checked.sha256
                ):
                    raise ValueError(
                        "The source candidate changed; refresh the source and select it again"
                    )
                evidence = capture_review_evidence(
                    self.store.run_dir(original.id),
                    original,
                    request.source_files,
                    config.backend.mode,
                )
                candidate = CandidateInput(
                    **checked.model_dump(include=set(CandidateInput.model_fields))
                )
                provenance = ReviewProvenance(
                    source_run_id=original.id,
                    source_candidate_id=checked.id,
                    candidate_sha256=checked.sha256,
                )
                # Carry factual literature investigations, never the earlier verdict or session.
                merged = carry_literature(
                    LiteratureSearch(),
                    [
                        *original.review_literature,
                        *(review.literature_search for review in checked.reviews),
                    ],
                )
                # Revalidate model bounds; never silently drop an older unresolved obstacle.
                review_literature = [LiteratureSearch.model_validate(merged.model_dump())]
                problem = original.problem or Problem(
                    id=f"claim-{digest(candidate.claim)[:12]}",
                    title=candidate.claim[:100],
                    statement=candidate.claim,
                )
        elif request.problem_id:
            problem = self.store.load_problem(request.problem_id)
        elif request.statement:
            problem = self.store.save_problem(
                Problem(
                    id=f"prompt-{digest(request.statement)[:12]}",
                    title=(request.title or request.statement[:100]).strip(),
                    statement=request.statement,
                )
            )
        if request.proof:
            candidate = CandidateInput(claim=problem.statement, proof=request.proof)
        run = Orchestrator(self.store).create(
            config,
            workflow=Workflow(request.workflow),
            problem=problem,
            candidate=candidate,
            source=request.source,
            discovery_request=request.query,
            discovery_count=request.count,
            review_literature=review_literature,
        )
        if provenance is not None:
            run.review_source = provenance
            self.store.save(run, "web_review_source_linked")
        if evidence is not None:
            run.review_evidence = evidence.model_copy(
                update={"candidate_id": run.candidates[-1].id}
            )
            self.store.save(
                run,
                "web_review_sources_captured",
                source_run_id=evidence.source_run_id,
                source_candidate_id=evidence.source_candidate_id,
                file_count=len(evidence.files),
            )
        if request.instructions and request.instructions.strip():
            run.native.steering = request.instructions.strip()
            self.store.save(run, "web_initial_direction")
        self.jobs.launch(run.id, "drive")
        return self.store.load(run.id)

    def ensure_review_source_idle(self, run_id, *, include_run_lock=True):
        if self.jobs.running(run_id, include_run_lock=include_run_lock):
            raise BusyError(
                "Stop the source task and wait for its worker to finish before starting an independent review or report"
            )

    def export_organized(self, run_id):
        self.ensure_review_source_idle(run_id)
        run = Orchestrator(self.store).export_organized(run_id)
        return run

    def resume(
        self,
        run_id,
        request: ResumeRequest,
        *,
        ensure_backend: Callable[[str, str], None] | None = None,
        ensure_agent_slots: Callable[[Config], None] | None = None,
        ensure_config: Callable[[Config], None] | None = None,
    ) -> Run:
        run = self.store.load(run_id)
        if self.jobs.running(run_id):
            raise BusyError("Stop the active task before resuming with new instructions")
        if run.mode == "manual":
            raise ValueError("Manual handoffs are managed through the CLI")
        if run.state == "COMPLETED" and not (request.message and request.message.strip()):
            raise ValueError("Add new instructions to continue a completed task")
        if run.workflow != Workflow.SOLVE and any(
            value is not None
            for value in (
                request.solve_parallel_agents,
                request.solve_max_groups,
            )
        ):
            raise ValueError("Research parallelism and group limits apply only to Solve")
        config = Overrides(
            budget_minutes=request.budget_minutes,
            max_iterations=request.max_iterations,
            solve_until_budget_exhausted=request.solve_until_budget_exhausted,
            solve_parallel_agents=request.solve_parallel_agents,
            solve_max_groups=request.solve_max_groups,
        ).apply(Config.model_validate(run.config))
        for field in ("formal_memory_mb", "formal_address_space_mb", "formal_timeout_seconds"):
            value = getattr(request, field)
            if value is not None:
                setattr(config.verification, field, value)
        if run.workflow == Workflow.SOLVE and config.solve.agent_slots:
            if ensure_agent_slots is not None:
                ensure_agent_slots(config)
        elif ensure_config is not None:
            ensure_config(config)
        elif ensure_backend is not None:
            # Resume preserves the saved transport, regardless of current defaults or form values.
            ensure_backend(run.mode, run.execution)
        self.jobs.launch(
            run_id, "resume", config=config.model_dump(mode="json"), message=request.message
        )
        return self.store.load(run_id)

    def stop(self, run_id):
        self.store.load(run_id)
        self.jobs.request_stop(run_id)
        return Orchestrator(self.store).stop(run_id)

    def ensure_account_change_allowed(self, profile=None):
        for run in self.store.list_runs():
            config = Config.model_validate(run.config)
            connections = [config.backend]
            if run.workflow == Workflow.SOLVE:
                connections.extend(slot.backend for slot in config.solve.agent_slots)
            used = any(
                backend.mode in {"codex", "work"} and backend.codex_auth == "chatgpt"
                and backend.codex_identity == profile
                for backend in connections
            )
            if used and self.jobs.running(run.id):
                raise BusyError(
                    "Stop active Codex research in this workspace before switching or signing out. "
                    "Wait for its worker to finish stopping, then retry."
                )
