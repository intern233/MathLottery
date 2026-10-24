"""UI/CLI report integration uses scripted agents, never a real account or model."""

import hashlib
import io
import zipfile

import pytest
from test_native import FAKE_NATIVE
from test_organization import Editor
from test_organization import reviewed as reviewed
from test_web import SIGNED_IN, finished, serving
from test_web import web as web
from typer.testing import CliRunner

from mathlottery import organization
from mathlottery.cli import app
from mathlottery.models import Phase, State
from mathlottery.orchestrator import Orchestrator
from mathlottery.organized_reports import read_report
from mathlottery.storage import json_text
from mathlottery.web.service import StartRequest, WebService


@pytest.fixture
def rendered(monkeypatch):
    def render(markdown, destination, **kwargs):
        data = b"%PDF-1.4\nscripted-export-fixture"
        destination.write_bytes(data)
        return {"sha256": hashlib.sha256(data).hexdigest(), "warnings": []}
    monkeypatch.setattr("mathlottery.report_pdf.render_pdf", render)


@pytest.mark.parametrize("extra", [
    {"statement": "replacement"}, {"proof": "replacement"}, {"query": "search"},
    {"source_files": ["workspace/Main.lean"]}, {"language": "fr"},
    {"from_run": None},
])
def test_organize_request_rejects_ambiguous_inputs(extra):
    with pytest.raises(ValueError):
        StartRequest.model_validate({"workflow": "organize", "from_run": "run-000000000001", **extra})


def test_http_four_stages_preserve_source_and_link_solver(web, monkeypatch):
    # The worker is a real child process; its agent is a local deterministic CLI fixture.
    executable = web.store.root / "scripted-codex"
    code = FAKE_NATIVE.replace(
        "if 'Task: FIND' in prompt:",
        "if 'Task: ORGANIZE' in prompt:\n"
        "            checkpoint.update(kind='organization', report_markdowns={'en': '# Expert exposition\\n\\nThe fixture remains inconclusive.', 'zh': '# 专家报告\\n\\n此测试问题仍无定论。'})\n"
        "        elif 'Task: FIND' in prompt:",
    )
    executable.write_text(executable.read_text().splitlines()[0] + "\n" + code)
    with serving(web, account_status=SIGNED_IN) as (client, _):
        client.headers["X-MathLottery-Token"] = client.get("/api/bootstrap").json()["csrf_token"]
        response = client.post("/api/runs", json={"workflow": "find", "query": "Fixture"})
        assert response.status_code == 202, response.text
        found = finished(web, response.json()["id"])
        problem_id = found["shortlist"][0]["id"]
        response = client.post("/api/runs", json={"workflow": "solve", "from_discovery": found["id"],
            "problem_id": problem_id, "discovery_problem_sha256": found["shortlist_bindings"][problem_id]})
        solved = finished(web, response.json()["id"])
        response = client.post("/api/runs", json={"workflow": "verify", "from_run": solved["id"]})
        reviewed = finished(web, response.json()["id"])
        source = web.store.load(reviewed["id"])
        assert source.review_source.source_run_id == solved["id"]
        before = json_text(source)
        response = client.post("/api/runs", json={"workflow": "organize", "from_run": source.id,
            "language": "en", "instructions": "Explain gaps clearly"})
        assert response.status_code == 202, response.text
        arranged = finished(web, response.json()["id"])
        assert arranged["state"] == "COMPLETED", arranged.get("last_error")
        assert arranged["problem_key"] == reviewed["problem_key"]
        assert arranged["candidates"] == reviewed["candidates"]
        assert arranged["reviewed_candidate_count"] == 0  # Never recursively organize a report.
        assert arranged["organized_report"]["markdown_available"]
        assert arranged["organized_report"]["language"] == "en"
        assert arranged["organized_report"]["bilingual_complete"]
        assert set(arranged["organized_report"]["reports"]) == {"zh", "en"}
        assert json_text(web.store.load(source.id)) == before
        saved = web.store.load(arranged["id"])
        assert {item["run_id"] for item in saved.organization_context.lineage} == {source.id, solved["id"]}
        download = client.get(f"/api/runs/{saved.id}/organized?format=markdown")
        assert download.status_code == 200 and "INCONCLUSIVE" in download.text
        assert "attachment" in download.headers["content-disposition"]
        assert "Expert exposition" in download.text
        assert "config.yaml" not in download.text
        chinese = client.get(f"/api/runs/{saved.id}/organized?format=markdown&language=zh")
        assert chinese.status_code == 200 and "专家报告" in chinese.text
        assert ".zh.md" in chinese.headers["content-disposition"]
        assert "INCONCLUSIVE" in chinese.text
        for query in ("format=markdown&language=fr", "format=markdown&language=",
                      "format=markdown&language=en&language=zh", "format=bundle&language=en"):
            assert client.get(f"/api/runs/{saved.id}/organized?{query}").status_code == 400
        assert client.get(f"/api/runs/{saved.id}/organized?format=../../config.yaml").status_code == 400
        # PDF is optional in installations without the reports extra. Both outcomes are explicit.
        pdf = client.get(f"/api/runs/{saved.id}/organized?format=pdf")
        if saved.organization_report.pdf_status == "ready":
            assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF-")
        else:
            assert pdf.status_code == 400 and saved.organization_report.pdf_error


