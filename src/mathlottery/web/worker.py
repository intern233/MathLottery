"""Internal background entry point, independent of the browser/server lifetime."""

import argparse
import json
import os
import signal
import threading
from pathlib import Path

from mathlottery.config import Config
from mathlottery.demo import DemoBackend
from mathlottery.local_network import apply_network_environment
from mathlottery.models import now
from mathlottery.orchestrator import Orchestrator
from mathlottery.storage import Store, atomic_write, json_text
from mathlottery.web.jobs import Jobs


def execute(store, run_id, request):
    directory = Jobs(store).directory(run_id)
    finished = threading.Event()

    def propagate_stop():
        # A stop racing a queued resume must survive resume's removal of the core marker.
        while not finished.wait(0.1):
            if (directory / "stop.requested").exists():
                atomic_write(store.run_dir(run_id) / "stop.requested", now())

    watcher = threading.Thread(target=propagate_stop, daemon=True)
    watcher.start()
    atomic_write(directory / "status.json", json_text({"state": "running", "time": now()}))
    try:
        apply_network_environment(store.root)
        run = store.load(run_id)
        backend = DemoBackend(run.environment.get("demo_case", "correct")) if run.mode == "demo" else None
        engine = Orchestrator(store, backend)
        if (directory / "stop.requested").exists():
            engine.stop(run_id)
        elif request["action"] == "resume":
            engine.resume(
                run_id, config=Config.model_validate(request["config"]),
                message=request.get("message"),
            )
        elif request["action"] == "drive":
            engine.drive(run_id)
        else:
            raise ValueError("Unknown worker action")
        atomic_write(directory / "status.json", json_text({"state": "finished", "time": now()}))
    except Exception as exc:
        atomic_write(
            directory / "status.json",
            json_text({"state": "error", "error": f"{type(exc).__name__}: {exc}", "time": now()}),
        )
    finally:
        finished.set()
        watcher.join(timeout=1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--lock-fd", type=int, required=True)
    args = parser.parse_args()
    # Do not let model/tool subprocesses inherit the worker ownership lock.
    os.set_inheritable(args.lock_fd, False)
    store = Store(args.root)
    directory = Jobs(store).directory(args.run_id)
    signal.signal(
        signal.SIGTERM,
        lambda *_: atomic_write(directory / "stop.requested", now()),
    )
    try:
        execute(store, args.run_id, json.loads((directory / "request.json").read_text()))
    finally:
        os.close(args.lock_fd)


if __name__ == "__main__":
    main()
