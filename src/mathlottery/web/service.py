"""Public browser application façade composed of requests, queries and commands.

Keep the HTTP layer independent of presentation and workflow implementation.
Request/settings imports remain available here for existing integrations.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from mathlottery.config import Config, load_config
from mathlottery.storage.core import Store
from mathlottery.web.jobs import Jobs
from mathlottery.web.operations import WorkflowOperations
from mathlottery.web.queries import RunQueries
from mathlottery.web.requests import Overrides, ResumeRequest, StartRequest
from mathlottery.web.settings import config_summary, workspace_key

__all__ = [
    "Overrides",
    "ResumeRequest",
    "StartRequest",
    "WebService",
    "config_summary",
    "workspace_key",
]


class WebService:
    def __init__(self, root: Path, config_path: Path | None = None):
        self.store = Store(root)
        self.config_path = config_path
        self.jobs = Jobs(self.store)
        self.queries = RunQueries(self.store, self.jobs)
        # Read current workspace defaults at command time, never at service startup.
        self.operations = WorkflowOperations(self.store, self.jobs, lambda: self.config())

    def config(self):
        return load_config(self.store.root, self.config_path)

    def summary(self, run):
        return self.queries.summary(run)

    def bootstrap(self):
        return self.queries.bootstrap(self.config)

    def start(
        self,
        request: StartRequest,
        *,
        ensure_backend: Callable[[str, str], None] | None = None,
        validate_model: Callable[[Config], None] | None = None,
        ensure_agent_slots: Callable[[Config], None] | None = None,
        ensure_config: Callable[[Config], None] | None = None,
    ):
        run = self.operations.start(
            request,
            ensure_backend=ensure_backend,
            validate_model=validate_model,
            ensure_agent_slots=ensure_agent_slots,
            ensure_config=ensure_config,
        )
        return self.summary(run)

    def ensure_review_source_idle(self, run_id, *, include_run_lock=True):
        return self.operations.ensure_review_source_idle(run_id, include_run_lock=include_run_lock)

    def export_organized(self, run_id):
        return self.queries.organized(self.operations.export_organized(run_id))

    def resume(
        self,
        run_id,
        request: ResumeRequest,
        *,
        ensure_backend: Callable[[str, str], None] | None = None,
        ensure_agent_slots: Callable[[Config], None] | None = None,
        ensure_config: Callable[[Config], None] | None = None,
    ):
        return self.summary(self.operations.resume(
            run_id, request, ensure_backend=ensure_backend, ensure_agent_slots=ensure_agent_slots,
            ensure_config=ensure_config,
        ))

    def stop(self, run_id):
        return self.summary(self.operations.stop(run_id))

    def ensure_account_change_allowed(self, profile=None):
        return self.operations.ensure_account_change_allowed(profile)

    def text_artifact(self, run_id, relative, limit=200000):
        return self.queries.text_artifact(run_id, relative, limit)

    def activity_archive(self, run_id):
        return self.queries.activity_archive(run_id)

    def detail(self, run_id):
        return self.queries.detail(run_id)

    def solve_team_detail(self, run):
        return self.queries.solve_team_detail(run)
