"""User choice, provenance and reproducible context handoff; no model calls."""

import json

import pytest

from mathlottery.config import Config
from mathlottery.discovery import problem_fingerprint
from mathlottery.models import Phase, Problem, State, Workflow, digest
from mathlottery.native import NativeRunner
from mathlottery.orchestrator import Orchestrator
from mathlottery.storage import atomic_write, json_text


@pytest.fixture
def discovery(store):
    config = Config()
    engine = Orchestrator(store)
    source = engine.create(config, workflow=Workflow.FIND, discovery_request="Small combinatorial problems")
    first = Problem(id="recommended", title="First suggestion", statement="For every n, P(n).")
    second = Problem(id="chosen", title="User's preference", statement="For every n, Q(n).",
                     difficulty_estimate="Promising: a finite recurrence may suffice.",
                     lean_feasibility="Likely finite-set induction; definitions need formalizing.")
    source.shortlist, source.problem = [first, second], first
    source.state, source.phase = State.COMPLETED, Phase.REPORT
    source.native.solver_session_id = "00000000-0000-0000-0000-000000000001"
    answer = "tasks/find-turn/answer.md"
    source.native.history = [{"role": "research", "answer": answer}]
    atomic_write(store.run_dir(source.id) / answer, "DISCOVERY_DERIVATION\n" + "x" * 20000)
    atomic_write(store.run_dir(source.id) / "workspace/notes.md", "FAILED_ROUTE_AND_USEFUL_LEMMA")
    atomic_write(store.run_dir(source.id) / "workspace/.lake/cache.txt", "DO_NOT_COPY_BUILD")
    atomic_write(store.run_dir(source.id) / "workspace/.env", "DO_NOT_COPY_SECRET")
    atomic_write(store.run_dir(source.id) / "workspace/auth.json", "DO_NOT_COPY_AUTH")
    atomic_write(store.run_dir(source.id) / "literature/snapshots/source.extracted.txt", "SOURCE_TEXT")
    store.save(source, "fixture_discovery")
    return engine, source, config


def test_nonrecommended_choice_carries_notes_in_a_separate_session(discovery, store):
    engine, source, config = discovery
    second = source.shortlist[1]
    run = engine.solve_discovered(config, source.id, second.id, problem_fingerprint(second))
    assert run.problem == second and run.shortlist == []
    assert run.native.solver_session_id is None
    assert store.load(source.id).problem == source.shortlist[0]
    context = run.discovery_context
    assert context.source_run_id == source.id
    files = {item.path for item in context.files}
    assert {"dossier.json", "workspace/notes.md", "tasks/find-turn/answer.md"} <= files
    assert not any(".env" in p or ".lake" in p or "auth.json" in p for p in files)
    runner = NativeRunner(engine)
    prompt = runner.prepare(run, config)
    assert "user explicitly chose" in prompt and "discovery-context/" in prompt
    assert "For every n, Q(n)." in prompt
    workspace = runner.workspace(run)
    assert len((workspace / "discovery-context/tasks/find-turn/answer.md").read_text()) > 16000
    assert "FAILED_ROUTE" in (workspace / "discovery-context/workspace/notes.md").read_text()
    # Later edits in Find cannot change what the solver received.
    atomic_write(store.run_dir(source.id) / "workspace/notes.md", "CHANGED_FIND")
    runner.prepare(run, config)
    assert "CHANGED_FIND" not in (workspace / "discovery-context/workspace/notes.md").read_text()


def test_global_problem_catalog_does_not_override_selected_find_snapshot(discovery, store):
    engine, source, config = discovery
    selected = source.shortlist[1]
    store.save_problem(selected.model_copy(update={"statement": "Different later statement"}))
    run = engine.solve_discovered(config, source.id, selected.id)
    assert run.problem.statement == selected.statement


def test_legacy_discovery_fingerprint_survives_new_optional_evidence_fields(discovery):
    engine, source, config = discovery
    legacy = source.shortlist[1].model_dump(mode="json")
    legacy["literature_search"].pop("limitations")
    legacy["evidence_assessment"].pop("limitations")
    previous_hash = digest(json_text(legacy))
    assert problem_fingerprint(Problem.model_validate(legacy)) == previous_hash
    run = engine.solve_discovered(config, source.id, "chosen", previous_hash)
    run.discovery_context.problem_sha256 = previous_hash
    assert "user explicitly chose" in NativeRunner(engine).prepare(run, config)


