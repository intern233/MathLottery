"""Expert handoffs authenticate original bytes; public exports are labeled derivatives."""

import hashlib
import io
import json
import subprocess
import sys
import zipfile

import pytest
from test_organization import reviewed as reviewed
from test_organization_bilingual import bilingual as bilingual
from test_web import serving
from typer.testing import CliRunner

from mathlottery.cli import app
from mathlottery.organize import delivery as expert_delivery
from mathlottery.organize import workflow as organization
from mathlottery.organize.downloads import read_report, summary
from mathlottery.runtime.orchestrator import Orchestrator
from mathlottery.storage.core import atomic_write, json_text
from mathlottery.web.service import WebService


def test_existing_report_gets_local_handoff_without_model_or_markdown_changes(store, bilingual, monkeypatch):
    old = {language: doc.markdown_sha256 for language, doc in organization.report_documents(bilingual).items()}
    snapshot = json_text(bilingual.organization_context)
    monkeypatch.setattr(Orchestrator, "drive", lambda *a: pytest.fail("No model call for derived handoff"))
    updated = Orchestrator(store).export_organized(bilingual.id)
    assert old == {language: doc.markdown_sha256 for language, doc in organization.report_documents(updated).items()}
    assert snapshot == json_text(updated.organization_context)
    base = store.run_dir(updated.id) / "organized"
    assert (base / "handoff/START_HERE.zh.md").exists()
    assert (base / "handoff/START_HERE.en.md").exists()
    for language, boundary, before in (
        ("zh", "**交付范围：", "## 先核对命题与结论"),
        ("en", "**Delivery scope:", "## Check the statement and conclusions first"),
    ):
        entry = (base / f"handoff/START_HERE.{language}.md").read_text()
        assert entry.index(boundary) < entry.index(before)
        assert "`manifest.json`" in entry and "`handoff/files.json`" in entry
    assert "缺失附件须另行提供并说明来源" in (base / "handoff/START_HERE.zh.md").read_text()
    assert "does not establish that every referenced attachment is present" in (base / "handoff/START_HERE.en.md").read_text()
    index = json.loads((base / "handoff/index.json").read_text())
    assert index["candidates"][0]["verdict"] == "INCONCLUSIVE"
    assert index["candidates"][0]["novelty"] == "UNKNOWN"
    assert index["candidates"][0]["remaining_obligations"] == ["Prove the missing lemma"]
    assert not index["automatic_replay_available"]
    assert "No formal execution receipt" in index["reproduction_gaps"][0]
    assert summary(store, updated)["public_bundle_available"]
    result = subprocess.run([sys.executable, "handoff/check_files.py"], cwd=base, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    (base / "handoff/candidate-1.proof.md").write_text("Tampered proof")
    result = subprocess.run([sys.executable, "handoff/check_files.py"], cwd=base, capture_output=True, text=True)
    assert result.returncode != 0 and "integrity check failed" in result.stderr


def test_handoff_identifies_checked_sources_by_hash_and_exposes_unpinned_dependencies(store, reviewed):
    config, engine, source = reviewed
    lean = "theorem sample : True := True.intro\n"
    sha = hashlib.sha256(lean.encode()).hexdigest()
    atomic_write(store.run_dir(source.id) / "workspace/formal/Sample.lean", lean)
    receipt = {"status": "KERNEL_REPLAYED", "candidate_sha256": source.candidates[0].sha256,
               "sources": [{"path": "workspace/other/Sample.lean", "sha256": sha},
                           {"path": "workspace/formal/Missing.lean", "sha256": "0" * 64}],
               "declarations": [{"name": "sample", "type": "True", "axioms": []}],
               "lean_version": "Lean fixture", "steps": [{"argv": ["/lean/bin/lean", "Sample.lean"]}]}
    source.candidates[0].reviews[0].formal_receipt = receipt
    store.save(source, "fixture_receipt")
    run = engine.organize(config, source.id)
    materials = list(organization._read_files(store, run))
    handoff = expert_delivery.build(run, materials)
    index = json.loads(handoff["handoff/index.json"])
    formal = index["formal_checks"][0]
    assert formal["candidate_hash_matches"]
    assert formal["sources"][0]["captured_paths_with_same_sha256"] == [f"{source.id}/workspace/formal/Sample.lean"]
    assert not formal["sources"][1]["source_bytes_available"]
    assert formal["statement_alignment"] == "NOT_CERTIFIED"
    assert any("library revisions are not pinned" in item for item in index["reproduction_gaps"])
    assert "handwritten review" in formal["limitations"][1]


def test_capture_includes_dependency_lock_but_does_not_execute_it(store, reviewed):
    config, engine, source = reviewed
    path = store.run_dir(source.id) / "workspace/formal/lake-manifest.json"
    atomic_write(path, '{"packages": [{"name": "mathlib", "rev": "fixture-commit"}]}')
    run = engine.organize(config, source.id)
    materials = list(organization._read_files(store, run))
    index = json.loads(expert_delivery.build(run, materials)["handoff/index.json"])
    assert any(item["path"].endswith("lake-manifest.json") for item in index["dependency_files"])


@pytest.mark.parametrize("name", ["lake-manifest.snapshot.json", "mathlib-lake-manifest.snapshot.json"])
def test_handoff_links_dependency_snapshot_without_certifying_compilation_environment(store, reviewed, name):
    config, engine, source = reviewed
    content = '{"packages": [{"name": "mathlib", "rev": "recorded-snapshot-only"}]}'
    atomic_write(store.run_dir(source.id) / "workspace/formal" / name, content)
    atomic_write(store.run_dir(source.id) / "workspace/formal/unrelated.snapshot.json", "{}")
    source.candidates[0].reviews[0].formal_receipt = {
        "status": "KERNEL_REPLAYED", "candidate_sha256": source.candidates[0].sha256,
    }
    store.save(source, "snapshot_navigation_fixture")
    run = engine.organize(config, source.id)
    frozen_context = json_text(run.organization_context)
    materials = list(organization._read_files(store, run))
    handoff = expert_delivery.build(run, materials)
    index = json.loads(handoff["handoff/index.json"])
    captured_path = f"{source.id}/workspace/formal/{name}"
    assert index["dependency_files"] == [{
        "path": captured_path, "sha256": hashlib.sha256(content.encode()).hexdigest(), "kind": "snapshot",
    }]
    assert index["dependency_binding"] == "NOT_CERTIFIED" and not index["automatic_replay_available"]
    assert any("not a project lake-manifest.json" in gap for gap in index["reproduction_gaps"])
    assert index["formal_checks"][0]["status"] == "KERNEL_REPLAYED"
    for lang, label in (("zh", "依赖快照未必是编译时实际使用的锁文件"),
                        ("en", "Dependency snapshots may not be the lockfile actually used for compilation")):
        entry = handoff[f"handoff/START_HERE.{lang}.md"].decode()
        assert label in entry and f"../materials/{captured_path}" in entry
    assert json_text(run.organization_context) == frozen_context
    assert dict((item.path, data) for item, data in organization._read_files(store, run))[captured_path] == content.encode()


@pytest.mark.parametrize("candidate_hash", [None, "f" * 64])
def test_handoff_never_applies_successful_receipt_to_missing_or_different_candidate_hash(store, reviewed, candidate_hash):
    config, engine, source = reviewed
    source.candidates[0].reviews[0].formal_receipt = {
        "status": "KERNEL_REPLAYED", "candidate_sha256": candidate_hash,
        "declarations": [{"name": "unrelated_theorem", "type": "True", "axioms": []}],
    }
    store.save(source, "inapplicable_receipt_fixture")
    run = engine.organize(config, source.id)
    handoff = expert_delivery.build(run, list(organization._read_files(store, run)))
    index = json.loads(handoff["handoff/index.json"])
    receipt = index["formal_checks"][0]
    assert receipt["status"] == "INAPPLICABLE" and receipt["recorded_status"] == "KERNEL_REPLAYED"
    assert not receipt["candidate_hash_matches"]
    assert any("INAPPLICABLE" in gap for gap in index["reproduction_gaps"])
    assert "不能作为当前候选的形式验证证据" in handoff["handoff/START_HERE.zh.md"].decode()
    assert "does not verify the current candidate" in handoff["handoff/START_HERE.en.md"].decode()


def test_public_bundle_redacts_private_data_preserves_raw_and_maps_hashes(store, bilingual, tmp_path):
    private = "/home/researcher/private/path /Users/researcher/private C:\\Users\\researcher\\private "
    private += "mail@example.test 192.168.10.20 [fd00::1234] https://name:password@proxy.invalid "
    private += "sk-" + "a" * 40
    organization.accept(bilingual, {"zh": "# 报告\n" + private, "en": "# Report\n" + private})
    store.save(bilingual, "private_fixture_report")
    Orchestrator(store).export_organized(bilingual.id)
    raw = read_report(store, bilingual.id, "bundle")
    public = read_report(store, bilingual.id, "public_bundle")
    with zipfile.ZipFile(io.BytesIO(raw)) as original, zipfile.ZipFile(io.BytesIO(public)) as sanitized:
        assert "report.zh.pdf" in original.namelist()
        assert not any(name.endswith(".pdf") for name in sanitized.namelist())
        assert b"/home/researcher" in original.read("report.en.md")
        assert b"/home/researcher" not in sanitized.read("report.en.md")
        for token in [b"mail@example.test", b"192.168.10.20", b"fd00::1234", b"proxy.invalid", b"sk-" + b"a" * 40]:
            assert token not in sanitized.read("report.en.md")
        mapping = json.loads(sanitized.read("public-export.json"))
        assert mapping["original_receipts_apply_to_original_hashes_only"]
        assert any(item["path"] == "report.zh.pdf" for item in mapping["omitted"])
        report = next(item for item in mapping["files"] if item["path"] == "report.en.md")
        assert report["original_sha256"] == hashlib.sha256(original.read("report.en.md")).hexdigest()
        assert report["export_sha256"] == hashlib.sha256(sanitized.read("report.en.md")).hexdigest()
        assert report["redactions"]["home_path"] == 3 and not report["byte_identical"]
        sanitized.extractall(tmp_path / "public")
    result = subprocess.run([sys.executable, "handoff/check_files.py"], cwd=tmp_path / "public", capture_output=True)
    assert result.returncode == 0, result.stderr
    # The separate raw evidence and immutable report are untouched.
    assert read_report(store, bilingual.id, "bundle") == raw


def test_public_json_is_valid_private_fields_removed_clean_lean_stays_exact():
    source = {
        "materials/receipt.json": json_text({"refresh_token": "sensitive", "email": "someone@example.test",
            "candidate_sha256": "a" * 64, "plan_type": "pro", "proof": "x + x = 2 * x"}).encode(),
        "materials/Good.lean": b"theorem sample : True := True.intro\n",
        "materials/auth.json": b'{"unknown": "secret"}',
        "materials/blob.md": b"\0binary",
        "materials/invalid.json": b"not json",
    }
    exported = expert_delivery.public_files(source)
    receipt = json.loads(exported["materials/receipt.json"])
    assert receipt["refresh_token"] == receipt["plan_type"] == "REDACTED_PRIVATE_FIELD"
    assert receipt["email"] == "REDACTED_EMAIL"
    assert receipt["candidate_sha256"] == "a" * 64
    assert receipt["proof"] == "x + x = 2 * x"
    assert exported["materials/Good.lean"] == source["materials/Good.lean"]
    assert "materials/auth.json" not in exported
    assert "materials/blob.md" not in exported and "materials/invalid.json" not in exported


def test_public_bundle_rejects_modified_frozen_materials(store, bilingual):
    item = bilingual.organization_context.files[0]
    (store.run_dir(bilingual.id) / "organization-context" / item.path).write_text("tampered")
    with pytest.raises(ValueError, match="modified|limit"):
        read_report(store, bilingual.id, "public_bundle")


def test_public_sanitized_key_collisions_are_blocked():
    value = json.dumps({"one@example.test": 1, "two@example.test": 2}).encode()
    with pytest.raises(ValueError, match="colliding sanitized JSON keys"):
        expert_delivery.public_files({"materials/keys.json": value})


def test_public_http_download_and_local_handoff_refresh_need_no_account_or_model(store, bilingual, monkeypatch):
    monkeypatch.setattr(Orchestrator, "drive", lambda *a: pytest.fail("Export must not call a model"))
    before = {lang: doc.markdown_sha256 for lang, doc in organization.report_documents(bilingual).items()}
    index = store.run_dir(bilingual.id) / "organized/handoff/index.json"
    index.unlink()  # Simulate a completed report exported before handoffs existed.
    service = WebService(store.root)
    with serving(service, account_status={"available": False, "authenticated": False}) as (client, _):
        endpoint = f"/api/runs/{bilingual.id}/organized"
        detail = client.get(f"/api/runs/{bilingual.id}").json()
        assert not detail["organized_report"]["handoff_available"]
        assert detail["organized_report"]["public_bundle_available"]
        response = client.get(endpoint + "?format=public_bundle")
        assert response.status_code == 200 and response.headers["content-type"] == "application/zip"
        assert "-public-text.zip" in response.headers["content-disposition"]
        with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
            assert {"public-export.json", "handoff/START_HERE.zh.md", "handoff/START_HERE.en.md"} <= set(archive.namelist())
            assert not any(path.endswith(".pdf") for path in archive.namelist())
        for query in ("format=public_bundle&language=zh", "format=public_bundle&language=",
                      "format=public_bundle&language=fr", "format=public_bundle&language=en&language=zh",
                      "format=public_bundle&format=bundle", "format=public_bundle&path=auth.json"):
            invalid = client.get(endpoint + "?" + query)
            assert invalid.status_code == 400
            assert isinstance(invalid.json()["error"], str) and invalid.json()["error"]
        # Same local POST action used by the frontend refresh button retains CSRF protection.
        assert client.post(endpoint, json={}).status_code == 403
        client.headers["X-MathLottery-Token"] = client.get("/api/bootstrap").json()["csrf_token"]
        refreshed = client.post(endpoint, json={})
        assert refreshed.status_code == 200 and refreshed.json()["handoff_available"]
        assert client.post(endpoint, json={"model": "unexpected"}).status_code == 400
    after = store.load(bilingual.id)
    assert before == {lang: doc.markdown_sha256 for lang, doc in organization.report_documents(after).items()}


def test_public_cli_requires_new_output_rejects_language_and_never_overwrites(store, bilingual, tmp_path, monkeypatch):
    monkeypatch.setattr(Orchestrator, "drive", lambda *a: pytest.fail("Export must not call a model"))
    runner = CliRunner()
    arguments = ["--root", str(store.root), "export", bilingual.id, "--format", "public_bundle"]
    missing = runner.invoke(app, arguments)
    assert missing.exit_code != 0 and "requires --output" in missing.output
    destination = tmp_path / "public.zip"
    invalid = runner.invoke(app, [*arguments, "--language", "en", "--output", str(destination)])
    assert invalid.exit_code != 0 and "only to organized Markdown/PDF" in invalid.output
    assert not destination.exists()
    exported = runner.invoke(app, [*arguments, "--output", str(destination)])
    assert exported.exit_code == 0, exported.output
    original = destination.read_bytes()
    with zipfile.ZipFile(io.BytesIO(original)) as archive:
        assert "public-export.json" in archive.namelist() and "report.en.md" in archive.namelist()
    repeated = runner.invoke(app, [*arguments, "--output", str(destination)])
    assert repeated.exit_code != 0 and destination.read_bytes() == original
