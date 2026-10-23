"""Organization uses real checkpoints with scripted inference, never mathematical verdicts."""

import json
import sys
import types

import pytest

from mathlottery import organization
from mathlottery.backends import BackendResult, BackendStatus
from mathlottery.config import Config
from mathlottery.demo import demo_problem
from mathlottery.milestones import validate_milestone
from mathlottery.models import (
    CandidateInput,
    Level,
    Phase,
    Review,
    ReviewProvenance,
    State,
    Workflow,
    now,
)
from mathlottery.native import NativeRunner
from mathlottery.orchestrator import Orchestrator
from mathlottery.storage import atomic_write, json_text


@pytest.fixture
def reviewed(store):
    config = Config()
    config.budget.max_iterations = 2
    engine = Orchestrator(store)
    source = engine.create(config, problem=demo_problem(), workflow=Workflow.VERIFY,
                           candidate=CandidateInput(claim="A precise fixture claim", proof="A saved proof"))
    source.candidates[-1].reviews.append(Review(
        verdict="INCONCLUSIVE", truth_assessment="Unknown", proof_assessment="Missing lemma",
        issues=["Missing step"], novelty="UNKNOWN", original_problem_coverage="PARTIAL",
        remaining_obligations=["Prove the missing lemma"],
    ))
    source.candidates[-1].level = Level.PARTIALLY_VERIFIED
    source.state, source.phase = State.COMPLETED, Phase.REPORT
    source.native.solver_session_id = "old-solver-session"
    source.native.reviewer_session_id = "old-review-session"
    store.save(source, "fixture_reviewed")
    return config, engine, source


@pytest.fixture
def pdf(monkeypatch):
    calls = []

    def render(markdown, destination, **kwargs):
        calls.append(markdown)
        destination.write_bytes(b"%PDF-1.4\nfixture")
        return {"renderer": "fixture", "warnings": []}

    # A deterministic renderer isolates workflow checks from optional system PDF dependencies.
    monkeypatch.setitem(sys.modules, "mathlottery.report_pdf", types.SimpleNamespace(render_pdf=render))
    return calls


class Editor:
    def __init__(self, kind="organization"):
        self.calls = []
        self.kind = kind

    def invoke_native(self, prompt, directory, workspace, timeout, **kwargs):
        self.calls.append({"prompt": prompt, "workspace": workspace, **kwargs})
        fields = dict(line.split(": ", 1) for line in prompt.splitlines()
                      if line.startswith(("run_id: ", "task_id: ")))
        milestone = {**fields, "kind": self.kind, "summary": "Visible editorial work"}
        if self.kind == "organization":
            milestone["report_markdown"] = "# A readable exposition\n\nThe missing lemma remains unproved.\n"
        text = "Draft saved.\n```mathlottery\n" + json.dumps(milestone) + "\n```\n"
        return BackendResult(BackendStatus.COMPLETED, text=text, invoked=True,
                             usage={"input_tokens": 12, "output_tokens": 5})


def test_editorial_workflow_preserves_source_and_review_evidence(store, reviewed, pdf):
    config, engine, source = reviewed
    original = json_text(store.load(source.id))
    backend = Editor()
    engine.backend_override = backend
    run = engine.organize(config, source.id, language="en", instructions="Explain lemma dependencies")
    assert run.phase == Phase.ORGANIZE
    assert run.native.solver_session_id is run.native.reviewer_session_id is None
    assert organization.eligible(source) and not organization.eligible(run)
    assert any("no saved solver linkage" in line for line in run.organization_context.limitations)
    result = engine.drive(run.id)
    assert result.state == State.COMPLETED
    assert result.organization_report.pdf_status == "ready"
    assert len(backend.calls) == len(pdf) == 1
    assert backend.calls[0]["reviewer"] is True  # Disables shared mutable model memories.
    assert backend.calls[0]["session_id"] is None
    assert "Task: ORGANIZE" in backend.calls[0]["prompt"]
    assert "Explain lemma dependencies" in backend.calls[0]["prompt"]
    assert backend.calls[0]["workspace"].name == "organization-workspace"
    assert json_text(store.load(source.id)) == original
    assert result.candidates == source.candidates
    assert result.native.history[0]["role"] == "organization"
    report = (store.run_dir(run.id) / "organized/report.md").read_text()
    assert "INCONCLUSIVE" in report and "PARTIAL" in report and "UNKNOWN" in report
    assert "does not upgrade proof status" in report
    manifest = json.loads((store.run_dir(run.id) / "organized/manifest.json").read_text())
    assert manifest["candidate_hashes"][0]["sha256"] == source.candidates[0].sha256
    assert manifest["report"]["pdf"] == "report.pdf"
    assert (store.run_dir(run.id) / f"organized/materials/{source.id}/dossier.json").is_file()


