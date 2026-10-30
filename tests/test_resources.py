import json
import os
import subprocess
import sys
import time
from types import SimpleNamespace

import pytest

from mathlottery.config import Config
from mathlottery.runtime.resources import Coordinator, process_tree_memory
from mathlottery.storage.core import Store
from mathlottery.telemetry.activity import ActivityReporter, read_activity

CHILD = """
import sys, time
from pathlib import Path
from types import SimpleNamespace
from mathlottery.config import Config
from mathlottery.runtime.resources import Coordinator
from mathlottery.storage.core import Store
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
    from mathlottery.providers.codex import NativeWorkBackend
    from mathlottery.runtime.orchestrator import Orchestrator

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
    monkeypatch.setattr("mathlottery.runtime.resources.process_tree_memory", lambda pid: 300.0)
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
    monkeypatch.setattr("mathlottery.runtime.resources.available_memory_mb", lambda: 32.0)
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
    from mathlottery.runtime.orchestrator import Orchestrator
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


def test_resume_retains_cumulative_time_and_historical_peak_without_offline_time(tmp_path, monkeypatch):
    store = Store(tmp_path)
    run = SimpleNamespace(id="run-000000000010")
    store.run_dir(run.id).mkdir(parents=True)
    clock, rss = [100.0], [600.0]
    monkeypatch.setattr("mathlottery.runtime.resources.time", SimpleNamespace(monotonic=lambda: clock[0]))
    monkeypatch.setattr("mathlottery.runtime.resources.process_tree_memory", lambda pid: rss[0])
    config = Config(resources={"min_available_memory_mb": 0, "sample_interval_seconds": 0.1})
    coordinator = Coordinator(store)
    with coordinator.admission(run, config) as admitted:
        assert admitted
        wait_for(lambda: (coordinator.snapshot(run.id).get("memory") or {}).get("peak_rss_mb") == 600)
        clock[0] += 10
    assert coordinator.snapshot(run.id)["cumulative"]["active_seconds"] == 10
    clock[0] += 10000
    rss[0] = 120
    with coordinator.admission(run, config):
        wait_for(lambda: (coordinator.snapshot(run.id).get("memory") or {}).get("peak_rss_mb") == 120)
        clock[0] += 4
    final = Coordinator(Store(tmp_path)).snapshot(run.id)
    assert final["attempt"]["active_seconds"] == 4
    assert final["memory"]["peak_rss_mb"] == 120
    assert final["cumulative"] == {"attempts": 2, "queue_seconds": 0.0, "active_seconds": 14.0,
                                   "peak_rss_mb": 600.0, "history_complete": True, "timing_basis": "monotonic"}
    assert [item["active_seconds"] for item in final["recent_attempts"]] == [10, 4]


def test_cancelled_queue_time_is_separate_and_counts_no_active_time(tmp_path, monkeypatch):
    store = Store(tmp_path)
    run = SimpleNamespace(id="run-000000000011")
    store.run_dir(run.id).mkdir(parents=True)
    clock = [0.0]
    monkeypatch.setattr("mathlottery.runtime.resources.time", SimpleNamespace(monotonic=lambda: clock[0]))
    monkeypatch.setattr("mathlottery.runtime.resources.available_memory_mb", lambda: 0)
    calls = 0

    def cancelled():
        nonlocal calls
        calls += 1
        clock[0] += 3
        return calls > 1

    config = Config(resources={"sample_interval_seconds": 0.1})
    with Coordinator(store).admission(run, config, cancelled=cancelled) as admitted:
        assert not admitted
    value = Coordinator(store).snapshot(run.id)
    assert value["cumulative"]["active_seconds"] == 0
    assert value["cumulative"]["queue_seconds"] == 6
    assert value["attempt"]["state"] == "cancelled"
    assert value["cumulative"]["peak_rss_mb"] is None


def test_legacy_snapshot_preserves_observed_peak_and_marks_missing_history(tmp_path, monkeypatch):
    store = Store(tmp_path)
    run = SimpleNamespace(id="run-000000000012")
    store.run_dir(run.id).mkdir(parents=True)
    coordinator = Coordinator(store)
    coordinator.snapshot_path(run.id).write_text(json.dumps({
        "state": "released", "queued_at": "2025-01-01T00:00:00+00:00",
        "started_at": "2025-01-01T00:00:03+00:00", "updated_at": "2025-01-01T00:00:13+00:00",
        "memory": {"available": True, "peak_rss_mb": 2400, "rss_mb": 100},
    }))
    prior = coordinator.snapshot(run.id)
    assert not prior["cumulative"]["history_complete"]
    assert prior["cumulative"]["queue_seconds"] == 3
    assert prior["cumulative"]["active_seconds"] == 10
    monkeypatch.setattr("mathlottery.runtime.resources.process_tree_memory", lambda pid: None)
    with coordinator.admission(run, Config(resources={"min_available_memory_mb": 0})):
        pass
    value = coordinator.snapshot(run.id)
    assert value["cumulative"]["peak_rss_mb"] == 2400
    assert value["cumulative"]["active_seconds"] >= 10
    assert not value["cumulative"]["history_complete"]
    assert value["cumulative"]["timing_basis"] == "legacy_snapshot_and_monotonic"


def test_resource_history_is_bounded_but_totals_keep_all_admissions(tmp_path, monkeypatch):
    store = Store(tmp_path)
    run = SimpleNamespace(id="run-000000000013")
    store.run_dir(run.id).mkdir(parents=True)
    clock = [0.0]
    monkeypatch.setattr("mathlottery.runtime.resources.time", SimpleNamespace(monotonic=lambda: clock[0]))
    coordinator = Coordinator(store)
    config = Config(resources={"min_available_memory_mb": 0})
    for _ in range(23):
        with coordinator.admission(run, config, kind="formal"):
            clock[0] += 2
    value = coordinator.snapshot(run.id, kind="formal")
    assert len(value["recent_attempts"]) == 20
    assert value["recent_attempts"][0]["number"] == 4
    assert value["cumulative"]["attempts"] == 23
    assert value["cumulative"]["active_seconds"] == 46
    assert coordinator.snapshot_path(run.id, "formal").stat().st_size < 16000
    archive = store.run_dir(run.id) / "formal-resource-attempts.jsonl"
    archived = [json.loads(line) for line in archive.read_text().splitlines()]
    assert archived[0]["earlier_history"] == "none_observed"
    assert [item["attempt"]["number"] for item in archived[1:]] == list(range(1, 24))


def test_resource_snapshot_redacts_unknown_metadata_and_untrusted_values(tmp_path):
    store = Store(tmp_path)
    run_id = "run-000000000014"
    store.run_dir(run_id).mkdir(parents=True)
    coordinator = Coordinator(store)
    coordinator.snapshot_path(run_id).write_text(json.dumps({
        "state": {"token": "PRIVATE"}, "reason": "PRIVATE_PROXY", "updated_at": "PRIVATE_PATH",
        "memory": {"rss_mb": float("nan"), "peak_rss_mb": -1, "scope": "PRIVATE"},
        "cumulative": {"timing_basis": [], "active_seconds": "PRIVATE"},
        "attempt": {"state": [], "command": "PRIVATE"}, "recent_attempts": [None, {"token": "PRIVATE"}],
    }))
    value = coordinator.snapshot(run_id)
    assert "PRIVATE" not in json.dumps(value)
    assert value["memory"]["rss_mb"] is None
    assert value["memory"]["peak_rss_mb"] is None


def test_interrupted_resource_record_keeps_last_observed_time():
    from mathlottery.runtime.resources import _interrupt_snapshot

    value = _interrupt_snapshot({"state": "running", "queued_at": "2020-01-01T00:00:00+00:00",
                                 "started_at": "2020-01-01T00:00:01+00:00", "updated_at": "2020-01-01T00:00:06+00:00"})
    assert value["state"] == "interrupted"
    assert value["updated_at"] == "2020-01-01T00:00:06+00:00"
    assert value["cumulative"]["active_seconds"] == 5
    assert value["recent_attempts"][-1]["state"] == "interrupted"


def test_exception_releases_capacity_and_keeps_cumulative_observations(tmp_path, monkeypatch):
    store = Store(tmp_path)
    run = SimpleNamespace(id="run-000000000015")
    store.run_dir(run.id).mkdir(parents=True)
    clock = [0.0]
    monkeypatch.setattr("mathlottery.runtime.resources.time", SimpleNamespace(monotonic=lambda: clock[0]))
    config = Config(resources={"min_available_memory_mb": 0})
    coordinator = Coordinator(store)
    with pytest.raises(RuntimeError, match="PRIVATE_TOKEN"):
        with coordinator.admission(run, config, kind="formal"):
            clock[0] += 3
            raise RuntimeError("PRIVATE_TOKEN PRIVATE_PROXY")
    clock[0] += 1000
    with coordinator.admission(run, config, kind="formal"):
        clock[0] += 5
    value = coordinator.snapshot(run.id, kind="formal")
    assert value["cumulative"]["active_seconds"] == 8
    assert value["cumulative"]["attempts"] == 2
    assert "PRIVATE" not in coordinator.snapshot_path(run.id, "formal").read_text()


def test_crashed_execution_history_survives_resumption(processes):
    store, start = processes
    run_id, directory, owner = start(16)
    wait_for(lambda: (directory / "entered").exists())
    owner.kill()
    owner.wait(timeout=5)
    interrupted = Coordinator(store).snapshot(run_id)
    assert interrupted["state"] == "interrupted"
    observed = interrupted["cumulative"]["active_seconds"]
    time.sleep(0.1)
    assert Coordinator(store).snapshot(run_id)["cumulative"]["active_seconds"] == observed
    (directory / "entered").unlink()
    _, _, resumed = start(16)
    wait_for(lambda: (directory / "entered").exists())
    (directory / "release").touch()
    assert resumed.wait(timeout=5) == 0
    value = Coordinator(store).snapshot(run_id)
    assert value["cumulative"]["attempts"] == 2
    assert [item["state"] for item in value["recent_attempts"]] == ["interrupted", "released"]


def test_orphan_snapshot_without_queue_record_is_preserved_in_attempt_archive(tmp_path):
    store = Store(tmp_path)
    run = SimpleNamespace(id="run-000000000017")
    store.run_dir(run.id).mkdir(parents=True)
    coordinator = Coordinator(store)
    coordinator.snapshot_path(run.id, "formal").write_text(json.dumps({
        "state": "running", "queued_at": "2020-01-01T00:00:00+00:00",
        "started_at": "2020-01-01T00:00:01+00:00", "updated_at": "2020-01-01T00:00:06+00:00",
    }))
    with coordinator.admission(run, Config(resources={"min_available_memory_mb": 0}), kind="formal"):
        pass
    rows = [json.loads(line) for line in (store.run_dir(run.id) / "formal-resource-attempts.jsonl").read_text().splitlines()]
    assert rows[0]["earlier_history"] == "unavailable"
    assert [item["attempt"]["state"] for item in rows[1:]] == ["interrupted", "released"]
    assert rows[1]["attempt"]["active_seconds"] == 5
