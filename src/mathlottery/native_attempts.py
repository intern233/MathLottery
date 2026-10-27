"""Durable native invocation receipts, accounting and interrupted-session recovery."""

from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from mathlottery import budget
from mathlottery.agent_backend import research_backend
from mathlottery.backends import BackendResult, BackendStatus
from mathlottery.config import Config
from mathlottery.milestones import read_milestone
from mathlottery.models import Phase, Run, now, uid
from mathlottery.native_backend import NativeWorkBackend
from mathlottery.native_workspace import NativeWorkspace
from mathlottery.storage import atomic_write, json_text, safe_path

if TYPE_CHECKING:
    from mathlottery.orchestrator import Orchestrator


class NativeAttempts:
    def __init__(self, engine: Orchestrator, workspaces: NativeWorkspace):
        self.engine, self.store, self.workspaces = engine, engine.store, workspaces

    def invoke(self, run: Run, backend, prompt: str, config: Config) -> dict:
        directory = self.store.run_dir(run.id) / "tasks" / run.task_id / uid("attempt")
        run.native.active_attempt = str(directory.relative_to(self.store.run_dir(run.id)))
        self.store.save(run, "native_attempt_started", attempt=run.native.active_attempt)
        atomic_write(directory / "turn.json", json_text({
            "steering": run.native.steering, "started_at": now(),
            "finalizing": run.native.finalization.status == "running",
        }))
        timeout = budget.remaining(run, config)
        if config.backend.native_turn_timeout_seconds is not None:
            timeout = min(timeout, config.backend.native_turn_timeout_seconds)
        started = time.monotonic()
        result = backend.invoke_native(
            prompt,
            directory,
            self.workspaces.path(run),
            timeout,
            session_id=getattr(run.native, self.session_field(run)),
            reviewer=run.phase in {Phase.VERIFY, Phase.ORGANIZE},
            cancelled=lambda: self.engine._cancelled(run, config),
            on_session=lambda value: self.remember_session(run, value),
        )
        receipt = self.capture(run, result, directory)
        receipt["invocation_seconds"] = round(time.monotonic() - started, 3)
        atomic_write(directory / "receipt.json", json_text(receipt))
        return receipt

    def capture(self, run: Run, result: BackendResult, directory: Path) -> dict:
        milestone, error = None, None
        turn_path = directory / "turn.json"
        turn = json.loads(turn_path.read_text()) if turn_path.exists() else {}
        if result.status == BackendStatus.COMPLETED:
            try:
                milestone = read_milestone(run, self.workspaces.path(run), result.text)
            except (ValueError, OSError) as exc:
                error = str(exc)
        return {
            "result": asdict(result),
            "milestone": milestone,
            "checkpoint_error": error,
            "steering": turn.get("steering") if turn_path.exists() else run.native.steering,
            # Use original turn time, not recovery time, for search freshness.
            "source_observed_at": turn.get("started_at"),
            "directory": str(directory.relative_to(self.store.run_dir(run.id))),
            "finalizing": turn.get("finalizing", False),
        }

    def session_field(self, run: Run):
        role = "reviewer" if run.phase == Phase.VERIFY else "solver"
        suffix = "response_id" if run.mode == "chat" else "session_id"
        return f"{role}_{suffix}"

    def remember_session(self, run: Run, value: str):
        setattr(run.native, self.session_field(run), value)
        self.store.save(
            run,
            "native_session_started",
            backend=run.mode,
            role=("organization" if run.phase == Phase.ORGANIZE
                  else "review" if run.phase == Phase.VERIFY else "research"),
            session_id=value,
        )

    def queue(self, run: Run, receipt: dict):
        result = BackendResult(**receipt["result"])
        # A background response is charged once when its final state is known, including
        # after recovery. An unresolved response never starts another model invocation.
        if not result.pending:
            self.engine._account(run, result)
            if result.invoked:
                run.iteration += 1
        run.native.pending_result = receipt
        run.native.active_attempt = None
        self.store.save(run, "native_result_received", usage=result.usage, status=result.status)

    def recover(self, run: Run, queue: Callable[[Run, dict], None]):
        if not run.native.active_attempt:
            return
        directory = safe_path(self.store.run_dir(run.id), run.native.active_attempt)
        path = directory / "receipt.json"
        receipt = json.loads(path.read_text()) if path.is_file() else None
        if run.mode == "chat" and (not receipt or receipt["result"].get("pending")):
            config = Config.model_validate(run.config)
            config.backend.mode = "chat"
            backend = self.engine.backend_override or research_backend(config.backend, self.store.root)
            result = backend.recover_native(
                directory,
                budget.remaining(run, config),
                cancelled=lambda: self.engine._cancelled(run, config),
                on_session=lambda value: self.remember_session(run, value),
            )
            receipt = self.capture(run, result, directory)
            atomic_write(path, json_text(receipt))
            queue(run, receipt)
            return
        NativeWorkBackend.stop_orphan(directory)
        if path.is_file():
            queue(run, receipt)
            return
        # A killed runner may not have reached the post-call receipt. Keep its session and
        # logs, charge the unknown attempt, and let Codex inspect its own history on resume.
        turn_path = directory / "turn.json"
        turn = json.loads(turn_path.read_text()) if turn_path.is_file() else {}
        queue(
            run,
            {
                "result": asdict(
                    BackendResult(
                        BackendStatus.INTERRUPTED,
                        invoked=True,
                        error="Recovered an interrupted native attempt; its token usage is unknown",
                    )
                ),
                "milestone": None,
                "checkpoint_error": None,
                "directory": run.native.active_attempt,
                "recovered": True,
                "finalizing": turn.get("finalizing", False),
            },
        )
