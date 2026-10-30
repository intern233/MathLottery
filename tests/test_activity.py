import json
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from mathlottery.telemetry.activity import (
    ActivityReporter,
    controller_activity,
    interrupt_controller_activity,
    read_run_activity,
)


def test_controller_heartbeat_is_separate_from_visible_progress(tmp_path):
    with controller_activity(tmp_path, "sources", heartbeat_seconds=0.05):
        initial = read_run_activity(tmp_path)
        deadline = time.monotonic() + 5
        while True:
            current = read_run_activity(tmp_path)
            if current["last_heartbeat_at"] != initial["last_heartbeat_at"]:
                break
            assert time.monotonic() < deadline
            time.sleep(0.01)
        assert current["last_active_at"] == initial["last_active_at"]
        assert len(current["recent"]) == 1
        assert current["current"]["duration_seconds"] >= 0.05
        assert not current["current"]["heartbeat_stale"]
    final = read_run_activity(tmp_path)
    assert final["current"]["stage"] == "sources"
    assert final["current"]["status"] == "completed"
    assert final["current"]["duration_seconds"] >= 0.05
    assert final["active_controllers"] == []


@pytest.mark.parametrize("status", ["failed", "cancelled", "incomplete"])
def test_controller_handled_status_is_preserved(tmp_path, status):
    with controller_activity(tmp_path, "formal_replay") as operation:
        operation.set_status(status)
    assert read_run_activity(tmp_path)["current"]["status"] == status


def test_controller_failure_does_not_disclose_exception_details(tmp_path):
    with pytest.raises(RuntimeError, match="private-token"):
        with controller_activity(tmp_path, "report_render"):
            raise RuntimeError("private-token https://private.invalid /home/private")
    result = read_run_activity(tmp_path)
    assert result["current"]["status"] == "failed"
    assert "private" not in (tmp_path / "controller-activity.json").read_text()


def test_concurrent_and_nested_controller_events_do_not_overwrite_each_other(tmp_path):
    barrier = threading.Barrier(3)

    def work(stage):
        with controller_activity(tmp_path, stage, heartbeat_seconds=0.05):
            barrier.wait(timeout=5)
            barrier.wait(timeout=5)

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(work, stage) for stage in ("sources", "report_render")]
        barrier.wait(timeout=5)
        assert {item["stage"] for item in read_run_activity(tmp_path)["active_controllers"]} == {"sources", "report_render"}
        barrier.wait(timeout=5)
        for future in futures:
            future.result(timeout=5)
    assert len(read_run_activity(tmp_path)["recent"]) == 4
    with controller_activity(tmp_path, "organize_materials"):
        with controller_activity(tmp_path, "report_render"):
            assert read_run_activity(tmp_path)["current"]["stage"] == "report_render"
        assert read_run_activity(tmp_path)["current"]["stage"] == "organize_materials"
    assert not read_run_activity(tmp_path)["active_controllers"]


