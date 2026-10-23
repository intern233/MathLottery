"""Lean artifact visibility does not imply formal verification."""

import pytest
from test_web import serving

from mathlottery.config import Config
from mathlottery.models import Problem, Workflow
from mathlottery.orchestrator import Orchestrator
from mathlottery.web.artifacts import MAX_SOURCE_BYTES, list_formal_artifacts, read_formal_artifact
from mathlottery.web.service import WebService


def write(root, relative, content="example : 1 = 1 := rfl\n"):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def test_lists_only_sources_and_project_files(tmp_path):
    write(tmp_path, "workspace/formal/Proof.lean")
    write(tmp_path, "workspace/formal/lean-toolchain", "leanprover/lean4:v4.35.0\n")
    write(tmp_path, "workspace/formal/lakefile.toml", 'name = "proof"\n')
    write(tmp_path, "review-workspaces/candidate-example/Check.lean")
    for excluded in ("workspace/.lake/packages/mathlib/Mathlib/Foo.lean", "workspace/build/Foo.lean", "workspace/.hidden.lean", "workspace/auth.json", "workspace/Proof.olean", "outside.lean"):
        write(tmp_path, excluded)
    result = list_formal_artifacts(tmp_path)
    assert [item["path"] for item in result["items"]] == [
        "review-workspaces/candidate-example/Check.lean", "workspace/formal/Proof.lean",
        "workspace/formal/lakefile.toml", "workspace/formal/lean-toolchain",
    ]
    assert all(item["downloadable"] for item in result["items"])
    assert not result["truncated"]


def test_lists_and_reads_small_proof_materials_but_not_general_workspace_files(tmp_path):
    permitted = [
        "workspace/proof/Proof.md", "workspace/formal/check.py",
        "workspace/proof/certificates.json", "workspace/proof/data/table.csv",
        "workspace/proof/notes.txt",
        "review-workspaces/candidate-example/submitted-evidence/proof/Proof.md",
    ]
    excluded = [
        "workspace/notes.md", "workspace/auth.json", "workspace/research/history.json",
        "workspace/proof/.env", "workspace/proof/Proof.olean",
        "workspace/proof/.lake/manifest.json", "workspace/proof/build/table.json",
    ]
    for relative in permitted + excluded:
        write(tmp_path, relative, "small proof material\n")
    result = list_formal_artifacts(tmp_path)
    assert [item["path"] for item in result["items"]] == sorted(permitted)
    for relative in permitted:
        assert read_formal_artifact(tmp_path, relative) == b"small proof material\n"
    for relative in excluded:
        with pytest.raises(ValueError):
            read_formal_artifact(tmp_path, relative)


@pytest.mark.parametrize("variant", ["binary", "large", "symlink", "hardlink"])
def test_proof_materials_keep_download_guards(tmp_path, variant):
    path = write(tmp_path, "workspace/proof/certificate.json", "{}")
    if variant == "binary":
        path.write_bytes(b"\0not text")
    elif variant == "large":
        path.write_text("x" * (MAX_SOURCE_BYTES + 1))
    else:
        other = write(tmp_path, "private/certificate.json", "must not be exposed")
        path.unlink()
        if variant == "symlink":
            path.symlink_to(other)
        else:
            path.hardlink_to(other)
    with pytest.raises(ValueError):
        read_formal_artifact(tmp_path, "workspace/proof/certificate.json")


@pytest.mark.parametrize("relative", ["../outside.lean", "/tmp/outside.lean", "workspace/../outside.lean", "workspace/.lake/Dep.lean", "workspace//Proof.lean", "workspace/./Proof.lean", "workspace\\Proof.lean", "workspace/auth.json", "workspace/build/Proof.lean"])
def test_rejects_unapproved_paths(tmp_path, relative):
    with pytest.raises(ValueError):
        read_formal_artifact(tmp_path, relative)


def test_linked_sources_and_directories_are_neither_listed_nor_read(tmp_path):
    root = tmp_path / "run"
    outside = write(tmp_path, "outside/Proof.lean")
    (root / "workspace").mkdir(parents=True)
    (root / "workspace/Symlink.lean").symlink_to(outside)
    (root / "workspace/Hardlink.lean").hardlink_to(outside)
    (root / "workspace/linked").symlink_to(outside.parent, target_is_directory=True)
    assert list_formal_artifacts(root)["items"] == []
    for relative in ("workspace/Symlink.lean", "workspace/Hardlink.lean", "workspace/linked/Proof.lean"):
        with pytest.raises(ValueError):
            read_formal_artifact(root, relative)