def test_capture_includes_named_sources_not_credentials_or_raw_events(store, reviewed):
    config, engine, source = reviewed
    base = store.run_dir(source.id)
    for path in ("workspace/proof/Main.lean", "workspace/notes/math.md", "workspace/notes.md"):
        atomic_write(base / path, "Mathematical content")
    for path in ("workspace/auth.json", "workspace/config.toml", "workspace/private.txt",
                 "workspace/proof/.env", "workspace/proof/auth.json", "workspace/proof/.lake/Main.lean",
                 "tasks/task-000000000001/attempt-000000000001/codex.events.jsonl"):
        atomic_write(base / path, "PRIVATE_SENTINEL")
    atomic_write(base / "tasks/task-000000000001/attempt-000000000001/answer.md", "Saved derivation")
    source.native.history.append({"role": "research", "answer": "tasks/task-000000000001/attempt-000000000001/answer.md"})
    source.config["backend"]["model"] = "PRIVATE_CONFIG_SENTINEL"
    source.environment["private"] = "PRIVATE_ENV_SENTINEL"
    store.save(source, "fixture_artifacts")
    run = engine.organize(config, source.id)
    bundle = b"\n".join(data for _, data in organization._read_files(store, run))
    assert b"Saved derivation" in bundle and b"Mathematical content" in bundle
    assert b"PRIVATE_SENTINEL" not in bundle
    assert b"PRIVATE_CONFIG_SENTINEL" not in bundle and b"PRIVATE_ENV_SENTINEL" not in bundle


@pytest.mark.parametrize("kind,payload", [
    ("candidate", {"candidate": {"claim": "replacement", "proof": "replacement"}}),
    ("review", {"review": {"verdict": "NO_ISSUES_FOUND", "truth_assessment": "yes", "proof_assessment": "yes"}}),
    ("progress", {"problem": {"id": "replacement", "title": "replacement", "statement": "replacement"}}),
])
def test_organizer_cannot_replace_mathematical_outputs(reviewed, kind, payload):
    config, engine, source = reviewed
    run = engine.organize(config, source.id)
    run.task_id = "task-fixture"
    with pytest.raises(ValueError, match="cannot change"):
        validate_milestone(run, {"run_id": run.id, "task_id": run.task_id, "kind": kind, **payload})


def test_ordinary_solver_cannot_submit_editorial_milestone(reviewed):
    config, engine, _ = reviewed
    run = engine.create(config, demo_problem(), workflow=Workflow.SOLVE)
    run.task_id = "task-fixture"
    with pytest.raises(ValueError, match="Only an organizing"):
        validate_milestone(run, {"run_id": run.id, "task_id": run.task_id,
                                 "kind": "organization", "report_markdown": "Report"})


def test_busy_unreviewed_and_structured_sources_are_rejected(store, reviewed):
    config, engine, source = reviewed
    source.active_since = now()
    store.save(source, "fixture_active")
    with pytest.raises(ValueError, match="Finish, stop"):
        engine.organize(config, source.id)
    source.active_since = None
    source.candidates[0].reviews = []
    store.save(source, "fixture_unreviewed")
    with pytest.raises(ValueError, match="recorded candidate review"):
        engine.organize(config, source.id)
    config.backend.execution = "structured"
    with pytest.raises(ValueError, match="native execution"):
        engine.organize(config, source.id)


def test_frozen_bundle_tampering_fails_before_model_call(store, reviewed):
    config, engine, source = reviewed
    run = engine.organize(config, source.id)
    item = run.organization_context.files[0]
    path = store.run_dir(run.id) / "organization-context" / item.path
    path.write_text("Replaced evidence")
    backend = Editor()
    engine.backend_override = backend
    result = engine.drive(run.id)
    assert result.state == State.FAILED
    assert "snapshot was modified" in result.last_error
    assert backend.calls == []


def test_candidate_review_mutation_fails_before_model_call(store, reviewed):
    config, engine, source = reviewed
    run = engine.organize(config, source.id)
    run.candidates[0].reviews[0].verdict = "NO_ISSUES_FOUND"
    store.save(run, "fixture_tamper")
    backend = Editor()
    engine.backend_override = backend
    result = engine.drive(run.id)
    assert result.state == State.FAILED
    assert "candidate/review snapshot was modified" in result.last_error
    assert not backend.calls


