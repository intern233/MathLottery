"""Source handoff preserves exact inputs without promoting them to proofs."""

import fcntl
import json

import pytest
from test_web import SIGNED_IN, serving

from mathlottery.config import Config
from mathlottery.models import CandidateInput, Level, Problem, Run, State, Workflow
from mathlottery.runtime.orchestrator import Orchestrator
from mathlottery.runtime.workspace import NativeWorkspace
from mathlottery.verify.evidence import project
from mathlottery.web.jobs import BusyError
from mathlottery.web.service import StartRequest, WebService


@pytest.fixture
def evidence_source(tmp_path, monkeypatch):
    service = WebService(tmp_path)
    engine = Orchestrator(service.store)
    source = engine.create(
        Config(), Problem(id="source", title="Example", statement="For every n, n + 0 = n"),
        workflow=Workflow.SOLVE,
    )
    engine.candidates.add(source, CandidateInput(claim=source.problem.statement, proof="By additive identity."))
    source.state = State.COMPLETED
    service.store.save(source, "fixture_source")
    launches = []
    monkeypatch.setattr(service.jobs, "launch", lambda *args, **kwargs: launches.append((args, kwargs)))
    return service, source, launches


def write(service, source, relative="workspace/formal/Proof.lean", text="example (n : Nat) : n + 0 = n := rfl\n"):
    path = service.store.run_dir(source.id) / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def request(source, **changes):
    candidate = source.candidates[-1]
    return StartRequest.model_validate({
        "workflow": "verify", "from_run": source.id,
        "from_candidate_id": candidate.id, "from_candidate_sha256": candidate.sha256,
        "source_files": ["workspace/formal/Proof.lean"], **changes,
    })


def create_review(service, source, **changes):
    started = service.start(request(source, **changes))
    return service.store.load(started["id"])


def test_exact_snapshot_survives_source_change_and_review_resume(evidence_source):
    service, source, launches = evidence_source
    original = write(service, source)
    content = original.read_bytes()
    write(service, source, "workspace/notes.md", "SOLVER_HISTORY_MUST_NOT_TRANSFER")
    write(service, source, "review-workspaces/old/Check.lean", "PREVIOUS_REVIEW_MUST_NOT_TRANSFER")
    review = create_review(service, source)
    snapshot = review.review_evidence
    assert snapshot.source_run_id == source.id
    assert snapshot.source_candidate_id == source.candidates[-1].id
    assert snapshot.candidate_id == review.candidates[-1].id
    assert snapshot.files[0].content.encode() == content
    assert launches == [((review.id, "drive"), {})]
    original.write_text("example : False := by sorry")
    workspace = NativeWorkspace(service.store, Orchestrator(service.store).candidates)
    prompt = workspace.prepare(review, Config())
    copied = workspace.path(review) / "submitted-evidence/formal/Proof.lean"
    assert copied.read_bytes() == content
    assert "untrusted candidate evidence" in prompt
    assert "SOLVER_HISTORY_MUST_NOT_TRANSFER" not in prompt
    assert "PREVIOUS_REVIEW_MUST_NOT_TRANSFER" not in prompt
    assert "example (n : Nat)" not in prompt  # Codex reads the local snapshot itself.
    copied.write_text("reviewer scratch work cannot change the submitted snapshot")
    original.unlink()
    reloaded = service.store.load(review.id)
    workspace.prepare(reloaded, Config())
    assert copied.read_bytes() == content
    assert reloaded.candidates[-1].level == Level.CANDIDATE
    assert service.store.load(source.id).candidates[-1].reviews == []


def test_explicit_proof_materials_are_frozen_without_running_scripts(evidence_source):
    service, source, launches = evidence_source
    materials = {
        "workspace/proof/Main.lean": "example : True := trivial\n",
        "workspace/proof/Proof.md": "A complete proof.\n",
        "workspace/proof/certificates.json": '{"coefficients":[1,2]}\n',
        "workspace/proof/check.py": 'raise RuntimeError("must not run during capture")\n',
    }
    for path, text in materials.items():
        write(service, source, path, text)
    write(service, source, "workspace/proof/Unselected.md", "not selected")
    write(service, source, "workspace/proof/logs/Transcript.md", "solver history")
    detail = service.detail(source.id)
    flags = {item["path"]: item["reviewable"] for item in detail["formal_artifacts"]["items"]}
    assert all(flags[path] for path in materials)
    assert not flags["workspace/proof/logs/Transcript.md"]
    review = create_review(service, source, source_files=list(materials))
    assert len(launches) == 1
    assert {item.path: item.content for item in review.review_evidence.files} == materials
    for path in materials:
        write(service, source, path, "changed after capture")
    workspace = NativeWorkspace(service.store, Orchestrator(service.store).candidates)
    workspace.prepare(review, Config())
    root = workspace.path(review) / "submitted-evidence"
    for path, text in materials.items():
        assert (root / path.removeprefix("workspace/")).read_text() == text
    assert not (root / "proof/Unselected.md").exists()
    assert not (root / "proof/logs").exists()
    assert review.candidates[-1].level == Level.CANDIDATE


