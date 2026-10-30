"""Read-only browser views and downloads derived from authoritative checkpoints."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from mathlottery.config import Config
from mathlottery.find.discovery import problem_fingerprint
from mathlottery.find.risks import present_problem
from mathlottery.models import Run, Workflow, digest
from mathlottery.organize.downloads import summary as organization_summary
from mathlottery.runtime import budget
from mathlottery.runtime.resources import Coordinator
from mathlottery.storage.core import Store, safe_path
from mathlottery.telemetry.activity import export_activity_archive, read_activity, read_run_activity
from mathlottery.telemetry.metrics import run_metrics
from mathlottery.verify.artifacts import list_formal_artifacts
from mathlottery.verify.evidence import manifest as evidence_manifest
from mathlottery.verify.evidence import selectable_source
from mathlottery.web.jobs import Jobs
from mathlottery.web.outcomes import research_outcome
from mathlottery.web.settings import config_summary


class RunQueries:
    """Present saved runs without starting research or changing account state."""

    def __init__(self, store: Store, jobs: Jobs):
        self.store = store
        self.jobs = jobs

    def organized(self, run: Run):
        return organization_summary(self.store, run)

    def summary(self, run: Run):
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
            **run.model_dump(
                mode="json",
                include={
                    "id",
                    "workflow",
                    "mode",
                    "state",
                    "phase",
                    "iteration",
                    "created_at",
                    "updated_at",
                    "stop_reason",
                    "last_error",
                    "usage",
                    "execution",
                },
            ),
            "title": title,
            "problem_id": run.problem.id if run.problem and run.workflow != Workflow.FIND else None,
            # Group stages without conflating equal titles or revisions of a statement.
            "problem_key": digest(json.dumps([run.problem.id, run.problem.statement]))
            if run.problem and run.workflow != Workflow.FIND
            else None,
            "shortlist_count": len(run.shortlist),
            "discovery_run_id": run.discovery_context.source_run_id
            if run.discovery_context
            else None,
            "candidate_count": len(run.candidates) if run.workflow != Workflow.ORGANIZE else 0,
            "reviewed_candidate_count": sum(bool(c.reviews) for c in run.candidates)
            if run.workflow != Workflow.ORGANIZE
            else 0,
            "research_outcome": research_outcome(run),
            "finalization": run.native.finalization.model_dump(mode="json"),
            "organized_report": self.organized(run),
            "busy": busy,
            "resources": resources,
            "worker_state": resources["state"]
            if resources and resources["state"] in {"queued", "running"}
            else (worker or {}).get("state"),
            "elapsed_seconds": round(observed if observed is not None else budget.elapsed(run), 1),
            "elapsed_timing_basis": "last_resource_sample"
            if observed is not None
            else "wall_clock",
            "settings": config_summary(Config.model_validate(run.config)),
        }

    def bootstrap(self, config_loader: Callable[[], Config]):
        try:
            settings, error = config_summary(config_loader()), None
        except (ValueError, OSError):
            settings, error = (
                None,
                "Local configuration is invalid or unreadable; check config.yaml.",
            )
        return {
            "settings": settings,
            "config_error": error,
            "runs": [self.summary(run) for run in self.store.list_runs()],
            "problems": [present_problem(p) for p in self.store.list_problems()],
        }

    def text_artifact(self, run_id, relative, limit=200000):
        path = safe_path(self.store.run_dir(run_id), relative)
        if not path.is_file():
            return {"text": "", "truncated": False}
        with path.open("rb") as stream:
            data = stream.read(limit + 1)
        return {
            "text": data[:limit].decode("utf-8", errors="replace"),
            "truncated": len(data) > limit,
        }

    def activity_archive(self, run_id):
        run = self.store.load(run_id)
        directory = self.store.run_dir(run_id)
        attempts = [
            safe_path(directory, item["answer"]).parent
            for item in run.native.history
            if item.get("answer")
        ]
        for path in (run.native.active_attempt, (run.native.pending_result or {}).get("directory")):
            if path:
                attempts.append(safe_path(directory, f"{path}/activity.json").parent)
        for item in [
            *run.native.solve_team.active_attempts,
            *run.native.solve_team.pending_receipts,
        ]:
            attempts.append(safe_path(directory, item["directory"]))
        return export_activity_archive(directory, attempts)

    def detail(self, run_id):
        run = self.store.load(run_id)
        with self.store.connect() as db:
            rows = db.execute(
                "SELECT data FROM events WHERE run_id=? ORDER BY seq DESC LIMIT 100",
                (run_id,),
            ).fetchall()
        progress = {"text": "", "truncated": False}
        team_attempts = run.native.solve_team.active_attempts
        team_primary = next((a for a in team_attempts if a["worker_id"] == "primary"), None)
        team_attempt = (team_primary or (team_attempts[-1] if team_attempts else {})).get(
            "directory"
        )
        if run.native.active_attempt:
            progress = self.text_artifact(run_id, run.native.active_attempt + "/progress.md")
        elif team_attempt:
            progress = self.text_artifact(run_id, team_attempt + "/progress.md")
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
        attempt = run.native.active_attempt or team_attempt
        if not attempt and pending:
            attempt = pending.get("directory")
        if not attempt and run.native.history and run.native.history[-1].get("answer"):
            attempt = str(Path(run.native.history[-1]["answer"]).parent)
        run_dir = self.store.run_dir(run_id)
        prior_attempts = [
            safe_path(run_dir, item["answer"]).parent
            for item in run.native.history[-20:]
            if item.get("answer")
        ]
        prior_attempts += [safe_path(run_dir, item["directory"]) for item in team_attempts]
        activity = read_run_activity(
            run_dir,
            safe_path(run_dir, f"{attempt}/activity.json").parent if attempt else None,
            previous_attempt_directories=prior_attempts,
        )
        activity["attempt"] = attempt
        formal_artifacts = list_formal_artifacts(self.store.run_dir(run_id))
        for item in formal_artifacts["items"]:
            item["reviewable"] = item["downloadable"] and selectable_source(item["path"])
        return {
            **self.summary(run),
            "solve_team": self.solve_team_detail(run),
            "discovery_request": run.discovery_request,
            "problem": present_problem(run.problem) if run.problem else None,
            "shortlist": [present_problem(p) for p in run.shortlist],
            "shortlist_bindings": {p.id: problem_fingerprint(p) for p in run.shortlist},
            "discovery_context": run.discovery_context.model_dump(mode="json")
            if run.discovery_context
            else None,
            "candidates": [c.model_dump(mode="json") for c in run.candidates],
            "events": [json.loads(row[0]) for row in rows],
            "metrics": run_metrics(run),
            "progress": progress,
            "report": self.text_artifact(run_id, "report.md", limit=1000000),
            "formal_artifacts": formal_artifacts,
            "review_evidence": evidence_manifest(run.review_evidence),
            "worker": worker,
            "activity": activity,
            "formal_resources": Coordinator(self.store).snapshot(run_id, "formal"),
            "stop_requested": (self.store.run_dir(run_id) / "stop.requested").exists(),
        }

    def solve_team_detail(self, run: Run):
        if run.workflow != Workflow.SOLVE:
            return None
        from mathlottery.solve.board import SolveBoard

        team = run.native.solve_team
        settings = Config.model_validate(run.config).solve
        attempts = {
            item["worker_id"]: str(Path(item["answer"]).parent)
            for item in run.native.history
            if item.get("worker_id") and item.get("answer")
        }
        attempts.update(
            {
                item["worker_id"]: item["directory"]
                for item in [*team.pending_receipts, *team.active_attempts]
            }
        )
        workers = []
        for worker in team.workers.values():
            item = worker.model_dump(mode="json", exclude={"session_id", "response_id"})
            attempt = attempts.get(worker.id)
            item["activity"] = (
                read_activity(safe_path(self.store.run_dir(run.id), attempt + "/activity.json"))
                if attempt
                else None
            )
            item["progress"] = (
                self.text_artifact(run.id, attempt + "/progress.md", limit=20000)
                if attempt
                else None
            )
            workers.append(item)
        # Public UI never receives transport sessions or raw invocation receipts.
        return {
            "parallel_agents": settings.parallel_agents,
            "max_groups": settings.max_groups,
            "effective_max_groups": settings.group_limit,
            "rounds": team.rounds,
            "decision": team.decision,
            "groups": [g.model_dump(mode="json") for g in team.groups],
            "workers": workers,
            "supervisor_usage": team.supervisor_usage.model_dump(mode="json"),
            "messages": SolveBoard(self.store, run.id).messages(),
        }