def test_pdf_failure_retains_durable_markdown_and_local_retry(store, reviewed, pdf, monkeypatch):
    config, engine, source = reviewed
    backend = Editor()
    engine.backend_override = backend
    module = sys.modules["mathlottery.report_pdf"]
    good_render = module.render_pdf

    def fail(*args, **kwargs):
        raise RuntimeError("PRIVATE_RENDERER_PATH")

    monkeypatch.setattr(module, "render_pdf", fail)
    result = engine.drive(engine.organize(config, source.id).id)
    assert result.state == State.COMPLETED
    assert result.organization_report.pdf_status == "failed"
    assert "PRIVATE_RENDERER_PATH" not in json_text(result.organization_report)
    assert (store.run_dir(result.id) / "organized/report.md").is_file()
    monkeypatch.setattr(module, "render_pdf", good_render)
    retried = engine.export_organized(result.id)
    assert retried.organization_report.pdf_status == "ready"
    assert len(backend.calls) == 1
    assert retried.organization_report.markdown == result.organization_report.markdown


def test_pause_and_steered_resume_stay_in_organization(store, reviewed, pdf):
    config, engine, source = reviewed
    config.budget.max_iterations = 1
    backend = Editor(kind="progress")
    engine.backend_override = backend
    run = engine.drive(engine.organize(config, source.id).id)
    assert run.state == State.PAUSED and run.phase == Phase.ORGANIZE
    config.budget.max_iterations = 3
    backend.kind = "organization"
    result = engine.resume(run.id, config=config, message="Add an exposition of the gap")
    assert result.state == State.COMPLETED and result.organization_report is not None
    assert "Add an exposition of the gap" in backend.calls[-1]["prompt"]
    # A revision to an existing report is still editorial, and never a return to Solve.
    revised = engine.resume(run.id, message="Clarify notation")
    assert revised.state == State.COMPLETED
    assert "Task: ORGANIZE" in backend.calls[-1]["prompt"]
    assert revised.candidates == source.candidates


def test_recover_queued_editor_result_does_not_repeat_inference(store, reviewed, pdf):
    config, engine, source = reviewed
    run = engine.organize(config, source.id)
    runner = NativeRunner(engine)
    backend = Editor()
    prompt = runner.prepare(run, config)
    runner.queue(run, runner.attempts.invoke(run, backend, prompt, config))
    assert store.load(run.id).native.pending_result is not None
    engine.backend_override = backend
    result = engine.drive(run.id)
    assert result.state == State.COMPLETED
    assert len(backend.calls) == 1
    assert result.iteration == 1


def test_explicit_solver_lineage_is_captured_but_titles_are_not_guessed(store, reviewed):
    config, engine, source = reviewed
    solver = engine.create(config, demo_problem(), workflow=Workflow.SOLVE)
    candidate = engine._candidate(solver, CandidateInput(claim=source.candidates[0].claim,
                                                        proof=source.candidates[0].proof))
    solver.state = State.COMPLETED
    store.save(solver, "fixture_solved")
    source.review_source = ReviewProvenance(source_run_id=solver.id, source_candidate_id=candidate.id,
                                           candidate_sha256=candidate.sha256)
    store.save(source, "fixture_linked")
    run = engine.organize(config, source.id)
    assert {item["run_id"] for item in run.organization_context.lineage} == {source.id, solver.id}
    assert not any("no saved solver linkage" in line for line in run.organization_context.limitations)
    assert any(item.path == f"{solver.id}/dossier.json" for item in run.organization_context.files)


def test_chat_has_explicit_bounded_inline_context(store, reviewed, monkeypatch):
    config, engine, source = reviewed
    config.backend.mode = "chat"
    config.backend.model = "fixture-model"
    monkeypatch.setattr(organization, "CHAT_MAX_BYTES", 20)
    with pytest.raises(ValueError, match="complete candidate/review dossier"):
        engine.organize(config, source.id)


def test_linked_and_oversized_files_are_not_silently_copied(store, reviewed, monkeypatch):
    config, engine, source = reviewed
    root = store.run_dir(source.id)
    atomic_write(root / "workspace/proof/large.md", "x" * 1000)
    (root / "workspace/proof/linked.md").symlink_to(root / "config.yaml")
    monkeypatch.setattr(organization, "MAX_FILE_BYTES", 100)
    run = engine.organize(config, source.id)
    assert all("large.md" not in f.path and "linked.md" not in f.path for f in run.organization_context.files)
    assert any("large.md" in reason for reason in run.organization_context.omitted)
    assert any("linked.md" in reason for reason in run.organization_context.omitted)


