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
from mathlottery.native_formal import _output_budget_error, _run, check_snapshot
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


@pytest.mark.parametrize("root", ["/proof", "../proof", "proof/..", "proof//src", "proof\\src", "."])
def test_module_root_cannot_escape_or_change_path_interpretation(store, formal_run, root, monkeypatch):
    monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: pytest.fail("Must not execute"))
    result = check_snapshot(store, formal_run, request(module_root=root))
    assert result["status"] == "UNAVAILABLE"
    assert "Module root" in result["reason"]


def test_module_root_requires_every_requested_file_inside_it(store, formal_run):
    result = check_snapshot(store, formal_run, request(module_root="proof"))
    assert result["status"] == "UNAVAILABLE"
    assert "inside the selected module root" in result["reason"]


def test_module_root_does_not_grant_access_to_unattached_sources(store, formal_run):
    formal_run.review_evidence.files[0].path = "workspace/proof/Example.lean"
    result = check_snapshot(store, formal_run, FormalCheckRequest(
        files=["workspace/proof/Missing.lean"], declarations=["target"], module_root="proof",
    ))
    assert result["status"] == "UNAVAILABLE"
    assert "attached Lean files" in result["reason"]


@pytest.mark.parametrize("module", ["Init", "Lean", "Std", "Mathlib", "Mathlib/Injected", "MathLotteryInspector"])
def test_module_root_cannot_hide_trusted_module_shadowing(store, formal_run, module):
    path = f"workspace/proof/{module}.lean"
    formal_run.review_evidence.files[0].path = path
    result = check_snapshot(store, formal_run, FormalCheckRequest(
        files=[path], declarations=["target"], module_root="proof",
    ))
    assert result["status"] == "UNAVAILABLE"
    assert "shadow a trusted library or inspector" in result["reason"]


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


def test_explicit_module_root_preserves_bytes_and_module_dependencies(store, formal_run, scripted_tools, monkeypatch):
    contents = {
        "Lib/Lemmas.lean": "namespace Lemmas\ntheorem helper : True := True.intro\nend Lemmas\n",
        "Main.lean": "import Lib.Lemmas\nnamespace Main\ntheorem target : True := Lemmas.helper\nend Main\n",
    }
    formal_run.review_evidence.files = [
        ReviewSource(path="workspace/proof/" + path, size=len(text.encode()), content=text, sha256=digest(text))
        for path, text in contents.items()
    ]
    calls = []

    def scripted_run(command, directory, label, *args):
        calls.append(label)
        assert "--unshare-all" in command
        inputs = Path(command[command.index("/src") - 1])
        assert not (inputs / "proof").exists()
        for path, text in contents.items():
            assert (inputs / path).read_bytes() == text.encode()
        if label.startswith("compile"):
            relative = command[-1]
            assert relative in contents
            output = Path(command[command.index("--bind") + 1])
            (output / relative.removesuffix(".lean")).with_suffix(".olean").write_bytes(b"fixture")
            text = ""
        elif label == "inspect":
            assert "Lib.Lemmas" in command and "Main" in command
            text = json.dumps([{"name": "Main.target", "module": "Main", "type": "True", "axioms": []}])
        else:
            assert command[-1] in {"Lib.Lemmas", "Main"}
            text = ""
        return {"status": "OK", "returncode": 0, "output": text}

    monkeypatch.setattr("mathlottery.native_formal._run", scripted_run)
    result = check_snapshot(store, formal_run, FormalCheckRequest(
        files=[item.path for item in formal_run.review_evidence.files],
        declarations=["Main.target"], module_root="proof",
    ))
    assert result["status"] == "KERNEL_REPLAYED"
    assert calls == ["compile-0", "compile-1", "replay-0", "replay-1", "inspect"]
    assert result["request"]["module_root"] == "proof"
    assert [source["module"] for source in result["sources"]] == ["Lib.Lemmas", "Main"]
    assert [source["path"] for source in result["sources"]] == [source.path for source in formal_run.review_evidence.files]
    assert [source["sha256"] for source in result["sources"]] == [digest(text) for text in contents.values()]


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


