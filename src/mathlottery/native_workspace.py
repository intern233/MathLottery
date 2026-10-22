"""Workspace projections and complete visible context for native research/review."""

from __future__ import annotations

from pathlib import Path

from mathlottery import budget
from mathlottery.backends import BackendStatus
from mathlottery.candidates import CandidateStore, review_input
from mathlottery.config import Config
from mathlottery.models import Phase, Run, uid
from mathlottery.native_prompts import build_native_prompt, milestone_schema
from mathlottery.review_evidence import project as project_review_evidence
from mathlottery.storage import Store, atomic_write, json_text, safe_path


class NativeWorkspace:
    def __init__(self, store: Store, candidates: CandidateStore):
        self.store, self.candidates = store, candidates

    def path(self, run: Run) -> Path:
        root = self.store.run_dir(run.id)
        if run.phase == Phase.VERIFY:
            return safe_path(root, f"review-workspaces/{run.candidates[-1].id}")
        return safe_path(root, "workspace")

    def prepare(self, run: Run, config: Config) -> str:
        if run.phase == Phase.VERIFY:
            self.candidates.check(run)
            candidate_id = run.candidates[-1].id
            if run.native.reviewer_candidate_id != candidate_id:
                run.native.reviewer_candidate_id = candidate_id
                run.native.reviewer_session_id = None
                run.native.reviewer_response_id = None
        if not run.task_id:
            run.task_id = uid("task")
        workspace = self.path(run)
        workspace.mkdir(parents=True, exist_ok=True)
        safe_path(workspace, "submissions").mkdir(exist_ok=True)
        atomic_write(safe_path(workspace, "milestone.schema.json"), json_text(milestone_schema()))
        if run.problem:
            atomic_write(safe_path(workspace, "problem.json"), json_text(run.problem))
        if run.phase == Phase.VERIFY:
            atomic_write(
                safe_path(workspace, "candidate.json"), json_text(review_input(run.candidates[-1]))
            )
            project_review_evidence(run, workspace)
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