@pytest.mark.parametrize("field", ["literature_search", "evidence_assessment"])
def test_new_search_limits_are_bound_into_frozen_discovery(discovery, field):
    engine, source, config = discovery
    run = engine.solve_discovered(config, source.id, "chosen")
    getattr(run.problem, field).limitations = ["Only one database was searched."]
    with pytest.raises(ValueError, match="no longer matches"):
        NativeRunner(engine).prepare(run, config)


@pytest.mark.parametrize("problem_id,sha,error", [
    ("absent", None, "not in"), ("chosen", "f" * 64, "changed"),
])
def test_stale_or_outside_choice_creates_no_run(discovery, store, problem_id, sha, error):
    engine, source, config = discovery
    before = len(store.list_runs())
    with pytest.raises(ValueError, match=error):
        engine.solve_discovered(config, source.id, problem_id, sha)
    assert len(store.list_runs()) == before


def test_running_source_cannot_be_copied(discovery, store):
    engine, source, config = discovery
    source.active_since = source.created_at
    store.save(source, "fixture_running")
    with pytest.raises(ValueError, match="finish or pause"):
        engine.solve_discovered(config, source.id, "chosen")


def test_context_limits_and_symlinks_are_explicit(discovery, store):
    engine, source, config = discovery
    root = store.run_dir(source.id)
    outside = store.root / "outside.txt"
    outside.write_text("NOT_DISCOVERY_DATA")
    (root / "workspace/linked.txt").symlink_to(outside)
    config.discovery.context_max_file_bytes = 10000
    run = engine.solve_discovered(config, source.id, "chosen")
    assert any("answer.md" in entry for entry in run.discovery_context.omitted)
    assert any("linked.txt" in entry for entry in run.discovery_context.omitted)
    assert not any(f.path.endswith("linked.txt") for f in run.discovery_context.files)


def test_tampered_frozen_context_blocks_silent_changes(discovery, store):
    engine, source, config = discovery
    run = engine.solve_discovered(config, source.id, "chosen")
    atomic_write(store.run_dir(run.id) / "discovery-context/workspace/notes.md", "tampered")
    with pytest.raises(ValueError, match="modified"):
        NativeRunner(engine).prepare(run, config)


def test_context_projection_rejects_symlink_destination(discovery, store):
    engine, source, config = discovery
    run = engine.solve_discovered(config, source.id, "chosen")
    root = store.run_dir(run.id) / "workspace"
    root.mkdir(exist_ok=True)
    destination = store.root / "outside"
    destination.mkdir()
    (root / "discovery-context").symlink_to(destination, target_is_directory=True)
    with pytest.raises((OSError, ValueError)):
        NativeRunner(engine).prepare(run, config)
    assert not list(destination.iterdir())


def test_chat_receives_text_and_explicit_binary_omissions(discovery, store):
    engine, source, config = discovery
    atomic_write(store.run_dir(source.id) / "workspace/paper.pdf", "%PDF-test")
    config.backend.mode = "chat"
    run = engine.solve_discovered(config, source.id, "chosen")
    prompt = NativeRunner(engine).prepare(run, config)
    assert "DISCOVERY_DERIVATION" in prompt and "FAILED_ROUTE_AND_USEFUL_LEMMA" in prompt
    assert "workspace/paper.pdf: not sent inline" in prompt


def test_reviewer_does_not_receive_discovery_notes(discovery):
    engine, source, config = discovery
    run = engine.solve_discovered(config, source.id, "chosen")
    from mathlottery.models import CandidateInput

    engine.candidates.add(run, CandidateInput(claim=run.problem.statement, proof="Submitted proof"))
    run.phase = Phase.VERIFY
    runner = NativeRunner(engine)
    prompt = runner.prepare(run, config)
    assert "DISCOVERY_DERIVATION" not in prompt and "frozen discovery dossier" not in prompt
    assert not (runner.workspace(run) / "discovery-context").exists()


def test_snapshot_manifest_is_recoverable_from_checkpoint(discovery, store):
    engine, source, config = discovery
    run = engine.solve_discovered(config, source.id, "chosen")
    restored = store.load(run.id)
    manifest = json.loads((store.run_dir(run.id) / "discovery-context/manifest.json").read_text())
    assert restored.discovery_context.model_dump(mode="json") == manifest
    NativeRunner(engine).prepare(restored, config)
