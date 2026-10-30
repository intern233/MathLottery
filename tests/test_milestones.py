import json

import pytest

from mathlottery.config import Config
from mathlottery.providers.demo import demo_problem
from mathlottery.runtime.milestones import answer_milestone, read_milestone
from mathlottery.runtime.orchestrator import Orchestrator
from mathlottery.runtime.workspace import NativeWorkspace


@pytest.fixture
def prepared(store):
    engine = Orchestrator(store)
    run = engine.create(Config(), demo_problem())
    workspace = NativeWorkspace(store, engine.candidates)
    workspace.prepare(run, Config())
    data = {"run_id": run.id, "task_id": run.task_id, "kind": "progress", "summary": "A lemma"}
    return run, workspace.path(run), data


def fenced(data):
    return "Ordinary mathematical answer\n```mathlottery\n" + json.dumps(data) + "\n```\n"


def test_invalid_submission_file_cannot_be_overridden_by_answer(prepared):
    run, workspace, data = prepared
    (workspace / "submissions" / f"{run.task_id}.json").write_text(
        json.dumps(data | {"task_id": "stale"})
    )
    with pytest.raises(ValueError, match="Stale"):
        read_milestone(run, workspace, fenced(data))


def test_answer_fallback_is_explicit_and_validates_identity(prepared):
    run, workspace, data = prepared
    assert read_milestone(run, workspace, fenced(data))["summary"] == "A lemma"
    with pytest.raises(ValueError, match="Stale"):
        read_milestone(run, workspace, fenced(data | {"run_id": "other"}))
    with pytest.raises(ValueError, match="Missing milestone"):
        read_milestone(run, workspace, json.dumps(data))
    with pytest.raises(ValueError, match="at most one"):
        answer_milestone(run, fenced(data) + fenced(data))


def test_manual_answer_without_checkpoint_remains_valid_progress(prepared):
    run, workspace, _ = prepared
    run.mode = "manual"
    assert read_milestone(run, workspace, "An unfinished argument") is None


def test_chat_milestone_size_limit_does_not_truncate_proofs(prepared):
    run, _, data = prepared
    run.mode = "chat"
    with pytest.raises(ValueError, match="exceeds 2 MB"):
        answer_milestone(run, fenced(data | {"summary": "x" * 2_000_001}))
