import json
import time

import pytest

from mathlottery.activity import ActivityReporter, controller_activity, read_activity
from mathlottery.telemetry_archive import append_public_record, export_activity_archive


def records(data):
    return [json.loads(line) for line in data.splitlines()]


def test_all_visible_events_are_archived_after_projection_rollover(tmp_path):
    attempt = tmp_path / "attempt"
    reporter = ActivityReporter(attempt)
    reporter.record("command", "running", "PRIVATE_COMMAND")
    archive = attempt / "activity-events.jsonl"
    prefix = archive.read_bytes()
    for index in range(80):
        reporter.record("command", "completed", f"PRIVATE-{index}")
    assert len(read_activity(attempt / "activity.json")["recent"]) == 30
    assert archive.read_bytes().startswith(prefix)
    exported = export_activity_archive(tmp_path, [attempt])
    assert len([item for item in records(exported) if item["record_type"] == "activity"]) == 81
    assert b"PRIVATE" not in archive.read_bytes()
    assert b"PRIVATE" not in exported


def test_controller_archive_has_all_start_finish_events_without_heartbeat_flood(tmp_path):
    with controller_activity(tmp_path, "formal_replay", heartbeat_seconds=0.05):
        time.sleep(0.16)
    for _ in range(20):
        with controller_activity(tmp_path, "sources"):
            pass
    items = records(export_activity_archive(tmp_path))
    events = [item for item in items if item["record_type"] == "activity"]
    assert len(events) == 42
    assert [item["status"] for item in events[:2]] == ["running", "completed"]
    assert events[1]["duration_seconds"] >= 0.15
    assert items[0]["heartbeats_archived"] is False


def test_export_includes_more_than_twenty_attempts_without_persistent_paths(tmp_path):
    attempts = []
    for index in range(24):
        attempt = tmp_path / f"private-attempt-{index}"
        attempts.append(attempt)
        ActivityReporter(attempt).record("search", "completed")
    result = export_activity_archive(tmp_path, attempts)
    items = records(result)
    assert len([item for item in items if item["record_type"] == "activity"]) == 24
    assert len([item for item in items[0]["streams"] if item["scope"] == "agent"]) == 24
    assert b"private-attempt" not in result
    assert str(tmp_path).encode() not in result


def test_legacy_projection_is_not_backfilled_or_claimed_complete(tmp_path):
    old = tmp_path / "old"
    old.mkdir()
    (old / "activity.json").write_text(json.dumps({"recent": [{"kind": "model", "status": "completed", "time": "2020-01-01T00:00:00+00:00"}]}))
    before = records(export_activity_archive(tmp_path, [old]))
    assert before[0]["legacy_history_reconstructed"] is False
    assert not next(item for item in before[0]["streams"] if item["scope"] == "agent")["available"]
    ActivityReporter(old).record("search", "running")
    after = records(export_activity_archive(tmp_path, [old]))
    header = next(item for item in after if item["record_type"] == "archive_start")
    assert header["earlier_history"] == "unavailable"
    assert len([item for item in after if item["record_type"] == "activity"]) == 1


def test_legacy_root_attempt_is_explicitly_unavailable_without_rejecting_download(tmp_path):
    (tmp_path / "old-answer.md").write_text("Legacy answer, not an activity archive.")
    values = records(export_activity_archive(tmp_path, [tmp_path]))
    agent = next(item for item in values[0]["streams"] if item["scope"] == "agent")
    assert not agent["available"]
    assert values[0]["legacy_history_reconstructed"] is False


def test_export_resanitizes_injected_fields_and_reports_corrupt_records(tmp_path):
    attempt = tmp_path / "attempt"
    ActivityReporter(attempt).record("message", "completed")
    path = attempt / "activity-events.jsonl"
    with path.open("a") as target:
        target.write(json.dumps({"kind": "command", "status": "completed", "time": "2020-01-01T00:00:00+00:00",
                                 "command": "PRIVATE_SECRET", "proxy": "PRIVATE_IP"}) + "\n")
        target.write('{"kind":"command","token":"PRIVATE_TORN"')
    prefix = path.read_bytes()
    ActivityReporter(attempt).record("model", "running")
    assert path.read_bytes().startswith(prefix)
    result = export_activity_archive(tmp_path, [attempt])
    assert b"PRIVATE" not in result
    items = records(result)
    assert items[0]["invalid_records_omitted"] == 1
    assert len([item for item in items if item["record_type"] == "activity"]) == 3


def test_archive_export_enforces_explicit_limit_instead_of_returning_partial_history(tmp_path):
    attempt = tmp_path / "attempt"
    ActivityReporter(attempt).record("model", "running")
    with pytest.raises(ValueError, match="size limit"):
        export_activity_archive(tmp_path, [attempt], max_bytes=10)
    with pytest.raises(ValueError, match="64 MiB"):
        export_activity_archive(tmp_path, [attempt], max_bytes=65 * 1024 * 1024)
    assert records(export_activity_archive(tmp_path, [attempt]))[0]["coverage"] == "recorded_valid_events_only"


def test_export_rejects_external_attempts_and_symlinked_archive(tmp_path):
    outside = tmp_path.parent / "outside-activity"
    outside.mkdir(exist_ok=True)
    ActivityReporter(outside).record("command", "running")
    with pytest.raises(ValueError, match="belong to this run"):
        export_activity_archive(tmp_path, [outside])
    (tmp_path / "controller-activity-events.jsonl").symlink_to(outside / "activity-events.jsonl")
    with pytest.raises(ValueError, match="Unsafe"):
        export_activity_archive(tmp_path)


def test_terminal_attempt_append_is_idempotent_and_keeps_previous_bytes(tmp_path):
    path = tmp_path / "resource-attempts.jsonl"
    one = {"record_type": "resource_attempt", "attempt": {"number": 1, "state": "released"}}
    append_public_record(path, one, attempt_number=1)
    before = path.read_bytes()
    append_public_record(path, one, attempt_number=1)
    assert path.read_bytes() == before
    append_public_record(path, {"record_type": "resource_attempt", "attempt": {"number": 2, "state": "interrupted"}}, attempt_number=2)
    assert path.read_bytes().startswith(before)
    items = records(export_activity_archive(tmp_path))
    assert [item["attempt"]["number"] for item in items if item["record_type"] == "resource_attempt"] == [1, 2]
