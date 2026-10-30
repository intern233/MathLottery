import json

import pytest

from mathlottery.providers.metadata import clean_usage, session_path, session_runtime, turn_usage

BEFORE = {"input_tokens": 1000, "output_tokens": 100, "cached_input_tokens": 800}
AFTER = {"input_tokens": 1500, "output_tokens": 130, "cached_input_tokens": 1200}
DELTA = {"input_tokens": 500, "output_tokens": 30, "cached_input_tokens": 400}


def test_cumulative_and_per_turn_cli_counters_are_reconciled():
    assert turn_usage(AFTER, BEFORE, AFTER, resumed=True) == (DELTA, "session_cumulative_delta")
    assert turn_usage(DELTA, BEFORE, AFTER, resumed=True) == (DELTA, "per_turn_confirmed")
    assert turn_usage(BEFORE, None, BEFORE, resumed=False) == (BEFORE, "first_session_turn")


@pytest.mark.parametrize(
    "reported,before,after",
    [
        ({}, BEFORE, AFTER),
        (AFTER, None, AFTER),
        (AFTER, BEFORE, None),
        (BEFORE, AFTER, BEFORE),
        (AFTER | {"output_tokens": 999}, BEFORE, AFTER),
    ],
)
def test_missing_or_inconsistent_counters_remain_unknown(reported, before, after):
    usage, _ = turn_usage(reported, before, after, resumed=True)
    assert usage == {}


def test_usage_metadata_only_contains_nonnegative_integer_counters():
    assert clean_usage(
        {
            "input_tokens": True,
            "output_tokens": -3,
            "cached_input_tokens": 5,
            "private": "Do not copy",
            "other_counter": 4,
        }
    ) == {"cached_input_tokens": 5}


def test_metadata_default_ignores_local_codex_and_explicit_home_is_confined(tmp_path, monkeypatch):
    session = "11111111-1111-4111-8111-111111111111"
    local = tmp_path / "local-codex"
    (local / "sessions").mkdir(parents=True)
    record = local / "sessions" / f"rollout-{session}.jsonl"
    record.write_text(json.dumps({"type": "turn_context", "payload": {"model": "local-only"}}))
    monkeypatch.setenv("CODEX_HOME", str(local))
    monkeypatch.chdir(tmp_path)
    assert session_runtime(session) == {}
    private_parent = tmp_path / ".mathlottery"
    private_parent.mkdir()
    (private_parent / "codex-home").symlink_to(local, target_is_directory=True)
    assert session_runtime(session) == {}
    isolated = tmp_path / "isolated-codex"
    isolated.mkdir()
    (isolated / "sessions").symlink_to(local / "sessions", target_is_directory=True)
    assert session_path(session, isolated) is None
    assert session_runtime(session, isolated) == {}