def test_run_activity_merges_prior_attempts_and_controller_with_bounded_safe_fields(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    ActivityReporter(first).record("search", "completed", "private-search")
    with controller_activity(tmp_path, "sources"):
        pass
    ActivityReporter(second).record("model", "running", "private-session")
    result = read_run_activity(tmp_path, second, [first])
    assert [item["kind"] for item in result["recent"]] == ["search", "controller", "controller", "model"]
    assert result["current"]["kind"] == "model"
    assert "private" not in json.dumps(result)
    for _ in range(20):
        with controller_activity(tmp_path, "checkpoint"):
            pass
    assert len(read_run_activity(tmp_path, second, [first])["recent"]) == 30
    assert (tmp_path / "controller-activity.json").stat().st_size < 32000


def test_missing_legacy_malformed_and_outside_activity_are_not_invented(tmp_path):
    assert not read_run_activity(tmp_path)["available"]
    outside = tmp_path.parent / "outside-attempt"
    ActivityReporter(outside).record("command", "running")
    (tmp_path / "controller-activity.json").write_text('{"active": [], "recent": [{"stage": []}]}')
    result = read_run_activity(tmp_path, outside)
    assert not result["available"]
    with pytest.raises(ValueError, match="Unknown controller"):
        with controller_activity(tmp_path, "private/path"):
            pass


def test_resumed_transport_reporter_preserves_existing_bounded_projection(tmp_path):
    ActivityReporter(tmp_path).record("search", "completed", "old-id")
    ActivityReporter(tmp_path).record("model", "running", "new-id")
    from mathlottery.telemetry.activity import read_activity

    assert [item["kind"] for item in read_activity(tmp_path / "activity.json")["recent"]] == ["search", "model"]


def test_collect_sources_records_controller_completion_without_claiming_source_success(tmp_path):
    from mathlottery.config import Config
    from mathlottery.models import Citation, Problem
    from mathlottery.runtime.orchestrator import Orchestrator
    from mathlottery.storage.core import Store
    from mathlottery.verify.literature import collect_sources

    store = Store(tmp_path)
    config = Config()
    config.backend.native_network_access = False
    run = Orchestrator(store).create(config, Problem(id="activity", title="Activity", statement="Test only"))
    collect_sources(store, run, [])
    assert not read_run_activity(store.run_dir(run.id))["available"]
    collect_sources(store, run, [Citation(url="https://example.invalid/paper", role="ORIGINAL_STATEMENT",
                                        locator="Question 1", excerpt="Question 1", explanation="Original question")])
    event = read_run_activity(store.run_dir(run.id))["current"]
    assert event["stage"] == "sources" and event["status"] == "completed"
    assert run.observations[-1]["result"]["status"] == "UNAVAILABLE"


def test_stale_controller_heartbeat_does_not_claim_live_work_or_add_offline_time(tmp_path):
    event = {"kind": "controller", "stage": "formal_inspect", "status": "running",
             "time": "2020-01-01T00:00:00+00:00", "started_at": "2020-01-01T00:00:00+00:00",
             "heartbeat_at": "2020-01-01T00:00:05+00:00", "duration_seconds": 5,
             "error": "PRIVATE_PROXY", "command": "PRIVATE_TOKEN"}
    path = tmp_path / "controller-activity.json"
    path.write_text(json.dumps({"active": {"a" * 32: event}, "recent": [event]}))
    attempt = tmp_path / "new-attempt"
    ActivityReporter(attempt).record("model", "running")
    value = read_run_activity(tmp_path, attempt)
    assert value["current"]["kind"] == "model"
    assert value["active_controllers"][0]["heartbeat_stale"]
    interrupt_controller_activity(tmp_path)
    value = read_run_activity(tmp_path)
    assert not value["active_controllers"]
    assert value["current"]["status"] == "incomplete"
    assert value["current"]["duration_seconds"] == 5
    assert value["current"]["time"] == "2020-01-01T00:00:05+00:00"
    assert "PRIVATE" not in path.read_text()


def test_controller_activity_merges_between_processes(tmp_path):
    script = """
import sys, time
from pathlib import Path
from mathlottery.telemetry.activity import controller_activity
directory, stage = Path(sys.argv[1]), sys.argv[2]
with controller_activity(directory, stage, heartbeat_seconds=0.05):
    (directory / stage).touch()
    while not (directory / 'release').exists():
        time.sleep(0.01)
"""
    stages = ("sources", "formal_compile", "report_bundle")
    processes = [subprocess.Popen([sys.executable, "-c", script, str(tmp_path), stage],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.PIPE) for stage in stages]
    try:
        deadline = time.monotonic() + 10
        while not all((tmp_path / stage).exists() for stage in stages):
            assert time.monotonic() < deadline
            time.sleep(0.01)
        assert {item["stage"] for item in read_run_activity(tmp_path)["active_controllers"]} == set(stages)
        (tmp_path / "release").touch()
        for process in processes:
            assert process.wait(timeout=5) == 0
        value = read_run_activity(tmp_path)
        assert not value["active_controllers"]
        assert len(value["recent"]) == 6
        assert {item["stage"] for item in value["recent"] if item["status"] == "completed"} == set(stages)
    finally:
        for process in processes:
            if process.poll() is None:
                process.kill()
            process.wait(timeout=5)
