"""Language-specific exports retain source fidelity and independent PDF status."""

import hashlib
import io
import json
import zipfile

import pytest
from test_organization import reviewed as reviewed
from test_web import serving
from typer.testing import CliRunner

from mathlottery.cli import app
from mathlottery.models import Phase, State
from mathlottery.organize import workflow as organization
from mathlottery.organize.downloads import read_report, summary
from mathlottery.storage.core import json_text
from mathlottery.web.service import WebService


@pytest.fixture
def bilingual(store, reviewed, monkeypatch):
    config, engine, source = reviewed
    before = json_text(source)
    run = engine.organize(config, source.id, language="zh")
    organization.accept(run, {"zh": "# 中文报告\n\n尚有证明缺口。", "en": "# English report\n\nThe proof gap remains."})
    run.state, run.phase = State.COMPLETED, Phase.REPORT
    store.save(run, "bilingual_fixture")

    def render(markdown, destination, **kwargs):
        payload = b"%PDF-1.4\n" + hashlib.sha256(markdown.encode()).digest()
        destination.write_bytes(payload)
        return {"warnings": []}

    monkeypatch.setattr("mathlottery.organize.pdf.render_pdf", render)
    run = engine.export_organized(run.id)
    assert json_text(store.load(source.id)) == before
    return run


def test_bilingual_bundle_and_manifest_bind_each_version(store, bilingual):
    metadata = summary(store, bilingual)
    assert metadata["bilingual_complete"] and set(metadata["languages"]) == {"zh", "en"}
    assert all(item["pdf_available"] for item in metadata["reports"].values())
    documents = organization.report_documents(bilingual)
    with zipfile.ZipFile(io.BytesIO(read_report(store, bilingual.id, "bundle"))) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        for language, document in documents.items():
            name = f"report.{language}.md"
            assert archive.read(name).decode() == document.markdown
            assert manifest["reports"][language]["sha256"] == hashlib.sha256(archive.read(name)).hexdigest()
            assert archive.read(f"report.{language}.pdf") == read_report(store, bilingual.id, "pdf", language)
        assert archive.read("report.md") == archive.read("report.zh.md")
        assert archive.read("report.pdf") == archive.read("report.zh.pdf")
        assert archive.read("report.en.pdf") != archive.read("report.zh.pdf")
        assert "INCONCLUSIVE" in archive.read("report.en.md").decode()
        assert "INCONCLUSIVE" in archive.read("report.zh.md").decode()


@pytest.mark.parametrize("tamper", ["translated_markdown", "translated_pdf", "translated_pdf_link"])
def test_bilingual_export_refuses_tampering_in_either_language(store, bilingual, tmp_path, tamper):
    if tamper == "translated_markdown":
        bilingual.organization_report.translations["en"].markdown += "Altered conclusion"
        store.save(bilingual, "tampered_translation")
    else:
        path = store.run_dir(bilingual.id) / "organized/report.en.pdf"
        if tamper == "translated_pdf":
            path.write_bytes(b"%PDF-1.4\nchanged")
        else:
            path.unlink()
            private = tmp_path / "outside.pdf"
            private.write_bytes(b"%PDF-1.4\nprivate")
            path.symlink_to(private)
    for format in ("bundle", "markdown" if tamper == "translated_markdown" else "pdf"):
        with pytest.raises(ValueError, match="integrity|unreadable"):
            read_report(store, bilingual.id, format, None if format == "bundle" else "en")


def test_pdf_failure_in_one_language_preserves_other_report_and_retry_is_local(store, bilingual, monkeypatch):
    from mathlottery.runtime.orchestrator import Orchestrator

    def render(markdown, destination, **kwargs):
        if "# English report" in markdown:
            raise RuntimeError("PRIVATE_RENDERER_DIAGNOSTIC")
        destination.write_bytes(b"%PDF-1.4\nChinese")
        return {}

    monkeypatch.setattr("mathlottery.organize.pdf.render_pdf", render)
    monkeypatch.setattr(Orchestrator, "drive", lambda *args: pytest.fail("Local retry must not call a model"))
    before = {language: doc.markdown_sha256 for language, doc in organization.report_documents(bilingual).items()}
    run = Orchestrator(store).export_organized(bilingual.id)
    metadata = summary(store, run)
    assert metadata["reports"]["zh"]["pdf_available"]
    assert not metadata["reports"]["en"]["pdf_available"]
    assert metadata["reports"]["en"]["pdf_status"] == "failed"
    assert "PRIVATE_" not in json.dumps(metadata)
    assert before == {language: doc.markdown_sha256 for language, doc in organization.report_documents(run).items()}
    assert b"English report" in read_report(store, run.id, "markdown", "en")
    with pytest.raises(ValueError, match="not ready"):
        read_report(store, run.id, "pdf", "en")
    with zipfile.ZipFile(io.BytesIO(read_report(store, run.id, "bundle"))) as archive:
        assert {"report.zh.md", "report.en.md", "report.zh.pdf"} <= set(archive.namelist())
        assert "report.en.pdf" not in archive.namelist()


def test_legacy_language_selection_is_honest_and_never_implicitly_translates(store, reviewed, monkeypatch):
    config, engine, source = reviewed
    run = engine.organize(config, source.id, language="zh")
    run.organization_context.report_languages = None
    organization.accept(run, "# 历史中文报告")
    run.state, run.phase = State.COMPLETED, Phase.REPORT
    store.save(run, "legacy_report")
    metadata = summary(store, run)
    assert not metadata["bilingual_complete"] and metadata["languages"] == ["zh"]
    with serving(WebService(store.root), account_status={"available": False}) as (client, _):
        endpoint = f"/api/runs/{run.id}/organized?format=markdown"
        assert client.get(endpoint + "&language=zh").status_code == 200
        assert client.get(endpoint + "&language=en").status_code == 400
    before = json_text(store.load(run.id))
    result = CliRunner().invoke(app, ["--root", str(store.root), "export", run.id,
                                     "--format", "pdf", "--language", "en"])
    assert result.exit_code != 0 and "requested report language" in result.output
    assert json_text(store.load(run.id)) == before
