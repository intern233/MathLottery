"""Workspace-wide FIFO admission with crash-safe leases and sampled memory guardrails.

Locks, not PID files, own capacity. Queue records survive server restarts; a dead
owner is removed on the next inspection. Memory limits are cooperative and only
request cancellation of the owning run; they are not hard kernel quotas.
"""

from __future__ import annotations

import fcntl
import json
import os
import threading
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from mathlottery.models import now
from mathlottery.storage import atomic_write, json_text, safe_path


def available_memory_mb():
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemAvailable:"):
                return round(int(line.split()[1]) / 1024, 1)
    except (OSError, ValueError):
        pass
    return None


def process_tree_memory(pid):
    """Sum RSS of a process and current descendants (shared pages may be counted twice)."""
    processes = {}
    try:
        for entry in Path("/proc").iterdir():
            if not entry.name.isdigit():
                continue
            try:
                fields = (entry / "stat").read_text().rsplit(") ", 1)[1].split()
                if fields[0] != "Z":
                    processes[int(entry.name)] = (int(fields[1]), int(fields[21]))
            except (OSError, ValueError, IndexError):
                continue
        if pid not in processes:
            return None
        descendants = {pid}
        while True:
            children = {child for child, (parent, _) in processes.items() if parent in descendants}
            expanded = descendants | children
            if expanded == descendants:
                break
            descendants = expanded
        pages = sum(processes[child][1] for child in descendants)
        return round(pages * os.sysconf("SC_PAGE_SIZE") / 1024**2, 1)
    except (OSError, ValueError):
        return None


def _read(path, default):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return default


def _stop_requested(store, run_id):
    directory = store.run_dir(run_id)
    if (directory / "stop.requested").exists():
        return True
    # A resume clears the core marker. The browser worker's separate marker must
    # still cancel admission during that narrow window, without blocking later CLI resumes.
    if (directory / "web/stop.requested").exists() and (directory / "web/worker.lock").exists():
        with (directory / "web/worker.lock").open("a") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return True
    return False