def test_pdf_projection_rejects_link_swapped_by_renderer(store, reviewed, pdf, monkeypatch, tmp_path):
    config, engine, source = reviewed
    run = engine.organize(config, source.id)
    organization.accept(run, "# Exposition\n\nA remaining proof gap.")
    store.save(run, "fixture_draft")
    outside = tmp_path / "outside-export"
    outside.mkdir()
    module = sys.modules["mathlottery.report_pdf"]
    regular_render = module.render_pdf
    root = store.run_dir(run.id)

    def swap_parent(markdown, destination, **kwargs):
        result = regular_render(markdown, destination, **kwargs)
        (root / "organized").rename(root / "organized-before-swap")
        (root / "organized").symlink_to(outside, target_is_directory=True)
        return result

    monkeypatch.setattr(module, "render_pdf", swap_parent)
    with pytest.raises(OSError):
        organization.export(store, run)
    assert list(outside.iterdir()) == []
    assert store.load(run.id).organization_report.pdf_status == "failed"
    assert (root / "organized-before-swap/report.md").is_file()


def test_source_mutation_after_capture_does_not_change_organized_inputs(store, reviewed):
    config, engine, source = reviewed
    run = engine.organize(config, source.id)
    captured = b"\n".join(data for _, data in organization._read_files(store, run))
    source.candidates[0].reviews[0].verdict = "NO_ISSUES_FOUND"
    store.save(source, "fixture_later_source_change")
    assert b"\n".join(data for _, data in organization._read_files(store, run)) == captured
    assert run.candidates[0].reviews[0].verdict == "INCONCLUSIVE"


def test_chat_receives_evidence_once_and_no_original_session(store, reviewed):
    config, engine, source = reviewed
    config.backend.mode = "chat"
    config.backend.model = "fixture-model"
    run = engine.organize(config, source.id, language="en")
    runner = NativeRunner(engine)
    prompt = runner.prepare(run, config)
    assert "A saved proof" in prompt
    assert "PRIVATE" not in prompt
    assert run.native.solver_response_id is None
    run.native.solver_response_id = "resp_editor_chain"
    continued = runner.prepare(run, config)
    assert "already supplied in this response chain" in continued
    assert "A saved proof" not in continued


def test_historical_formal_layouts_include_sources_without_build_caches(store, reviewed):
    config, engine, source = reviewed
    root = store.run_dir(source.id)
    candidate = source.candidates[0]
    wanted = [
        "workspace/research/lean/Lemma.lean",
        f"review-workspaces/{candidate.id}/audits/codex_audits/2026-01-01/Claim.lean",
        f"review-workspaces/{candidate.id}/inputs/final-formal/Main.lean",
        f"review-workspaces/{candidate.id}/inputs/final-formal/lean-toolchain",
        f"review-workspaces/{candidate.id}/inputs/final-formal/lakefile.toml",
    ]
    for path in wanted:
        atomic_write(root / path, "Formal source fixture")
    excluded = ["workspace/research/lean/.lake/packages/mathlib/Big.lean",
                "workspace/research/lean/build/Cache.lean",
                f"review-workspaces/{candidate.id}/credentials/Private.lean",
                f"review-workspaces/{candidate.id}/inputs/final-formal/auth.json",
                "workspace/unrelated.json"]
    for path in excluded:
        atomic_write(root / path, "DO_NOT_COPY")
    run = engine.organize(config, source.id)
    paths = {item.path.removeprefix(source.id + "/") for item in run.organization_context.files}
    assert set(wanted) <= paths
    assert not set(excluded) & paths


def test_switch_to_chat_checks_frozen_dossier_limit_before_inference(reviewed, monkeypatch):
    config, engine, source = reviewed
    run = engine.organize(config, source.id)
    backend = Editor()
    engine.backend_override = backend
    monkeypatch.setattr(organization, "CHAT_MAX_BYTES", 20)
    result = engine.resume(run.id, mode="chat")
    assert result.state == State.FAILED
    assert "frozen organization dossier exceeds Chat" in result.last_error
    assert backend.calls == []


def test_controlled_pdf_setup_instructions_are_visible(reviewed, pdf, monkeypatch):
    config, engine, source = reviewed
    module = sys.modules["mathlottery.report_pdf"]

    class PDFRenderError(RuntimeError):
        pass

    module.PDFRenderError = PDFRenderError

    def needs_install(*args, **kwargs):
        raise PDFRenderError("Install PDF support with pip install -e '.[pdf]' and python -m playwright install chromium.")

    monkeypatch.setattr(module, "render_pdf", needs_install)
    engine.backend_override = Editor()
    result = engine.drive(engine.organize(config, source.id).id)
    assert result.state == State.COMPLETED
    assert result.organization_report.pdf_status == "failed"
    assert "playwright install chromium" in result.organization_report.pdf_error
    assert "Markdown is available" in result.organization_report.pdf_error
