"""Durable Solve invocations, sessions, and transport-level recovery.

Only invocation runs in backend threads. Preparing or remembering an attempt is
an owner-thread operation; backend callbacks write files, never Run state.
"""

from __future__ import annotations

import json
import time
from copy import copy
from dataclasses import asdict

from mathlottery.config import Config
from mathlottery.models import now, uid
from mathlottery.providers.base import BackendResult, BackendStatus
from mathlottery.providers.codex import NativeWorkBackend
from mathlottery.providers.registry import isolate_credentials, research_backend
from mathlottery.runtime import budget
from mathlottery.runtime.milestones import read_milestone
from mathlottery.runtime.prompts import milestone_schema
from mathlottery.solve.allocation import Allocation
from mathlottery.solve.board import Message
from mathlottery.solve.contracts import Supervision
from mathlottery.solve.lifecycle import supervised
from mathlottery.solve.routes import attempt_config, route_metadata
from mathlottery.storage.core import atomic_write, json_text, safe_path


def bounded_backend(config, engine):
    """Native shell/search/memory survive; nested spawning cannot evade the Solve cap."""
    settings = config.backend.model_copy(deep=True)
    settings.native_multi_agent = False
    backend = engine.backend_override or research_backend(settings, engine.store.root)
    return isolate_credentials(backend, config, engine.store.root)


