"""Independent integration checks for portable, evidence-bound expert reports."""

import io
import json
import zipfile

import pytest
from test_organization import reviewed as reviewed

from mathlottery.models import Phase, State
from mathlottery.organize import workflow as organization
from mathlottery.organize.downloads import read_report
from mathlottery.storage.core import atomic_write, json_text


@pytest.fixture
def arranged(store, reviewed):
    config, engine, source = reviewed
    root = store.run_dir(source.id)
    atomic_write(root / "workspace/proof/Main.lean", "-- Frozen proof source\n")
    atomic_write(root / "workspace/proof/.env", "PRIVATE_CREDENTIAL_SENTINEL")
    source.config["private"] = "PRIVATE_CONFIG_SENTINEL"
    source.environment["private"] = "PRIVATE_ENVIRONMENT_SENTINEL"
    store.save(source, "fixture_private_config")
    run = engine.organize(config, source.id, language="en")
    # Preserve coverage for historical reports saved before bilingual output existed.
    run.organization_context.report_languages = None
    organization.accept(run, "# Exposition\n\nThe missing lemma remains open.")
    run.state, run.phase = State.COMPLETED, Phase.REPORT
    run.organization_report.pdf_status = "failed"
    run.organization_report.pdf_error = "Optional renderer is unavailable"
    store.save(run, "fixture_report")
    return run


def test_bundle_contains_complete_manifest_bound_materials_without_private_state(store, arranged):
    # Unlisted or mutated projections must never be silently used as evidence.
    root = store.run_dir(arranged.id)
    atomic_write(root / "organized/manifest.json", '{"private": "PRIVATE_MANIFEST_SENTINEL"}')
    atomic_write(root / "organized/materials/secret.txt", "PRIVATE_EXTRA_SENTINEL")
    material = arranged.organization_context.files[0]
    atomic_write(root / "organized/materials" / material.path, "Changed projection")
    before = json_text(store.load(arranged.id))
    payload = read_report(store, arranged.id, "bundle")
    with zipfile.ZipFile(io.BytesIO(payload)) as bundle:
        names = set(bundle.namelist())
        expected = {"report.md", "manifest.json",
                    "handoff/START_HERE.zh.md", "handoff/START_HERE.en.md",
                    "handoff/index.json", "handoff/check_files.py", "handoff/files.json",
                    "handoff/candidate-1.proof.md", "handoff/candidate-1.review.json"} | {
            "materials/" + item.path for item in arranged.organization_context.files
        }
        assert names == expected
        handoff_files = json.loads(bundle.read("handoff/files.json"))["files"]
        assert {item["path"] for item in handoff_files} == expected - {"handoff/files.json"}
        manifest = json.loads(bundle.read("manifest.json"))
        assert manifest["report"]["pdf"] is None
        assert manifest["materials_prefix"] == "materials/"
        assert manifest["candidate_hashes"] == arranged.organization_context.candidate_hashes
        assert "INCONCLUSIVE" in bundle.read("report.md").decode()
        full = b"\n".join(bundle.read(name) for name in names)
        assert b"PRIVATE_" not in full
        assert b"Frozen proof source" in full
        assert b"Changed projection" not in full
        for item in arranged.organization_context.files:
            assert len(bundle.read("materials/" + item.path)) == item.size
    assert json_text(store.load(arranged.id)) == before  # No model, database or source changes.


def test_bundle_includes_the_verified_pdf_when_available(store, arranged):
    import hashlib

    content = b"%PDF-1.4\nfixture-bytes"
    root = store.run_dir(arranged.id)
    root.joinpath("organized").mkdir(exist_ok=True)
    root.joinpath("organized/report.pdf").write_bytes(content)
    arranged.organization_report.pdf_status = "ready"
    arranged.organization_report.pdf_details = {"sha256": hashlib.sha256(content).hexdigest()}
    store.save(arranged, "fixture_pdf")
    with zipfile.ZipFile(io.BytesIO(read_report(store, arranged.id, "bundle"))) as bundle:
        assert bundle.read("report.pdf") == content
        assert json.loads(bundle.read("manifest.json"))["report"]["pdf"] == "report.pdf"


@pytest.mark.parametrize("tamper", ["material", "candidate", "pdf"])
def test_bundle_rejects_modified_frozen_evidence_and_report_bytes(store, arranged, tamper):
    if tamper == "material":
        item = arranged.organization_context.files[0]
        target = store.run_dir(arranged.id) / "organization-context" / item.path
        target.write_bytes(b"Changed dossier")
    elif tamper == "candidate":
        arranged.candidates[0].reviews[0].verdict = "NO_ISSUES_FOUND"
        store.save(arranged, "fixture_tampering")
    else:
        root = store.run_dir(arranged.id)
        atomic_write(root / "organized/report.pdf", "%PDF-1.4\nchanged")
        arranged.organization_report.pdf_status = "ready"
        arranged.organization_report.pdf_details = {"sha256": "0" * 64}
        store.save(arranged, "fixture_tampering")
    with pytest.raises(ValueError, match="modified|integrity"):
        read_report(store, arranged.id, "bundle")


def test_bundle_rejects_linked_materials_and_count_overflow(store, arranged, tmp_path):
    item = arranged.organization_context.files[0]
    target = store.run_dir(arranged.id) / "organization-context" / item.path
    target.unlink()
    outside = tmp_path / "private-source.txt"
    outside.write_text("PRIVATE_SENTINEL")
    target.symlink_to(outside)
    with pytest.raises((ValueError, OSError)):
        read_report(store, arranged.id, "bundle")
    arranged.organization_context.files = [item] * (organization.MAX_FILES + 1)
    store.save(arranged, "fixture_bad_manifest")
    with pytest.raises(ValueError, match="file count or size"):
        read_report(store, arranged.id, "bundle")