def test_http_detail_exposes_manifest_not_source_contents(evidence_source):
    service, source, _ = evidence_source
    write(service, source, text="-- SOURCE_CONTENT_SENTINEL\nexample : True := trivial\n")
    with serving(service, account_status=SIGNED_IN) as (client, server):
        response = client.post("/api/runs", json=request(source).model_dump(),
                               headers={"X-MathLottery-Token": server.csrf_token})
        assert response.status_code == 202, response.text
        review_id = response.json()["id"]
        response = client.get(f"/api/runs/{review_id}")
        assert "SOURCE_CONTENT_SENTINEL" not in response.text
        manifest = response.json()["review_evidence"]
        assert set(manifest["files"][0]) == {"path", "size", "sha256"}
        assert len(manifest["files"][0]["sha256"]) == 64
        assert manifest["source_candidate_id"] == source.candidates[-1].id


def test_chat_receives_exact_inline_sources_and_manifest(evidence_source):
    service, source, _ = evidence_source
    write(service, source, text="-- unicode 数学\nexample : True := trivial\n")
    review = create_review(service, source, options={"backend": "chat"})
    workspace = NativeWorkspace(service.store, Orchestrator(service.store).candidates)
    prompt = workspace.prepare(review, Config())
    assert "unicode 数学" in prompt
    assert "Hosted tools cannot read local project paths" in prompt
    assert "submitted-evidence/manifest.json" not in prompt


@pytest.mark.parametrize("change", [
    {"from_candidate_id": "candidate-" + "0" * 12},
    {"from_candidate_sha256": "0" * 64},
])
def test_stale_candidate_binding_rejected_before_persistence(evidence_source, change):
    service, source, launches = evidence_source
    write(service, source)
    with pytest.raises(ValueError, match="candidate changed"):
        create_review(service, source, **change)
    assert len(service.store.list_runs()) == 1 and launches == []


def test_new_latest_candidate_requires_refresh(evidence_source):
    service, source, launches = evidence_source
    write(service, source)
    chosen = request(source)
    engine = Orchestrator(service.store)
    engine.candidates.add(source, CandidateInput(claim="A new claim", proof="A different proof"))
    service.store.save(source, "new_candidate")
    with pytest.raises(ValueError, match="candidate changed"):
        service.start(chosen)
    assert len(service.store.list_runs()) == 1 and launches == []


@pytest.mark.parametrize("relative", [
    "../secret.lean", "workspace/../secret.lean", "workspace/.lake/Proof.lean",
    "workspace/auth.json", "workspace/research-history.md", "workspace/build/Proof.lean",
    "workspace/research-history/Notes.lean", "workspace/logs/Transcript.lean",
    "workspace/cache/Dependency.lean", "workspace/submissions/Old.lean",
    "review-workspaces/old/Check.lean", "workspace/missing.lean",
])
def test_unselected_or_unapproved_source_locations_rejected(evidence_source, relative):
    service, source, launches = evidence_source
    with pytest.raises((ValueError, OSError)):
        create_review(service, source, source_files=[relative])
    assert len(service.store.list_runs()) == 1 and launches == []


@pytest.mark.parametrize("linked", ["file", "directory", "hardlink"])
def test_linked_sources_rejected_before_persistence(evidence_source, linked):
    service, source, launches = evidence_source
    original = write(service, source, "workspace/outside/Proof.lean")
    selected = original.parent.parent / "formal/Proof.lean"
    if linked == "directory":
        selected.parent.symlink_to(original.parent, target_is_directory=True)
    else:
        selected.parent.mkdir()
        if linked == "file":
            selected.symlink_to(original)
        else:
            selected.hardlink_to(original)
    with pytest.raises(ValueError):
        create_review(service, source)
    assert len(service.store.list_runs()) == 1 and launches == []


@pytest.mark.parametrize("variant", ["duplicate", "count", "single_size", "total_size", "chat_size", "binary"])
def test_snapshot_limits_reject_without_partial_runs(evidence_source, variant):
    service, source, launches = evidence_source
    changes = {}
    if variant == "duplicate":
        write(service, source)
        changes["source_files"] = ["workspace/formal/Proof.lean"] * 2
    elif variant == "count":
        changes["source_files"] = [f"workspace/{i}.lean" for i in range(21)]
    elif variant == "single_size":
        write(service, source, text="a" * 1_000_001)
    elif variant == "total_size":
        changes["source_files"] = [f"workspace/{i}.lean" for i in range(3)]
        for path in changes["source_files"]:
            write(service, source, path, "a" * 700_000)
    elif variant == "chat_size":
        # Byte limits, not character counts.
        write(service, source, text="数" * 43_000)
        changes["options"] = {"backend": "chat"}
    elif variant == "binary":
        write(service, source, text="\0not a source")
    with pytest.raises(ValueError):
        create_review(service, source, **changes)
    assert len(service.store.list_runs()) == 1 and launches == []


