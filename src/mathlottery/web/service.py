"""Browser application operations over the existing domain objects and checkpoints."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Literal
from urllib.parse import urlsplit

from pydantic import Field, model_validator

from mathlottery import budget
from mathlottery.candidates import CandidateStore
from mathlottery.config import Config, load_config
from mathlottery.discovery import problem_fingerprint
from mathlottery.metrics import run_metrics
from mathlottery.models import CandidateInput, Model, Problem, Workflow, digest
from mathlottery.orchestrator import Orchestrator
from mathlottery.review_evidence import capture as capture_review_evidence
from mathlottery.review_evidence import manifest as evidence_manifest
from mathlottery.review_evidence import selectable_source
from mathlottery.storage import Store, safe_path
from mathlottery.web.artifacts import list_formal_artifacts
from mathlottery.web.jobs import BusyError, Jobs


class Overrides(Model):
    backend: Literal["codex", "chat"] | None = None
    model: str | None = Field(default=None, min_length=1, max_length=200)
    reasoning_effort: str | None = Field(default=None, min_length=1, max_length=50)
    reasoning_mode: Literal["standard", "pro"] | None = None
    budget_minutes: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    max_iterations: int | None = Field(default=None, gt=0)
    native_multi_agent: bool | None = None
    native_memories: bool | None = None

    def apply(self, config):
        config = config.model_copy(deep=True)
        for field in ("model", "reasoning_effort"):
            if getattr(self, field) is not None:
                setattr(config.backend, field, getattr(self, field))
        if self.backend:
            config.backend.mode = self.backend
        if self.reasoning_mode is not None:
            if config.backend.mode != "chat":
                raise ValueError("Pro/standard reasoning mode applies only to the chat backend")
            config.backend.chat.reasoning_mode = self.reasoning_mode
        if self.budget_minutes is not None:
            config.budget.max_wall_time_minutes = self.budget_minutes
        if self.max_iterations is not None:
            config.budget.max_iterations = self.max_iterations
        for field in ("native_multi_agent", "native_memories"):
            if field in self.model_fields_set:
                if config.backend.mode != "codex":
                    raise ValueError("Native agent capabilities apply only to Codex")
                setattr(config.backend, field, getattr(self, field))
        return config


class StartRequest(Model):
    workflow: Literal["find", "solve", "verify"]
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


def config_summary(config):
    return {
        "backend": config.backend.mode,
        "model": config.backend.model,
        "reasoning_effort": config.backend.reasoning_effort,
        "reasoning_mode": config.backend.chat.reasoning_mode,
        "execution": config.backend.execution,
        "budget_minutes": config.budget.max_wall_time_minutes,
        "max_iterations": config.budget.max_iterations,
        "native_multi_agent": config.backend.native_multi_agent,
        "native_memories": config.backend.native_memories,
        "native_web_search": config.backend.native_web_search,
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
        return {
            **run.model_dump(mode="json", include={
                "id", "workflow", "mode", "state", "phase", "iteration", "created_at",
                "updated_at", "stop_reason", "last_error", "usage", "execution",
            }),
            "title": (run.discovery_request or "Find problems") if run.workflow == Workflow.FIND else run.problem.title if run.problem else "Find problems",
            "problem_id": run.problem.id if run.problem and run.workflow != Workflow.FIND else None,
            # Group stages without conflating equal titles or revisions of a statement.
            "problem_key": digest(json.dumps([run.problem.id, run.problem.statement])) if run.problem and run.workflow != Workflow.FIND else None,
            "shortlist_count": len(run.shortlist),
            "discovery_run_id": run.discovery_context.source_run_id if run.discovery_context else None,
            "candidate_count": len(run.candidates),
            "busy": self.jobs.running(run.id),
            "elapsed_seconds": round(budget.elapsed(run), 1),
            "settings": config_summary(Config.model_validate(run.config)),
        }

    def bootstrap(self):
        try:
            settings, error = config_summary(self.config()), None
        except (ValueError, OSError) as exc:
            settings, error = None, str(exc)
        return {
            "settings": settings, "config_error": error,
            "runs": [self.summary(run) for run in self.store.list_runs()],
            "problems": [p.model_dump(mode="json") for p in self.store.list_problems()],
        }

    def start(
        self, request: StartRequest, *, ensure_backend: Callable[[str, str], None] | None = None,
    ):
        config = request.options.apply(self.config())
        if config.backend.mode not in {"codex", "chat"} or config.backend.execution != "native":
            raise ValueError("The browser starts native codex/chat tasks; select these in config.yaml")
        if ensure_backend is not None:
            ensure_backend(config.backend.mode, config.backend.execution)
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
        problem, candidate, evidence = None, None, None
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
        )
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
                "Stop the source task and wait for its worker to finish before starting an independent review"
            )

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
        ).apply(Config.model_validate(run.config))
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

    def detail(self, run_id):
        run = self.store.load(run_id)
        with self.store.connect() as db:
            rows = db.execute(
                "SELECT data FROM events WHERE run_id=? ORDER BY seq DESC LIMIT 100", (run_id,),
            ).fetchall()
        progress = {"text": "", "truncated": False}
        if run.native.active_attempt:
            progress = self.text_artifact(run_id, run.native.active_attempt + "/progress.md")
        if not progress["text"] and run.native.history:
            last = run.native.history[-1]
            if last.get("answer"):
                progress = self.text_artifact(run_id, last["answer"])
        worker = self.text_artifact(run_id, "web/status.json", limit=10000)["text"]
        formal_artifacts = list_formal_artifacts(self.store.run_dir(run_id))
        for item in formal_artifacts["items"]:
            item["reviewable"] = item["downloadable"] and selectable_source(item["path"])
        return {
            **self.summary(run),
            "problem": run.problem.model_dump(mode="json") if run.problem else None,
            "shortlist": [p.model_dump(mode="json") for p in run.shortlist],
            "shortlist_bindings": {p.id: problem_fingerprint(p) for p in run.shortlist},
            "discovery_context": run.discovery_context.model_dump(mode="json") if run.discovery_context else None,
            "candidates": [c.model_dump(mode="json") for c in run.candidates],
            "events": [json.loads(row[0]) for row in rows],
            "metrics": run_metrics(run), "progress": progress,
            "report": self.text_artifact(run_id, "report.md", limit=1000000),
            "formal_artifacts": formal_artifacts,
            "review_evidence": evidence_manifest(run.review_evidence),
            "worker": json.loads(worker) if worker else None,
            "stop_requested": (self.store.run_dir(run_id) / "stop.requested").exists(),
        }
