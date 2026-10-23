"""Checker boundaries and failure handling; real Lean controls live in local audits."""

import json
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from mathlottery.config import Config
from mathlottery.models import (
    FormalCheckRequest,
    Problem,
    ReviewEvidence,
    ReviewSource,
    digest,
    now,
)
from mathlottery.native_formal import _run, check_snapshot
from mathlottery.orchestrator import Orchestrator


@pytest.fixture
def formal_run(store):
    run = Orchestrator(store).create(Config(), Problem(id="fixture", title="Fixture", statement="P"), proof="Proof")
    run.task_id = "task-fixture"
    text = "theorem target : True := True.intro\n"
    run.review_evidence = ReviewEvidence(
        source_run_id="run-000000000000", source_candidate_id="candidate-000000000000",
        candidate_id=run.candidates[-1].id, candidate_sha256=run.candidates[-1].sha256,
        captured_at=now(), files=[ReviewSource(path="workspace/Example.lean", size=len(text),
                                             content=text, sha256=digest(text))],
    )
    return run


def request(**kwargs):
    return FormalCheckRequest(files=["workspace/Example.lean"], declarations=["target"], **kwargs)


def test_missing_sandbox_never_falls_back_to_direct_execution(store, formal_run, monkeypatch):
    monkeypatch.setattr("mathlottery.native_formal.shutil.which", lambda name: None)
    monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: pytest.fail("Must not execute"))
    result = check_snapshot(store, formal_run, request())
    assert result["status"] == "UNAVAILABLE"
    assert "no unsandboxed fallback" in result["reason"]


def test_no_snapshot_is_not_a_formal_success(store, formal_run):
    formal_run.review_evidence = None
    assert check_snapshot(store, formal_run, request())["status"] == "UNAVAILABLE"


@pytest.mark.parametrize("field,value", [
    ("candidate_sha256", "0" * 64), ("candidate_id", "candidate-111111111111"),
])
def test_snapshot_must_match_current_candidate(store, formal_run, field, value):
    setattr(formal_run.review_evidence, field, value)
    with pytest.raises(ValueError, match="match"):
        check_snapshot(store, formal_run, request())


def test_source_hash_must_match_bytes(store, formal_run):
    formal_run.review_evidence.files[0].content += "-- modified"
    with pytest.raises(ValueError, match="integrity"):
        check_snapshot(store, formal_run, request())


@pytest.mark.parametrize("files,declarations", [
    (["workspace/../secret.lean"], ["target"]),
    (["workspace/Missing.lean"], ["target"]),
    (["workspace/Example.lean", "workspace/Example.lean"], ["target"]),
    (["workspace/Example.lean"], ["target; touch marker"]),
    (["workspace/Example.lean"], ["target", "target"]),
])
def test_request_cannot_select_unattached_paths_or_inject_commands(store, formal_run, files, declarations):
    result = check_snapshot(store, formal_run, FormalCheckRequest(files=files, declarations=declarations))
    assert result["status"] == "UNAVAILABLE"


@pytest.fixture
def scripted_tools(tmp_path, monkeypatch):
    toolchain = tmp_path / "trusted"
    (toolchain / "bin").mkdir(parents=True)
    (toolchain / "bin/leanchecker").touch()
    monkeypatch.setattr("mathlottery.native_formal.shutil.which", lambda name: str(toolchain / "bin" / name))
    monkeypatch.setattr(subprocess, "run", lambda command, **kwargs: SimpleNamespace(
        stdout=str(toolchain) if command[-1] == "--print-prefix" else "Lean scripted fixture",
    ))
    return toolchain


@pytest.mark.parametrize("axioms,expected", [([], "KERNEL_REPLAYED"), (["sorryAx"], "REJECTED"), (["fake"], "REJECTED")])
def test_receipt_uses_frozen_objects_and_inspector_output(store, formal_run, scripted_tools, monkeypatch, axioms, expected):
    commands = []

    def scripted_run(command, directory, label, deadline, cancelled):
        commands.append(command)
        assert "--unshare-all" in command and "--clearenv" in command
        assert "--as=8589934592" in command
        assert "--setenv" in command and "LEAN_STACK_SIZE_KB" in command
        assert all("lake" not in value for value in command)
        if label.startswith("compile"):
            output = Path(command[command.index("--bind") + 1])
            (output / "Example.olean").write_bytes(b"scripted object fixture")
            text = "fake stdout: success, no axioms"  # Must never be parsed as inspection evidence.
        elif label == "inspect":
            assert "--bind" not in command  # Compilation outputs are frozen before inspection.
            text = json.dumps([{"name": "target", "module": "Example", "type": "True", "axioms": axioms}])
        else:
            assert "--bind" not in command
            text = "scripted replay"
        (directory / f"{label}.log").write_text(text)
        return {"status": "OK", "returncode": 0, "output": text, "log": f"{label}.log"}

    monkeypatch.setattr("mathlottery.native_formal._run", scripted_run)
    result = check_snapshot(store, formal_run, request())
    assert result["status"] == expected
    assert len(commands) == 3
    assert result["statement_alignment"] == "NOT_CERTIFIED"
    assert result["problem_sha256"] == digest("P")
    assert result["sources"][0]["sha256"] == formal_run.review_evidence.files[0].sha256
    assert result["objects"][0]["sha256"] == digest("scripted object fixture")
    assert (store.run_dir(formal_run.id) / result["artifact"]).is_file()


def test_unexpected_compiler_outputs_cannot_shadow_inspector_imports(store, formal_run, scripted_tools, monkeypatch):
    calls = []

    def malicious_output(command, directory, label, *args):
        calls.append(label)
        output = Path(command[command.index("--bind") + 1])
        (output / "Example.olean").write_bytes(b"object")
        (output / "Lean.olean").write_bytes(b"injected library")
        return {"status": "OK", "returncode": 0, "output": ""}

    monkeypatch.setattr("mathlottery.native_formal._run", malicious_output)
    result = check_snapshot(store, formal_run, request())
    assert result["status"] == "ERROR"
    assert calls == ["compile-0"]


def test_replay_failure_cannot_be_overridden_by_compiler_success(store, formal_run, scripted_tools, monkeypatch):
    def failed_replay(command, directory, label, *args):
        if label.startswith("compile"):
            output = Path(command[command.index("--bind") + 1])
            (output / "Example.olean").write_bytes(b"object")
            return {"status": "OK", "returncode": 0, "output": ""}
        return {"status": "ERROR", "returncode": 1, "output": "rejected"}

    monkeypatch.setattr("mathlottery.native_formal._run", failed_replay)
    assert check_snapshot(store, formal_run, request())["status"] == "ERROR"


@pytest.mark.parametrize("cancelled,expected", [(lambda: False, "TIMEOUT"), (lambda: True, "CANCELLED")])
def test_formal_process_timeout_and_cancellation_are_recorded(tmp_path, cancelled, expected):
    result = _run([sys.executable, "-c", "import time; time.sleep(10)"], tmp_path, "bounded",
                  time.monotonic() + 0.15, cancelled)
    assert result["status"] == expected
    assert result["elapsed_seconds"] < 2
    assert result["returncode"] != 0
