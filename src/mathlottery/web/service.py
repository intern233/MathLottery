"""Browser application operations over the existing domain objects and checkpoints."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Literal
from urllib.parse import urlsplit

from pydantic import Field, model_validator

from mathlottery import budget
from mathlottery.activity import export_activity_archive, read_run_activity
from mathlottery.candidates import CandidateStore
from mathlottery.config import ChatConfig, Config, load_config
from mathlottery.discovery import problem_fingerprint
from mathlottery.literature_obstacles import carry_literature
from mathlottery.metrics import run_metrics
from mathlottery.model_catalog import effective_provider, validate_configured_selection
from mathlottery.models import (
    CandidateInput,
    LiteratureSearch,
    Model,
    Problem,
    ReviewProvenance,
    Workflow,
    digest,
)
from mathlottery.orchestrator import Orchestrator
from mathlottery.organized_reports import summary as organization_summary
from mathlottery.resources import Coordinator
from mathlottery.review_evidence import capture as capture_review_evidence
from mathlottery.review_evidence import manifest as evidence_manifest
from mathlottery.review_evidence import selectable_source
from mathlottery.statement_risks import present_problem
from mathlottery.storage import Store, safe_path
from mathlottery.web.artifacts import list_formal_artifacts
from mathlottery.web.jobs import BusyError, Jobs
from mathlottery.web.outcomes import research_outcome


class Overrides(Model):
    backend: Literal["codex", "chat"] | None = None
    provider: str | None = Field(default=None, pattern=r"^[a-z][a-z0-9_-]{0,63}$")
    model: str | None = Field(default=None, min_length=1, max_length=200)
    reasoning_effort: str | None = Field(default=None, min_length=1, max_length=50)
    reasoning_mode: Literal["standard", "pro"] | None = None
    budget_minutes: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    max_iterations: int | None = Field(default=None, gt=0)
    solve_until_budget_exhausted: bool | None = None
    native_multi_agent: bool | None = None
    native_memories: bool | None = None

    def apply(self, config):
        original_provider = effective_provider(config)
        provider = self.provider or self.backend or original_provider
        mode = provider if provider in {"codex", "chat", "work", "manual"} else "chat"
        unchanged_legacy = (
            provider in {"work", "manual"} and not self.provider and not self.backend
        )
        if provider not in {"codex", "chat"} and provider not in config.model_providers and not unchanged_legacy:
            raise ValueError("Unknown model provider; configure it before selecting it")
        if self.backend and self.backend != mode:
            raise ValueError("Model provider and backend override conflict")
        data = config.model_dump()
        backend = data["backend"]
        provider_changed = provider != original_provider
        model_changed = "model" in self.model_fields_set and self.model != backend["model"]
        if provider_changed:
            backend["provider"] = provider
            backend["mode"] = mode
            backend["model"] = None
            # Switching away from a custom profile must never inherit its endpoint/key/tools.
            if provider in config.model_providers:
                backend["chat"] = config.model_providers[provider].chat.model_dump()
            elif original_provider in config.model_providers:
                backend["chat"] = ChatConfig().model_dump()
        elif self.provider:
            backend["provider"] = provider
        if provider_changed or model_changed:
            backend["reasoning_effort"] = None
            backend["chat"]["reasoning_mode"] = None
        for field in ("model", "reasoning_effort"):
            if field in self.model_fields_set:
                backend[field] = getattr(self, field)
        if "reasoning_mode" in self.model_fields_set:
            if mode != "chat" and self.reasoning_mode is not None:
                raise ValueError("Pro/standard reasoning mode applies only to the chat backend")
            backend["chat"]["reasoning_mode"] = self.reasoning_mode
        config = Config.model_validate(data)
        if self.budget_minutes is not None:
            config.budget.max_wall_time_minutes = self.budget_minutes
        if self.max_iterations is not None:
            config.budget.max_iterations = self.max_iterations
        if self.solve_until_budget_exhausted is not None:
            config.budget.solve_until_budget_exhausted = self.solve_until_budget_exhausted
        for field in ("native_multi_agent", "native_memories"):
            if field in self.model_fields_set:
                if config.backend.mode != "codex":
                    raise ValueError("Native agent capabilities apply only to Codex")
                setattr(config.backend, field, getattr(self, field))
        validate_configured_selection(config)
        return config


class StartRequest(Model):
    workflow: Literal["find", "solve", "verify", "organize"]
    language: Literal["en", "zh"] | None = None
    query: str | None = Field(default=None, max_length=30000)
    source: str | None = Field(default=None, max_length=2048)
    count: int = Field(default=5, ge=1, le=50)
    problem_id: str | None = Field(default=None, max_length=100)
    statement: str | None = Field(default=None, max_length=30000)
    title: str | None = Field(default=None, max_length=200)
    proof: str | None = Field(default=None, max_length=100000)
    instructions: str | None = Field(default=None, max_length=30000)
    from_run: str | None = Field(default=None, pattern=r"^run-[a-f0-9]{12}$")
    from_discovery: str | None = Field(default=None, pattern=r"^run-[a-f0-9]{12}$")
    discovery_problem_sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    from_candidate_id: str | None = Field(default=None, pattern=r"^candidate-[a-f0-9]{12}$")
    from_candidate_sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    source_files: list[str] = Field(default_factory=list, max_length=20)
    options: Overrides = Field(default_factory=Overrides)

    @model_validator(mode="after")
    def inputs(self):
        if self.language is not None and self.workflow != "organize":
            raise ValueError("Report language applies only to organize")
        if self.workflow == "organize":
            if not self.from_run or any((
                self.problem_id, self.statement, self.proof, self.query, self.source,
                self.from_discovery, self.discovery_problem_sha256,
                self.from_candidate_id, self.from_candidate_sha256, self.source_files,
            )):
                raise ValueError("Organize requires only a reviewed source run, optional language and instructions")
            return self
        if self.from_discovery:
            if self.workflow != "solve" or not self.problem_id or any((self.from_run, self.statement, self.proof)):
                raise ValueError("Choose a problem ID from Find for a separate Solve task")
            if not self.discovery_problem_sha256:
                raise ValueError("Bind the selected Find problem to its displayed SHA256")
        elif self.discovery_problem_sha256:
            raise ValueError("A discovery problem binding requires a Find run")
        if bool(self.from_candidate_id) != bool(self.from_candidate_sha256):
            raise ValueError("Supply both the source candidate ID and SHA256")
        if (self.from_candidate_id or self.source_files) and not (
            self.workflow == "verify" and self.from_run
        ):
            raise ValueError("Source candidate binding and proof sources require verify from a saved run")
        if any(not path or len(path) > 2048 for path in self.source_files):
            raise ValueError("Each proof source must have a nonempty relative path of at most 2048 characters")
        if self.source:
            url = urlsplit(self.source)
            if url.scheme not in {"https", "http"} or not url.hostname or url.username or url.password:
                raise ValueError("Source must be an HTTP(S) URL without credentials")
        if self.workflow == "find":
            if any((self.problem_id, self.statement, self.proof, self.from_run)):
                raise ValueError("Find accepts selection criteria, not a problem or proof")
        else:
            if self.query or self.source:
                raise ValueError("Selection criteria and source apply only to find")
            if self.from_run:
                if self.workflow != "verify" or any((self.problem_id, self.statement, self.proof)):
                    raise ValueError("Verify from a saved run or a supplied proof, not both")
            else:
                if bool(self.problem_id) == bool(self.statement and self.statement.strip()):
                    raise ValueError("Select a saved problem or enter a nonempty problem statement")
                if self.workflow == "verify" and not (self.proof and self.proof.strip()):
                    raise ValueError("Verification requires a nonempty proof")
                if self.workflow == "solve" and self.proof is not None:
                    raise ValueError("Use verify to review an existing proof")
        return self


class ResumeRequest(Model):
    message: str | None = Field(default=None, max_length=30000)
    budget_minutes: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    max_iterations: int | None = Field(default=None, gt=0)
    solve_until_budget_exhausted: bool | None = None
    formal_memory_mb: int | None = Field(default=None, ge=256, le=32768)
    formal_address_space_mb: int | None = Field(default=None, ge=1024, le=32768)
    formal_timeout_seconds: float | None = Field(default=None, ge=1, le=1800, allow_inf_nan=False)


def config_summary(config):
    return {
        "backend": config.backend.mode,
        "provider": effective_provider(config),
        "model": config.backend.model,
        "reasoning_effort": config.backend.reasoning_effort,
        "reasoning_mode": config.backend.chat.reasoning_mode,
        "execution": config.backend.execution,
        "budget_minutes": config.budget.max_wall_time_minutes,
        "max_iterations": config.budget.max_iterations,
        "solve_until_budget_exhausted": config.budget.solve_until_budget_exhausted,
        "finalize_minutes": config.budget.finalize_minutes,
        "native_multi_agent": config.backend.native_multi_agent,
        "native_memories": config.backend.native_memories,
        "native_web_search": config.backend.native_web_search,
        "formal_limits": config.verification.model_dump(include={
            "formal_memory_mb", "formal_address_space_mb", "formal_timeout_seconds",
        }),
        "resource_limits": config.resources.model_dump(),
    }


def workspace_key(root, config_path=None):
    root = Path(root).resolve()
    config_path = (config_path or root / "config.yaml").resolve()
    return digest(str(root) + "\n" + str(config_path))


class WebService:
    def __init__(self, root: Path, config_path: Path | None = None):
        self.store = Store(root)
        self.config_path = config_path
        self.jobs = Jobs(self.store)

    def config(self):
        return load_config(self.store.root, self.config_path)

    def summary(self, run):
        title = run.problem.title if run.problem else "Find problems"
        if run.workflow == Workflow.FIND:
            title = (run.discovery_request or "").strip().partition("\n")[0] or "Find problems"
            if len(title) > 120:
                title = title[:119].rstrip() + "…"
        resources = Coordinator(self.store).snapshot(run.id)
        worker = self.jobs.status(run.id)
        busy = self.jobs.running(run.id)
        observed = budget.interrupted_elapsed(run, resources) if not busy else None
        return {
            **run.model_dump(mode="json", include={
                "id", "workflow", "mode", "state", "phase", "iteration", "created_at",
                "updated_at", "stop_reason", "last_error", "usage", "execution",
            }),
            "title": title,
            "problem_id": run.problem.id if run.problem and run.workflow != Workflow.FIND else None,
            # Group stages without conflating equal titles or revisions of a statement.
            "problem_key": digest(json.dumps([run.problem.id, run.problem.statement])) if run.problem and run.workflow != Workflow.FIND else None,
            "shortlist_count": len(run.shortlist),
            "discovery_run_id": run.discovery_context.source_run_id if run.discovery_context else None,
            "candidate_count": len(run.candidates) if run.workflow != Workflow.ORGANIZE else 0,
            "reviewed_candidate_count": sum(bool(c.reviews) for c in run.candidates)
            if run.workflow != Workflow.ORGANIZE else 0,
            "research_outcome": research_outcome(run),
            "finalization": run.native.finalization.model_dump(mode="json"),
            "organized_report": organization_summary(self.store, run),
            "busy": busy,
            "resources": resources,
            "worker_state": resources["state"] if resources and resources["state"] in {"queued", "running"} else (worker or {}).get("state"),
            "elapsed_seconds": round(observed if observed is not None else budget.elapsed(run), 1),
            "elapsed_timing_basis": "last_resource_sample" if observed is not None else "wall_clock",
            "settings": config_summary(Config.model_validate(run.config)),
        }

    def bootstrap(self):
        try:
            settings, error = config_summary(self.config()), None
        except (ValueError, OSError):
            settings, error = None, "Local configuration is invalid or unreadable; check config.yaml."
        return {
            "settings": settings, "config_error": error,
            "runs": [self.summary(run) for run in self.store.list_runs()],
            "problems": [present_problem(p) for p in self.store.list_problems()],
        }

    def start(
        self, request: StartRequest, *, ensure_backend: Callable[[str, str], None] | None = None,
        validate_model: Callable[[Config], None] | None = None,
    ):
        config = request.options.apply(self.config())
        if config.backend.mode not in {"codex", "chat"} or config.backend.execution != "native":
            raise ValueError("The browser starts native codex/chat tasks; select these in config.yaml")
        if validate_model is not None:
            validate_model(config)
        if ensure_backend is not None:
            ensure_backend(config.backend.mode, config.backend.execution)
        if request.workflow == "organize":
            self.ensure_review_source_idle(request.from_run)
            run = Orchestrator(self.store).organize(
                config, request.from_run, language=request.language or "zh",
                instructions=request.instructions,
            )
            self.jobs.launch(run.id, "drive")
            return self.summary(self.store.load(run.id))
        if request.from_discovery:
            self.ensure_review_source_idle(request.from_discovery)
            run = Orchestrator(self.store).solve_discovered(
                config, request.from_discovery, request.problem_id, request.discovery_problem_sha256,
            )
            if request.instructions and request.instructions.strip():
                run.native.steering = request.instructions.strip()
                self.store.save(run, "web_direction_added")
            self.jobs.launch(run.id, "drive")
            return self.summary(self.store.load(run.id))
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
                    raise ValueError("The source candidate changed; refresh the source and select it again")
                evidence = capture_review_evidence(
                    self.store.run_dir(original.id), original, request.source_files, config.backend.mode,
                )
                candidate = CandidateInput(**checked.model_dump(include=set(CandidateInput.model_fields)))
                provenance = ReviewProvenance(
                    source_run_id=original.id, source_candidate_id=checked.id,
                    candidate_sha256=checked.sha256,
                )
                # Carry factual literature investigations, never the earlier verdict or session.
                merged = carry_literature(LiteratureSearch(), [
                    *original.review_literature, *(review.literature_search for review in checked.reviews),
                ])
                # Revalidate model bounds; never silently drop an older unresolved obstacle.
                review_literature = [LiteratureSearch.model_validate(merged.model_dump())]
                problem = original.problem or Problem(
                    id=f"claim-{digest(candidate.claim)[:12]}",
                    title=candidate.claim[:100], statement=candidate.claim,
                )
        elif request.problem_id:
            problem = self.store.load_problem(request.problem_id)
        elif request.statement:
            problem = self.store.save_problem(Problem(
                id=f"prompt-{digest(request.statement)[:12]}",
                title=(request.title or request.statement[:100]).strip(),
                statement=request.statement,
            ))
        if request.proof:
            candidate = CandidateInput(claim=problem.statement, proof=request.proof)
        run = Orchestrator(self.store).create(
            config, workflow=Workflow(request.workflow), problem=problem, candidate=candidate,
            source=request.source, discovery_request=request.query, discovery_count=request.count,
            review_literature=review_literature,
        )
        if provenance is not None:
            run.review_source = provenance
            self.store.save(run, "web_review_source_linked")
        if evidence is not None:
            run.review_evidence = evidence.model_copy(update={"candidate_id": run.candidates[-1].id})
            self.store.save(run, "web_review_sources_captured", source_run_id=evidence.source_run_id,
                            source_candidate_id=evidence.source_candidate_id, file_count=len(evidence.files))
        if request.instructions and request.instructions.strip():
            run.native.steering = request.instructions.strip()
            self.store.save(run, "web_initial_direction")
        self.jobs.launch(run.id, "drive")
        return self.summary(self.store.load(run.id))

    def ensure_review_source_idle(self, run_id, *, include_run_lock=True):
        if self.jobs.running(run_id, include_run_lock=include_run_lock):
            raise BusyError(
                "Stop the source task and wait for its worker to finish before starting an independent review or report"
            )

    def export_organized(self, run_id):
        self.ensure_review_source_idle(run_id)
        run = Orchestrator(self.store).export_organized(run_id)
        return organization_summary(self.store, run)

    def resume(
        self, run_id, request: ResumeRequest,
        *, ensure_backend: Callable[[str, str], None] | None = None,
    ):
        run = self.store.load(run_id)
        if self.jobs.running(run_id):
            raise BusyError("Stop the active task before resuming with new instructions")
        if run.mode == "manual":
            raise ValueError("Manual handoffs are managed through the CLI")
        if run.state == "COMPLETED" and not (request.message and request.message.strip()):
            raise ValueError("Add new instructions to continue a completed task")
        config = Overrides(
            budget_minutes=request.budget_minutes, max_iterations=request.max_iterations,
            solve_until_budget_exhausted=request.solve_until_budget_exhausted,
        ).apply(Config.model_validate(run.config))
        for field in ("formal_memory_mb", "formal_address_space_mb", "formal_timeout_seconds"):
            value = getattr(request, field)
            if value is not None:
                setattr(config.verification, field, value)
        if ensure_backend is not None:
            # Resume preserves the saved transport, regardless of current defaults or form values.
            ensure_backend(run.mode, run.execution)
        self.jobs.launch(run_id, "resume", config=config.model_dump(mode="json"), message=request.message)
        return self.summary(self.store.load(run_id))

    def stop(self, run_id):
        self.store.load(run_id)
        self.jobs.request_stop(run_id)
        return self.summary(Orchestrator(self.store).stop(run_id))

    def ensure_account_change_allowed(self):
        for run in self.store.list_runs():
            if run.mode in {"codex", "work"} and self.jobs.running(run.id):
                raise BusyError(
                    "Stop active Codex research in this workspace before switching or signing out. "
                    "Wait for its worker to finish stopping, then retry."
                )

    def text_artifact(self, run_id, relative, limit=200000):
        path = safe_path(self.store.run_dir(run_id), relative)
        if not path.is_file():
            return {"text": "", "truncated": False}
        with path.open("rb") as stream:
            data = stream.read(limit + 1)
        return {"text": data[:limit].decode("utf-8", errors="replace"), "truncated": len(data) > limit}

    def activity_archive(self, run_id):
        run = self.store.load(run_id)
        directory = self.store.run_dir(run_id)
        attempts = [safe_path(directory, item["answer"]).parent
                    for item in run.native.history if item.get("answer")]
        for path in (run.native.active_attempt, (run.native.pending_result or {}).get("directory")):
            if path:
                attempts.append(safe_path(directory, f"{path}/activity.json").parent)
        return export_activity_archive(directory, attempts)

    def detail(self, run_id):
        run = self.store.load(run_id)
        with self.store.connect() as db:
            rows = db.execute(
                "SELECT data FROM events WHERE run_id=? ORDER BY seq DESC LIMIT 100", (run_id,),
            ).fetchall()
        progress = {"text": "", "truncated": False}
        if run.native.active_attempt:
            progress = self.text_artifact(run_id, run.native.active_attempt + "/progress.md")
        pending = run.native.pending_result
        if not progress["text"] and pending and pending.get("directory"):
            progress = self.text_artifact(run_id, pending["directory"] + "/answer.md")
            if not progress["text"]:
                progress = self.text_artifact(run_id, pending["directory"] + "/progress.md")
        if not progress["text"] and run.native.history:
            last = run.native.history[-1]
            if last.get("answer"):
                progress = self.text_artifact(run_id, last["answer"])
        progress["checking_evidence"] = bool(
            pending and (pending.get("milestone") or {}).get("kind") in {"selection", "review"}
        )
        worker = self.jobs.status(run_id)
        attempt = run.native.active_attempt
        if not attempt and pending:
            attempt = pending.get("directory")
        if not attempt and run.native.history and run.native.history[-1].get("answer"):
            attempt = str(Path(run.native.history[-1]["answer"]).parent)
        run_dir = self.store.run_dir(run_id)
        prior_attempts = [safe_path(run_dir, item["answer"]).parent
                          for item in run.native.history[-20:] if item.get("answer")]
        activity = read_run_activity(run_dir, safe_path(run_dir, f"{attempt}/activity.json").parent if attempt else None,
                                     previous_attempt_directories=prior_attempts)
        activity["attempt"] = attempt
        formal_artifacts = list_formal_artifacts(self.store.run_dir(run_id))
        for item in formal_artifacts["items"]:
            item["reviewable"] = item["downloadable"] and selectable_source(item["path"])
        return {
            **self.summary(run),
            "discovery_request": run.discovery_request,
            "problem": present_problem(run.problem) if run.problem else None,
            "shortlist": [present_problem(p) for p in run.shortlist],
            "shortlist_bindings": {p.id: problem_fingerprint(p) for p in run.shortlist},
            "discovery_context": run.discovery_context.model_dump(mode="json") if run.discovery_context else None,
            "candidates": [c.model_dump(mode="json") for c in run.candidates],
            "events": [json.loads(row[0]) for row in rows],
            "metrics": run_metrics(run), "progress": progress,
            "report": self.text_artifact(run_id, "report.md", limit=1000000),
            "formal_artifacts": formal_artifacts,
            "review_evidence": evidence_manifest(run.review_evidence),
            "worker": worker,
            "activity": activity,
            "formal_resources": Coordinator(self.store).snapshot(run_id, "formal"),
            "stop_requested": (self.store.run_dir(run_id) / "stop.requested").exists(),
        }
