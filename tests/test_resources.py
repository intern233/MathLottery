import json
import os
import subprocess
import sys
import time
from types import SimpleNamespace

import pytest

from mathlottery.activity import ActivityReporter, read_activity
from mathlottery.config import Config
from mathlottery.resources import Coordinator, process_tree_memory
from mathlottery.storage import Store

CHILD = """
import sys, time
from pathlib import Path
from types import SimpleNamespace
from mathlottery.config import Config
from mathlottery.resources import Coordinator
from mathlottery.storage import Store
root, run_id, kind, limit = sys.argv[1:]
store = Store(Path(root))
run = SimpleNamespace(id=run_id)
directory = store.run_dir(run_id)
directory.mkdir(parents=True, exist_ok=True)
config = Config(resources={'min_available_memory_mb': 0, 'sample_interval_seconds': 0.1,
                           'max_concurrent_runs': int(limit), 'max_concurrent_formal': int(limit)})
with Coordinator(store).admission(run, config, kind) as admitted:
    if admitted:
        (directory / 'entered').touch()
        while not (directory / 'release').exists():
            time.sleep(0.02)
"""


def wait_for(predicate, timeout=10):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.03)
    raise AssertionError("Timed out waiting for local resource test")


@pytest.fixture
def processes(tmp_path):
    store = Store(tmp_path)
    owned = []

    def start(index, kind="run", limit=1):
        run_id = f"run-{index:012x}"
        directory = store.run_dir(run_id)
        directory.mkdir(parents=True, exist_ok=True)
        process = subprocess.Popen([sys.executable, "-c", CHILD, str(tmp_path), run_id, kind, str(limit)],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        owned.append(process)
        return run_id, directory, process

    yield store, start
    for process in owned:
        if process.poll() is None:
            process.kill()
        process.wait(timeout=5)


def test_workspace_fifo_survives_owner_crash_without_duplicate_admission(processes):
    store, start = processes
    first, first_dir, owner = start(1)
    wait_for(lambda: (first_dir / "entered").exists())
    second, second_dir, waiting = start(2)
    coordinator = Coordinator(store)
    wait_for(lambda: (coordinator.snapshot(second) or {}).get("state") == "queued")
    assert not (second_dir / "entered").exists()
    assert coordinator.snapshot(second)["queue_position"] == 1
    # A fresh server-side coordinator sees the same live lock and cannot claim capacity.
    assert Coordinator(Store(store.root)).snapshot(first)["state"] == "running"
    owner.kill()
    owner.wait(timeout=5)
    wait_for(lambda: (second_dir / "entered").exists())
    assert coordinator.snapshot(first)["state"] == "interrupted"
    (second_dir / "release").touch()
    assert waiting.wait(timeout=5) == 0
    assert coordinator.snapshot(second)["state"] == "released"


def test_queued_stop_does_not_enter_execution_or_stop_other_owner(processes):
    store, start = processes
    _, first_dir, owner = start(3)
    wait_for(lambda: (first_dir / "entered").exists())
    second, second_dir, waiting = start(4)
    coordinator = Coordinator(store)
    wait_for(lambda: (coordinator.snapshot(second) or {}).get("state") == "queued")
    (second_dir / "stop.requested").touch()
    assert waiting.wait(timeout=5) == 0
    assert not (second_dir / "entered").exists()
    assert coordinator.snapshot(second)["state"] == "cancelled"
    assert owner.poll() is None


def test_crashed_executor_reclaims_only_its_identified_native_child(processes):
    from mathlottery.models import Problem, Workflow
    from mathlottery.native_backend import NativeWorkBackend
    from mathlottery.orchestrator import Orchestrator

    store, start = processes
    run = Orchestrator(store).create(Config(), workflow=Workflow.SOLVE, problem=Problem(
        id="orphan-test", title="Orphan recovery", statement="Test only"))
    run.native.active_attempt = "tasks/task-local/attempt-local"
    directory = store.run_dir(run.id) / run.native.active_attempt
    directory.mkdir(parents=True)
    store.save(run, "test_native_orphan")
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)", str(directory / "answer.md")],
                             start_new_session=True)
    unrelated = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"], start_new_session=True)
    try:
        (directory / "process.json").write_text(json.dumps({"pid": child.pid, "start": NativeWorkBackend.process_start(child.pid)}))
        _, run_directory, owner = start(int(run.id[4:], 16))
        wait_for(lambda: (run_directory / "entered").exists())
        owner.kill()
        owner.wait(timeout=5)
        assert Coordinator(store).snapshot(run.id)["state"] == "interrupted"
        assert child.wait(timeout=5) != 0
        assert unrelated.poll() is None
    finally:
        for process in (child, unrelated):
            if process.poll() is None:
                process.kill()
            process.wait(timeout=5)