def test_http_pdf_retry_needs_no_login_or_inference(store, reviewed, rendered, monkeypatch):
    config, engine, source = reviewed
    run = engine.organize(config, source.id)
    organization.accept(run, {"en": "# Expert draft\nThe gap remains.", "zh": "# 专家报告\n缺口仍然存在。"})
    run.state, run.phase = State.COMPLETED, Phase.REPORT
    run.organization_report.pdf_status = "failed"
    store.save(run, "fixture_draft")
    service = WebService(store.root)
    monkeypatch.setattr(Orchestrator, "drive", lambda *a: pytest.fail("Retry must not call a model"))
    with serving(service, account_status={"available": False, "authenticated": False}) as (client, _):
        path = f"/api/runs/{run.id}/organized"
        assert client.post(path, json={}).status_code == 403
        client.headers["X-MathLottery-Token"] = client.get("/api/bootstrap").json()["csrf_token"]
        response = client.post(path, json={})
        assert response.status_code == 200, response.text
        assert response.json()["pdf_available"]
        assert all(version["pdf_available"] for version in response.json()["reports"].values())
        assert client.get(path + "?format=pdf").content.startswith(b"%PDF-")
        for language in ("zh", "en"):
            assert client.get(path + f"?format=pdf&language={language}").content.startswith(b"%PDF-")
        bundle = client.get(path + "?format=bundle")
        assert bundle.status_code == 200 and bundle.headers["content-type"] == "application/zip"
        with zipfile.ZipFile(io.BytesIO(bundle.content)) as archive:
            assert {"report.md", "report.pdf", "manifest.json"} <= set(archive.namelist())
            assert {f"report.{language}.{extension}" for language in ("zh", "en")
                    for extension in ("md", "pdf")} <= set(archive.namelist())
            assert any(name.startswith("materials/") for name in archive.namelist())
        assert client.post(path, json={"model": "unexpected"}).status_code == 400
        assert client.get(path + "?format=pdf&path=auth.json").status_code == 400
        assert client.get(path + "?format=pdf&format=markdown").status_code == 400