class Coordinator:
    def __init__(self, store):
        self.store = store
        self.folder = store.internal / "resources"
        self.folder.mkdir(parents=True, exist_ok=True)

    def snapshot_path(self, run_id, kind="run"):
        return self.store.run_dir(run_id) / ("resources.json" if kind == "run" else "formal-resources.json")

    def stop_identified_orphan(self, entry):
        if entry["kind"] != "run":
            return
        try:
            run = self.store.load(entry["run_id"])
        except ValueError:
            return
        if run.mode in {"codex", "work"} and run.native.active_attempt:
            from mathlottery.native_backend import NativeWorkBackend

            # PID start time, command output path and private process-group checks
            # must all succeed; never signal a process based only on its PID.
            NativeWorkBackend.stop_orphan(safe_path(self.store.run_dir(run.id), run.native.active_attempt))

    @contextmanager
    def transaction(self):
        with (self.folder / "queue.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            entries = _read(self.folder / "queue.json", [])
            live = []
            for entry in entries:
                with (self.folder / f"{entry['ticket']}.lease").open("a") as handle:
                    try:
                        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    except BlockingIOError:
                        live.append(entry)
                        continue
                snapshot = self.snapshot_path(entry["run_id"], entry["kind"])
                self.stop_identified_orphan(entry)
                value = _read(snapshot, {})
                value.update(state="interrupted", updated_at=now(), queue_position=None,
                             reason="Worker exited; resume the preserved checkpoint")
                atomic_write(snapshot, json_text(value))
                (self.folder / f"{entry['ticket']}.lease").unlink(missing_ok=True)
            try:
                yield live
            finally:
                atomic_write(self.folder / "queue.json", json_text(live))
                fcntl.flock(lock, fcntl.LOCK_UN)

    def snapshot(self, run_id, kind="run"):
        # Reconcile crashed owners before exposing status. No model call is restarted.
        with self.transaction():
            pass
        value = _read(self.snapshot_path(run_id, kind), None)
        if not isinstance(value, dict):
            return None
        return {key: value.get(key) for key in ("state", "queued_at", "started_at", "updated_at",
                                               "queue_position", "reason", "memory")}

    @contextmanager
    def admission(self, run, config, kind="run", cancelled=None):
        settings = config.resources
        limit = settings.max_concurrent_runs if kind == "run" else settings.max_concurrent_formal
        cancelled = cancelled or (lambda: _stop_requested(self.store, run.id))
        ticket = uuid4().hex
        lease_path = self.folder / f"{ticket}.lease"
        path = self.snapshot_path(run.id, kind)
        initial = now()
        value = {"state": "queued", "queued_at": initial, "started_at": None,
                 "updated_at": initial, "queue_position": None, "reason": "capacity", "memory": None}
        done = threading.Event()
        monitor = None
        acquired = False
        memory_reason = None

        def write():
            value["updated_at"] = now()
            atomic_write(path, json_text(value))

        def observe():
            nonlocal memory_reason
            peak = 0.0
            while not done.is_set():
                rss = process_tree_memory(os.getpid())
                if rss is not None:
                    peak = max(peak, rss)
                value["memory"] = {"available": rss is not None, "rss_mb": rss,
                                   "peak_rss_mb": peak if rss is not None else None,
                                   "available_mb": available_memory_mb(), "sampled_at": now(),
                                   "scope": "local_process_tree"}
                if settings.memory_soft_limit_mb is not None and rss is not None and rss > settings.memory_soft_limit_mb:
                    memory_reason = "Sampled local process-tree RSS exceeded the configured soft limit"
                    value["reason"] = memory_reason
                    atomic_write(self.store.run_dir(run.id) / "stop.requested", now())
                write()
                done.wait(settings.sample_interval_seconds)

        with lease_path.open("a") as lease:
            fcntl.flock(lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
            try:
                with self.transaction() as entries:
                    entries.append({"ticket": ticket, "run_id": run.id, "kind": kind,
                                    "state": "queued", "limit": limit})
                    write()
                while not cancelled():
                    free_memory = available_memory_mb()
                    memory_ok = free_memory is None or free_memory >= settings.min_available_memory_mb
                    with self.transaction() as entries:
                        relevant = [item for item in entries if item["kind"] == kind]
                        effective_limit = min(item["limit"] for item in relevant)
                        active = sum(item["state"] == "running" for item in relevant)
                        waiting = [item for item in relevant if item["state"] == "queued"]
                        position = next(i for i, item in enumerate(waiting) if item["ticket"] == ticket)
                        value["queue_position"] = position + 1
                        value["reason"] = "capacity" if memory_ok else "low_available_memory"
                        if memory_ok and position == 0 and active < effective_limit:
                            next(item for item in entries if item["ticket"] == ticket)["state"] = "running"
                            acquired = True
                            value.update(state="running", started_at=now(), queue_position=None, reason=None)
                        write()
                    if acquired:
                        if kind == "run":
                            monitor = threading.Thread(target=observe, daemon=True)
                            monitor.start()
                        break
                    done.wait(min(settings.sample_interval_seconds, 0.25))
                yield acquired
            finally:
                done.set()
                if monitor:
                    monitor.join(timeout=5)
                with self.transaction() as entries:
                    entries[:] = [item for item in entries if item["ticket"] != ticket]
                    value.update(state="released" if acquired else "cancelled", queue_position=None)
                    if memory_reason:
                        value["reason"] = memory_reason
                    elif not acquired:
                        value["reason"] = "Queue wait cancelled; no model call was started"
                    write()
                fcntl.flock(lease, fcntl.LOCK_UN)
                lease_path.unlink(missing_ok=True)


@contextmanager
def run_admission(store, run, config):
    with Coordinator(store).admission(run, config) as admitted:
        yield admitted


@contextmanager
def formal_admission(store, run, config, cancelled=None):
    with Coordinator(store).admission(run, config, "formal", cancelled) as admitted:
        yield admitted