def test_formal_gate_has_independent_workspace_capacity(processes):
    store, start = processes
    _, first_dir, _ = start(5, "formal")
    wait_for(lambda: (first_dir / "entered").exists())
    second, second_dir, waiting = start(6, "formal")
    wait_for(lambda: (Coordinator(store).snapshot(second, "formal") or {}).get("state") == "queued")
    assert not (second_dir / "entered").exists()
    _, research_dir, _ = start(7, "run")
    wait_for(lambda: (research_dir / "entered").exists())
    (second_dir / "stop.requested").touch()
    assert waiting.wait(timeout=5) == 0


def test_memory_soft_limit_requests_cooperative_stop_only(tmp_path, monkeypatch):
    store = Store(tmp_path)
    run = SimpleNamespace(id="run-000000000008")
    store.run_dir(run.id).mkdir(parents=True)
    monkeypatch.setattr("mathlottery.resources.process_tree_memory", lambda pid: 300.0)
    config = Config(resources={"memory_soft_limit_mb": 256, "min_available_memory_mb": 0,
                               "sample_interval_seconds": 0.1})
    with Coordinator(store).admission(run, config) as admitted:
        assert admitted
        wait_for(lambda: (store.run_dir(run.id) / "stop.requested").exists())
    value = Coordinator(store).snapshot(run.id)
    assert value["memory"]["rss_mb"] == 300.0
    assert value["memory"]["peak_rss_mb"] == 300.0
    assert "soft limit" in value["reason"]


def test_low_available_memory_queues_without_consuming_capacity(tmp_path, monkeypatch):
    store = Store(tmp_path)
    run = SimpleNamespace(id="run-000000000009")
    store.run_dir(run.id).mkdir(parents=True)
    monkeypatch.setattr("mathlottery.resources.available_memory_mb", lambda: 32.0)
    polls = 0

    def cancel():
        nonlocal polls
        polls += 1
        return polls > 1

    with Coordinator(store).admission(run, Config(), cancelled=cancel) as admitted:
        assert not admitted
        assert Coordinator(store).snapshot(run.id)["reason"] == "low_available_memory"


def test_actual_process_tree_rss_includes_a_child(tmp_path):
    initial = process_tree_memory(os.getpid())
    assert initial and initial > 0
    ready = tmp_path / "ready"
    code = "import pathlib,sys,time; data=bytearray(32*1024*1024); pathlib.Path(sys.argv[1]).touch(); time.sleep(30)"
    process = subprocess.Popen([sys.executable, "-c", code, str(ready)])
    try:
        wait_for(ready.exists)
        assert process_tree_memory(os.getpid()) > initial + 20
    finally:
        process.kill()
        process.wait(timeout=5)


def test_activity_projection_is_bounded_and_excludes_tool_payloads(tmp_path):
    reporter = ActivityReporter(tmp_path)
    for index in range(40):
        reporter.codex({"type": "item.completed", "item": {"id": f"private-{index}",
            "type": "command_execution", "command": "SECRET_PROXY=secret.invalid", "aggregated_output": "secret-token"}})
    response = {"id": "resp_private", "status": "in_progress", "output": [
        {"id": "search_private", "type": "web_search_call", "status": "completed",
         "action": {"query": "private query"}}]}
    reporter.response(response)
    reporter.response(response)
    value = read_activity(tmp_path / "activity.json")
    assert len(value["recent"]) == 30
    assert sum(item["kind"] == "search" for item in value["recent"]) == 1
    assert value["current"]["kind"] == "search"
    raw = json.dumps(value)
    assert all(secret not in raw for secret in ("private", "secret", "command_execution", "query"))


def test_empty_activity_is_explicitly_unavailable(tmp_path):
    assert read_activity(tmp_path / "missing.json") == {
        "available": False, "last_active_at": None, "current": None, "recent": [],
    }


def test_activity_ignores_unknown_or_malformed_event_metadata(tmp_path):
    reporter = ActivityReporter(tmp_path)
    reporter.codex({"type": {"unexpected": "value"}})
    reporter.codex({"type": "item.completed", "item": {"type": []}})
    reporter.response({"status": {}, "output": [{"type": []}, {"type": "message", "status": {}}]})
    assert not read_activity(tmp_path / "activity.json")["available"]


def test_web_detail_reads_safe_activity_without_reparsing_raw_event_log(tmp_path):
    from mathlottery.models import Problem, Workflow
    from mathlottery.orchestrator import Orchestrator
    from mathlottery.web.service import WebService

    store = Store(tmp_path)
    run = Orchestrator(store).create(Config(), workflow=Workflow.SOLVE, problem=Problem(
        id="activity-problem", title="Telemetry test", statement="A test statement"))
    run.native.active_attempt = "tasks/task-example/attempt-example"
    attempt = store.run_dir(run.id) / run.native.active_attempt
    attempt.mkdir(parents=True)
    ActivityReporter(attempt).record("search", "completed", "not-public")
    (attempt / "codex.events.jsonl").write_text("Sensitive raw data must not enter the activity projection")
    store.save(run, "test_activity")
    detail = WebService(tmp_path).detail(run.id)
    assert detail["activity"]["current"]["kind"] == "search"
    assert detail["activity"]["available"]
    assert "Sensitive" not in json.dumps(detail["activity"])