@pytest.mark.parametrize("worker", [False, True])
def test_active_or_queued_source_rejected(evidence_source, worker):
    service, source, launches = evidence_source
    write(service, source)
    if worker:
        directory = service.jobs.directory(source.id)
        directory.mkdir(parents=True)
        handle = (directory / "worker.lock").open("a")
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            with pytest.raises(BusyError, match="Stop the source"):
                create_review(service, source)
        finally:
            handle.close()
    else:
        with service.store.lock(source.id), pytest.raises(BusyError, match="Stop the source"):
            create_review(service, source)
    assert len(service.store.list_runs()) == 1 and launches == []


@pytest.mark.parametrize("field,value", [("content", "tampered"), ("sha256", "0" * 64), ("size", 0)])
def test_snapshot_tampering_is_detected_on_prepare(evidence_source, field, value):
    service, source, _ = evidence_source
    write(service, source)
    review = create_review(service, source)
    setattr(review.review_evidence.files[0], field, value)
    workspace = NativeWorkspace(service.store, Orchestrator(service.store).candidates)
    with pytest.raises(ValueError, match="integrity"):
        workspace.prepare(review, Config())


@pytest.mark.parametrize("field,value", [("candidate_id", "candidate-" + "0" * 12), ("candidate_sha256", "0" * 64)])
def test_wrong_review_candidate_binding_is_detected(evidence_source, field, value):
    service, source, _ = evidence_source
    write(service, source)
    review = create_review(service, source)
    setattr(review.review_evidence, field, value)
    workspace = NativeWorkspace(service.store, Orchestrator(service.store).candidates)
    with pytest.raises(ValueError, match="match the review candidate"):
        workspace.prepare(review, Config())


@pytest.mark.parametrize("part", ["submitted-evidence", "submitted-evidence/formal", "submitted-evidence/formal/Proof.lean"])
def test_resume_projection_cannot_follow_reviewer_symlinks(evidence_source, part):
    service, source, _ = evidence_source
    write(service, source)
    review = create_review(service, source)
    workspace = NativeWorkspace(service.store, Orchestrator(service.store).candidates)
    workspace.prepare(review, Config())
    root = workspace.path(review)
    selected = root / part
    outside = service.store.root / "outside"
    outside.mkdir()
    sentinel = outside / "Proof.lean"
    sentinel.write_text("outside must stay unchanged")
    selected.rename(selected.with_name(selected.name + "-saved"))
    selected.symlink_to(sentinel if part.endswith(".lean") else outside, target_is_directory=not part.endswith(".lean"))
    with pytest.raises((OSError, ValueError)):
        project(review, root)
    assert sentinel.read_text() == "outside must stay unchanged"
    assert list(outside.iterdir()) == [sentinel]


def test_empty_selection_preserves_old_requests_and_checkpoints(evidence_source):
    service, source, _ = evidence_source
    summary = service.start(StartRequest(workflow="verify", from_run=source.id))
    review = service.store.load(summary["id"])
    assert review.review_evidence is None
    legacy = review.model_dump()
    legacy.pop("review_evidence")
    assert Run.model_validate(legacy).review_evidence is None
    assert service.detail(review.id)["review_evidence"] is None
    assert "content" not in json.dumps(service.detail(review.id))


def test_detail_marks_only_current_solver_sources_as_reviewable(evidence_source):
    service, source, _ = evidence_source
    write(service, source)
    write(service, source, "review-workspaces/old/Check.lean")
    write(service, source, "workspace/research-history/Notes.lean")
    flags = {item["path"]: item["reviewable"] for item in service.detail(source.id)["formal_artifacts"]["items"]}
    assert flags == {
        "workspace/formal/Proof.lean": True,
        "review-workspaces/old/Check.lean": False,
        "workspace/research-history/Notes.lean": False,
    }


@pytest.mark.parametrize("changes", [
    {"from_candidate_sha256": None},
    {"from_candidate_id": None},
    {"workflow": "find", "from_run": None},
    {"from_run": None, "statement": "Claim", "proof": "Proof"},
])
def test_attachment_and_binding_fields_are_verify_from_run_only(evidence_source, changes):
    _, source, _ = evidence_source
    with pytest.raises(ValueError):
        request(source, **changes)
