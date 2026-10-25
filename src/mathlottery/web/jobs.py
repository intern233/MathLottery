"""Detached workers with OS locks, durable status and cooperative cancellation."""

from __future__ import annotations

import fcntl
import json
import subprocess
import sys
import threading

from mathlottery.models import now
from mathlottery.storage import Store, atomic_write, json_text, safe_path


class BusyError(ValueError):
    pass


class Jobs:
    def __init__(self, store: Store):
        self.store = store

    def directory(self, run_id):
        return safe_path(self.store.run_dir(run_id), "web")

    def running(self, run_id, *, include_run_lock=True):
        paths = [self.directory(run_id) / "worker.lock"]
        if include_run_lock:
            paths.append(self.store.internal / "locks" / f"{run_id}.lock")
        for path in paths:
            if not path.exists():
                continue
            with path.open("a") as handle:
                try:
                    fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    return True
                finally:
                    fcntl.flock(handle, fcntl.LOCK_UN)
        return False

    def status(self, run_id):
        try:
            value = json.loads((self.directory(run_id) / "status.json").read_text())
        except (OSError, ValueError):
            return None
        if value.get("state") in {"queued", "running"} and not self.running(run_id, include_run_lock=False):
            return {"state": "interrupted", "time": value.get("time"),
                    "error": "Worker exited; resume the preserved checkpoint"}
        return value

    def launch(self, run_id: str, action: str, **options):
        directory = self.directory(run_id)
        directory.mkdir(parents=True, exist_ok=True)
        with (directory / "worker.lock").open("a") as handle:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise BusyError("This run already has an active worker") from exc
            try:
                with self.store.lock(run_id):
                    pass
            except ValueError as exc:
                raise BusyError(str(exc)) from exc
            (directory / "stop.requested").unlink(missing_ok=True)
            atomic_write(directory / "request.json", json_text({"action": action, **options}))
            atomic_write(directory / "status.json", json_text({"state": "queued", "time": now()}))
            try:
                with (directory / "worker.log").open("ab") as log:
                    process = subprocess.Popen(
                        [
                            sys.executable, "-m", "mathlottery.web.worker",
                            "--root", str(self.store.root), "--run-id", run_id,
                            "--lock-fd", str(handle.fileno()),
                        ],
                        stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                        start_new_session=True, pass_fds=(handle.fileno(),),
                        cwd=self.store.root,
                    )
            except OSError as exc:
                atomic_write(
                    directory / "status.json",
                    json_text({"state": "error", "error": str(exc), "time": now()}),
                )
                raise
            # Closing the parent's descriptor leaves the child's inherited lock held.
            threading.Thread(target=process.wait, daemon=True).start()

    def request_stop(self, run_id):
        atomic_write(self.directory(run_id) / "stop.requested", now())