class SolveAttempts:
    def __init__(self, engine, abort):
        self.engine, self.store, self.abort = engine, engine.store, abort

    def path(self, run, relative):
        return safe_path(self.store.run_dir(run.id), relative)

    def cancelled(self, run, config):
        if supervised(run, config):
            # The research deadline closes admissions, never an in-flight turn.
            return self.abort.is_set() or self.engine._stop_file(run).exists()
        return self.abort.is_set() or self.engine._cancelled(run, config)

    def prepare(self, run, worker=None):
        task_id = uid("task")
        identifier = worker.id if worker else "supervisor"
        workspace = "workspace" if identifier == "primary" else f"solve-workspaces/{identifier}"
        attempt = {
            "task_id": task_id,
            "worker_id": identifier,
            "group": worker.group if worker else "supervision",
            "workspace": workspace,
            "directory": f"tasks/{task_id}/{uid('attempt')}",
            "role": "research" if worker else "supervision",
            "started_at": now(),
        }
        config = Config.model_validate(run.config)
        slot_id = worker.slot_id if worker else (
            config.solve.agent_slots[0].id if config.solve.agent_slots else None
        )
        if config.solve.agent_slots:
            attempt.update(route_metadata(config, slot_id))
        else:
            # Historical runs can carry an explicit transport switch in run.mode.
            attempt.update(mode=run.mode, model=config.backend.model,
                           provider=config.backend.provider or run.mode)
        root = self.path(run, workspace)
        root.mkdir(parents=True, exist_ok=True)
        safe_path(root, "outbox").mkdir(exist_ok=True)
        safe_path(root, "submissions").mkdir(exist_ok=True)
        atomic_write(safe_path(root, "problem.json"), json_text(run.problem))
        atomic_write(safe_path(root, "milestone.schema.json"), json_text(milestone_schema()))
        atomic_write(
            safe_path(root, "board-message.schema.json"), json_text(Message.model_json_schema())
        )
        atomic_write(
            safe_path(root, "allocation.schema.json"), json_text(Allocation.model_json_schema())
        )
        atomic_write(
            safe_path(root, "supervision.schema.json"), json_text(Supervision.model_json_schema())
        )
        run.native.solve_team.active_attempts.append(attempt)
        if worker:
            worker.state = "running"
        self.store.save(run, "solve_agent_started", **attempt)
        return attempt

    def _session(self, run, attempt):
        team = run.native.solve_team
        suffix = "response_id" if attempt.get("mode", run.mode) == "chat" else "session_id"
        if attempt["role"] == "supervision":
            return getattr(team, f"supervisor_{suffix}")
        return getattr(team.workers[attempt["worker_id"]], suffix)

    def remember(self, run, attempt):
        path = self.path(run, attempt["directory"] + "/session.json")
        if not path.exists():
            return False
        value = json.loads(path.read_text())["id"]
        team = run.native.solve_team
        suffix = "response_id" if attempt.get("mode", run.mode) == "chat" else "session_id"
        if attempt["role"] == "supervision":
            field, owner = f"supervisor_{suffix}", team
        else:
            field, owner = suffix, team.workers[attempt["worker_id"]]
            if owner.id == "primary":
                setattr(run.native, f"solver_{suffix}", value)
        changed = getattr(owner, field) != value
        setattr(owner, field, value)
        return changed

    def invoke(self, run, attempt, prompt, config, *, recover=False):
        """No Run mutation here: this method also executes in worker threads."""
        directory = self.path(run, attempt["directory"])
        workspace = self.path(run, attempt["workspace"])
        atomic_write(directory / "prompt.md", prompt)
        atomic_write(directory / "turn.json", json_text(attempt))
        selected_config = attempt_config(config, attempt)
        backend = bounded_backend(selected_config, self.engine)
        if supervised(run, config) and hasattr(backend, "local_tools"):
            from mathlottery.solve.board import SolveBoard
            from mathlottery.solve.board_tools import BoardTools

            # Even an injected/shared transport gets attempt-local capabilities;
            # concurrent workers must not overwrite each other's board identity.
            backend = copy(backend)
            backend.local_tools = BoardTools(
                SolveBoard(self.store, run.id), attempt["worker_id"], attempt["group"], workspace,
            )
        timeout = float("inf") if supervised(run, config) else budget.remaining(run, config)
        if attempt["role"] == "supervision":
            timeout = min(timeout, config.solve.supervisor_timeout_seconds)
        elif selected_config.backend.native_turn_timeout_seconds is not None:
            timeout = min(timeout, selected_config.backend.native_turn_timeout_seconds)
        started = time.monotonic()
        kwargs = {
            "cancelled": lambda: self.cancelled(run, config),
            "on_session": lambda value: atomic_write(
                directory / "session.json", json_text({"id": value})
            ),
        }
        try:
            if recover:
                result = backend.recover_native(directory, timeout, **kwargs)
            else:
                result = backend.invoke_native(
                    prompt,
                    directory,
                    workspace,
                    timeout,
                    session_id=self._session(run, attempt),
                    **kwargs,
                )
        except Exception as exc:
            result = BackendResult(
                BackendStatus.FAILED,
                invoked=True,
                error=f"Solve agent transport error: {type(exc).__name__}: {exc}",
            )
        milestone, error = None, None
        if result.status == BackendStatus.COMPLETED and attempt["role"] == "research":
            try:
                snapshot = run.model_copy(update={
                    "task_id": attempt["task_id"], "mode": selected_config.backend.mode,
                })
                milestone = read_milestone(snapshot, workspace, result.text)
            except (ValueError, OSError) as exc:
                error = str(exc)
        receipt = {
            **attempt,
            "result": asdict(result),
            "milestone": milestone,
            "checkpoint_error": error,
            "steering": run.native.steering,
            "source_observed_at": attempt["started_at"],
            "invocation_seconds": round(time.monotonic() - started, 3),
            "team_worker": True,
        }
        atomic_write(directory / "answer.md", result.text)
        atomic_write(directory / "receipt.json", json_text(receipt))
        return receipt

    def recover(self, run, attempt, config):
        """Recover the durable receipt, polling an existing hosted call if needed."""
        directory = self.path(run, attempt["directory"])
        file = directory / "receipt.json"
        receipt = json.loads(file.read_text()) if file.exists() else None
        attempt_config(config, attempt)  # Validate the saved route even for a durable receipt.
        if attempt.get("mode", run.mode) == "chat" and (not receipt or receipt["result"].get("pending")):
            prompt_path = directory / "prompt.md"
            return self.invoke(
                run,
                attempt,
                prompt_path.read_text() if prompt_path.exists() else "",
                config,
                recover=True,
            )
        NativeWorkBackend.stop_orphan(directory)
        if receipt is None:
            receipt = {
                **attempt,
                "result": asdict(
                    BackendResult(
                        BackendStatus.INTERRUPTED,
                        invoked=True,
                        error="Recovered interrupted Solve researcher; usage unknown",
                    )
                ),
                "milestone": None,
                "checkpoint_error": None,
                "team_worker": True,
                "recovered": True,
            }
            atomic_write(
                directory / "answer.md", "Interrupted; resume the saved conversation and files."
            )
            atomic_write(file, json_text(receipt))
        return receipt