def test_list_and_reads_are_bounded(tmp_path, monkeypatch):
    from mathlottery.web import artifacts

    write(tmp_path, "workspace/Large.lean", "x" * (MAX_SOURCE_BYTES + 1))
    assert list_formal_artifacts(tmp_path)["items"][0]["downloadable"] is False
    with pytest.raises(ValueError, match="1 MB"):
        read_formal_artifact(tmp_path, "workspace/Large.lean")
    write(tmp_path, "workspace/Small.lean")
    monkeypatch.setattr(artifacts, "MAX_FILES", 1)
    result = list_formal_artifacts(tmp_path)
    assert len(result["items"]) == 1 and result["truncated"]
    monkeypatch.setattr(artifacts, "MAX_ENTRIES", 0)
    assert list_formal_artifacts(tmp_path) == {"items": [], "truncated": True}


def test_binary_source_rejected(tmp_path):
    write(tmp_path, "workspace/Binary.lean", "\0secret")
    with pytest.raises(ValueError, match="text"):
        read_formal_artifact(tmp_path, "workspace/Binary.lean")


def test_http_sources_are_downloadable_but_not_verification_evidence(tmp_path):
    service = WebService(tmp_path)
    run = Orchestrator(service.store).create(Config(), Problem(id="sample", title="Example", statement="1 = 1"), workflow=Workflow.SOLVE)
    folder = service.store.run_dir(run.id)
    source = write(folder, "workspace/formal/Proof.lean")
    with serving(service) as (client, _):
        response = client.get(f"/api/runs/{run.id}")
        data = response.json()
        assert data["candidates"] == []
        assert data["formal_artifacts"]["items"][0]["path"] == "workspace/formal/Proof.lean"
        response = client.get(f"/api/runs/{run.id}/artifact", params={"path": "workspace/formal/Proof.lean"})
        assert response.status_code == 200
        assert response.text == source.read_text()
        assert response.headers["content-type"].startswith("text/plain")
        assert "attachment" in response.headers["content-disposition"]
        assert "filename*=UTF-8''Proof.lean" in response.headers["content-disposition"]
        write(folder, 'workspace/证明"\r\nX-Bad: yes.lean')
        response = client.get(f"/api/runs/{run.id}/artifact", params={"path": 'workspace/证明"\r\nX-Bad: yes.lean'})
        assert response.status_code == 200
        assert "x-bad" not in response.headers
        assert "%0D%0A" in response.headers["content-disposition"]
        for invalid in ("../config.yaml", "workspace/../../.mathlottery/codex-home/auth.json", "report.md", str(source)):
            response = client.get(f"/api/runs/{run.id}/artifact", params={"path": invalid})
            assert response.status_code == 400
        assert client.get(f"/api/runs/{run.id}/artifact").status_code == 400
        assert client.get(f"/api/runs/{run.id}/artifact?path=a&path=b").status_code == 400
        assert service.store.load(run.id).candidates == []


def test_linked_workspace_root_is_rejected(tmp_path):
    root = tmp_path / "run"
    root.mkdir()
    source = write(tmp_path, "personal/Proof.lean")
    (root / "workspace").symlink_to(source.parent, target_is_directory=True)
    assert list_formal_artifacts(root)["items"] == []
    with pytest.raises(ValueError):
        read_formal_artifact(root, "workspace/Proof.lean")


def test_parent_symlink_swapped_after_validation_is_rejected(tmp_path, monkeypatch):
    from mathlottery.web import artifacts

    root = tmp_path / "run"
    write(root, "workspace/formal/Proof.lean")
    write(tmp_path, "personal/Proof.lean", "must not be served")
    original = artifacts._source_path

    def swapped(root, relative):
        result = original(root, relative)
        (root / "workspace/formal").rename(root / "workspace/old-formal")
        (root / "workspace/formal").symlink_to(tmp_path / "personal", target_is_directory=True)
        return result

    monkeypatch.setattr(artifacts, "_source_path", swapped)
    with pytest.raises(OSError):
        read_formal_artifact(root, "workspace/formal/Proof.lean")