def test_pdf_download_rejects_links_and_changed_bytes(store, reviewed, rendered, tmp_path):
    config, engine, source = reviewed
    run = engine.organize(config, source.id)
    organization.accept(run, {"zh": "An expert draft", "en": "Another expert draft"})
    run.state, run.phase = State.COMPLETED, Phase.REPORT
    store.save(run, "fixture_draft")
    engine.export_organized(run.id)
    path = store.run_dir(run.id) / "organized/report.pdf"
    path.write_bytes(b"%PDF-1.4\nchanged")
    with pytest.raises(ValueError, match="integrity"):
        read_report(store, run.id, "pdf")
    path.unlink()
    outside = tmp_path / "private.pdf"
    outside.write_bytes(b"%PDF-1.4\nprivate")
    path.symlink_to(outside)
    with pytest.raises(ValueError, match="unreadable"):
        read_report(store, run.id, "pdf")
    assert b"expert draft" in read_report(store, run.id, "markdown")


def test_cli_organize_and_local_exports(store, reviewed, rendered, monkeypatch, tmp_path):
    _, _, source = reviewed
    original_drive = Orchestrator.drive
    editor = Editor()
    def drive(engine, run_id):
        engine.backend_override = editor
        return original_drive(engine, run_id)
    monkeypatch.setattr(Orchestrator, "drive", drive)
    runner = CliRunner()
    result = runner.invoke(app, ["--root", str(store.root), "organize", "--from-run", source.id,
                                 "--language", "en", "--budget-time", "2m"])
    assert result.exit_code == 0, result.output
    organized = next(run for run in store.list_runs() if run.workflow == "organize")
    assert organized.organization_context.language == "en"
    assert organized.config["budget"]["max_wall_time_minutes"] == 2
    assert len(editor.calls) == 1
    exported = tmp_path / "expert.md"
    result = runner.invoke(app, ["--root", str(store.root), "export", organized.id, "--output", str(exported)])
    assert result.exit_code == 0, result.output
    assert "A readable exposition" in exported.read_text()
    chinese = tmp_path / "expert.zh.md"
    result = runner.invoke(app, ["--root", str(store.root), "export", organized.id,
                                 "--language", "zh", "--output", str(chinese)])
    assert result.exit_code == 0, result.output
    assert chinese.read_text() == read_report(store, organized.id, "markdown", language="zh").decode()
    result = runner.invoke(app, ["--root", str(store.root), "export", organized.id, "--format", "pdf"])
    assert result.exit_code == 0 and "organized/report.pdf" in result.output
    assert len(editor.calls) == 1
    result = runner.invoke(app, ["--root", str(store.root), "export", organized.id,
                                 "--format", "pdf", "--language", "en"])
    assert result.exit_code == 0 and "organized/report.en.pdf" in result.output
    bundle = tmp_path / "expert.zip"
    result = runner.invoke(app, ["--root", str(store.root), "export", organized.id, "--format", "bundle",
                                 "--output", str(bundle)])
    assert result.exit_code == 0, result.output
    with zipfile.ZipFile(bundle) as archive:
        assert {"report.md", "report.pdf", "manifest.json"} <= set(archive.namelist())
    assert len(editor.calls) == 1
    result = runner.invoke(app, ["--root", str(store.root), "export", organized.id,
                                 "--format", "bundle", "--language", "en", "--output", str(tmp_path / "bad.zip")])
    assert result.exit_code != 0 and not (tmp_path / "bad.zip").exists()
    result = runner.invoke(app, ["--root", str(store.root), "export", organized.id, "--output", str(exported)])
    assert result.exit_code != 0  # Existing expert files are never overwritten by export --output.


def test_cli_verify_records_solver_provenance_without_attachments(store, reviewed, monkeypatch):
    _, _, source = reviewed
    monkeypatch.setattr(Orchestrator, "drive", lambda engine, run_id: engine.store.load(run_id))
    result = CliRunner().invoke(app, ["--root", str(store.root), "verify", "--from-run", source.id])
    assert result.exit_code == 0, result.output
    review = next(run for run in store.list_runs() if run.id != source.id)
    assert review.review_evidence is None
    assert review.review_source.source_run_id == source.id
    assert review.review_source.candidate_sha256 == source.candidates[-1].sha256