@pytest.mark.parametrize("kind", ["single", "total"])
def test_oversized_objects_interrupt_compilation_before_replay(store, formal_run, scripted_tools, monkeypatch, kind):
    limits = formal_run.config["verification"]
    limits["formal_max_object_mb"] = 1 if kind == "single" else 2
    limits["formal_max_total_object_mb"] = 4 if kind == "single" else 1
    calls = []

    def oversized_output(command, directory, label, deadline, interrupted):
        calls.append(label)
        assert label == "compile-0"
        output = Path(command[command.index("--bind") + 1])
        size = 1_048_577 if kind == "single" else 786_432
        with (output / "Example.olean").open("wb") as stream:
            stream.truncate(size)
        if kind == "total":
            with (output / "temporary.bin").open("wb") as stream:
                stream.truncate(size)
        assert interrupted(), "Output limits must be checked while the compiler is running"
        return {"status": "CANCELLED", "returncode": -9, "output": ""}

    monkeypatch.setattr("mathlottery.native_formal._run", oversized_output)
    result = check_snapshot(store, formal_run, request())
    assert calls == ["compile-0"]
    assert result["status"] == "OUTPUT_LIMIT"
    assert "total size limit" in result["reason"] if kind == "total" else "object exceeds" in result["reason"]
    assert result["steps"][0]["status"] == "OUTPUT_LIMIT"


def test_configured_large_objects_are_hashed_and_replayed(store, formal_run, scripted_tools, monkeypatch):
    formal_run.config["verification"].update(formal_max_object_mb=20, formal_max_total_object_mb=20)
    size = 17 * 1024 * 1024
    calls = []

    def large_output(command, directory, label, deadline, interrupted):
        calls.append(label)
        assert "--fsize=20971520" in command
        if label.startswith("compile"):
            output = Path(command[command.index("--bind") + 1])
            with (output / "Example.olean").open("wb") as stream:
                stream.truncate(size)
            assert not interrupted()
        text = json.dumps([{"name": "target", "module": "Example", "type": "True", "axioms": []}]) if label == "inspect" else ""
        return {"status": "OK", "returncode": 0, "output": text}

    monkeypatch.setattr("mathlottery.native_formal._run", large_output)
    result = check_snapshot(store, formal_run, request())
    assert result["status"] == "KERNEL_REPLAYED"
    assert calls == ["compile-0", "replay-0", "inspect"]
    assert result["limits"]["max_object_mb"] == 20
    assert result["objects"][0]["size"] == size
    assert len(result["objects"][0]["sha256"]) == 64


def test_long_formal_timeout_still_shares_remaining_run_budget(store, formal_run, scripted_tools, monkeypatch):
    formal_run.config["verification"]["formal_timeout_seconds"] = 1800
    formal_run.config["budget"]["max_wall_time_minutes"] = 0.1
    calls = []

    def bounded_check(command, directory, label, deadline, interrupted):
        calls.append(label)
        assert 0 < deadline - time.monotonic() <= 6
        if label.startswith("compile"):
            output = Path(command[command.index("--bind") + 1])
            (output / "Example.olean").write_bytes(b"fixture")
        text = json.dumps([{"name": "target", "module": "Example", "type": "True", "axioms": []}]) if label == "inspect" else ""
        return {"status": "OK", "returncode": 0, "output": text}

    monkeypatch.setattr("mathlottery.native_formal._run", bounded_check)
    result = check_snapshot(store, formal_run, request())
    assert result["status"] == "KERNEL_REPLAYED"
    assert result["limits"]["seconds"] == 1800
    assert calls == ["compile-0", "replay-0", "inspect"]


@pytest.mark.parametrize("kind", ["symlink", "hardlink", "entry_count"])
def test_output_monitor_bounds_links_and_directory_entries(tmp_path, kind):
    output = tmp_path / "output"
    output.mkdir()
    original = tmp_path / "outside"
    original.write_bytes(b"outside")
    if kind == "symlink":
        (output / "object").symlink_to(original)
    elif kind == "hardlink":
        (output / "object").hardlink_to(original)
    else:
        for number in range(257):
            (output / f"file-{number}").touch()
    failure = _output_budget_error(output, 1024, 1024)
    assert failure is not None
    assert failure[0] == ("OUTPUT_LIMIT" if kind == "entry_count" else "ERROR")
    assert original.read_bytes() == b"outside"


@pytest.mark.parametrize("cancelled,expected", [(lambda: False, "TIMEOUT"), (lambda: True, "CANCELLED")])
def test_formal_process_timeout_and_cancellation_are_recorded(tmp_path, cancelled, expected):
    result = _run([sys.executable, "-c", "import time; time.sleep(10)"], tmp_path, "bounded",
                  time.monotonic() + 0.15, cancelled)
    assert result["status"] == expected
    assert result["elapsed_seconds"] < 2
    assert result["returncode"] != 0
