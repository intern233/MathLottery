"""Proof archive, collaboration and curation invariants; no paid model calls."""

import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

import pytest
from test_solve_campaign import CampaignBackend, setup, theorem
from test_web import serving

from mathlottery.models import SolveWorker, State
from mathlottery.solve.board import Message, SolveBoard
from mathlottery.solve.board_tools import BoardTools
from mathlottery.solve.bulletin import events, navigation
from mathlottery.solve.bulletin.contracts import BoardEvent, Curation
from mathlottery.solve.bulletin.curation import suggestions
from mathlottery.solve.contracts import BoardReview
from mathlottery.storage.core import atomic_write, json_text
from mathlottery.web.service import WebService


@pytest.fixture
def bulletin(store):
    engine, run = setup(store, CampaignBackend())
    workspace = store.run_dir(run.id) / "workspace"
    workspace.mkdir(exist_ok=True)
    return engine, run, SolveBoard(store, run.id), workspace


def publish(board, workspace, actor="a", identifier="lemma", **kwargs):
    board.publish(actor, "algebra", Message(id=identifier, kind="result", title=identifier,
                  body="Long derivation not in compact context", theorem=theorem(), **kwargs), workspace)
    return f"{actor}:{identifier}"


def curate(board, keys, *, action="archive", task="review"):
    snapshot = {m["key"]: m["content_sha256"] for m in board.messages()}
    return board.curate([Curation(key=k, content_sha256=snapshot[k], action=action,
                                 reason="An exact-version visibility decision") for k in keys],
                        task, snapshot_hashes=snapshot)


def test_compact_graph_preserves_proof_archive_and_exact_assumptions(bulletin):
    _, _, board, workspace = bulletin
    a = publish(board, workspace, assumptions=["n is natural"])
    b = publish(board, workspace, "b", "consequence", depends_on=[a])
    board.project(workspace)
    graph = json.loads((workspace / "bulletin/graph.json").read_text())
    assert graph["nodes"][0]["assumptions"] == ["n is natural"]
    assert graph["nodes"][0]["statement"] == theorem()["statement"]
    assert "Long derivation" not in json_text(graph) and "justification" not in json_text(graph)
    assert graph["edges"][0]["from"] == a and graph["edges"][0]["to"] == b
    archived = json.loads((workspace / graph["edges"][0]["proof_path"]).read_text())
    assert archived["theorem"]["proof_steps"][0]["justification"]
    assert {v["key"] for v in navigation.explore(board.cards(), b, "premises", 1)["nodes"]} == {a, b}


def test_archive_restore_never_changes_hash_proof_or_acceptance(bulletin):
    _, run, board, workspace = bulletin
    atomic_write(workspace / "proof.md", "Frozen proof source")
    key = publish(board, workspace, artifacts=["proof.md"])
    before = board.read(key)
    board.review(BoardReview(key=key, content_sha256=before["content_sha256"], verdict="accepted",
                             rationale="Definition checked", checked_steps=["definition"]),
                 "opinion", snapshot_hashes={key: before["content_sha256"]})
    curate(board, [key])
    assert not board.graph()["nodes"]
    assert not navigation.search(board.cards(), "lemma")["messages"]
    assert navigation.search(board.cards(), "lemma", include_archived=True)["messages"][0]["archived"]
    board.project(workspace)
    record = board.read(key)
    assert record["content_sha256"] == before["content_sha256"]
    assert record["standing"] == "supervisor_accepted"
    assert board.material(before["artifacts"][0]["sha256"]) == b"Frozen proof source"
    # Replay cannot change an exact decision, and restore is an additional event.
    curate(board, [key])
    assert len(events.rows(board, "solve_board_curation")) == 1
    curate(board, [key], action="restore", task="restore")
    assert board.graph()["nodes"][0]["key"] == key
    assert board.read(key)["content_sha256"] == before["content_sha256"]
    assert len(events.rows(SolveBoard(board.store, run.id), "solve_board_curation")) == 2


def test_curation_guards_dependencies_live_focus_and_unresolved_objections(bulletin):
    _, run, board, workspace = bulletin
    a = publish(board, workspace)
    b = publish(board, workspace, "b", "dependent", depends_on=[a])
    with pytest.raises(ValueError, match="prerequisite"):
        curate(board, [a])
    assert not board.read(a)["archived"]
    board.publish("b", "algebra", Message(id="gap", kind="objection", title="Boundary",
                  body="Check zero", target=b), workspace)
    with pytest.raises(ValueError, match="objection"):
        curate(board, [a, b, "b:gap"])
    free = publish(board, workspace, "c", "focus")
    run.state = State.SOLVING
    run.native.solve_team.workers["c"] = SolveWorker(id="c", group="algebra", objective="Check focus", mode="peer")
    run.native.solve_team.active_attempts = [{"worker_id": "c", "task_id": "turn-c", "group": "algebra", "role": "research"}]
    board.store.save(run, "fixture")
    board.event("c", "algebra", BoardEvent(id="current", action="activity", summary="Using lemma", focus=[free]), task_id="turn-c")
    with pytest.raises(ValueError, match="current focus"):
        curate(board, [free])
    # Reading/replay never changes a content hash, and a stale snapshot is rejected.
    original = board.read(free)["content_sha256"]
    board.event("c", "algebra", BoardEvent(id="read", action="read", focus=[free]), task_id="turn-c")
    assert board.read(free)["content_sha256"] == original
    with pytest.raises(ValueError, match="exact version"):
        board.curate([Curation(key=free, content_sha256="0" * 64, action="archive", reason="wrong")],
                     "wrong", snapshot_hashes={free: original})


def test_archived_premise_stays_reachable_and_retraction_propagates(bulletin):
    _, _, board, workspace = bulletin
    a = publish(board, workspace)
    curate(board, [a])
    b = publish(board, workspace, "b", "later", depends_on=[a])
    assert {n["key"] for n in board.graph()["nodes"]} == {a, b}
    board.publish("a", "algebra", Message(id="retract", kind="retraction", title="Withdraw",
                  body="Missing case", target=a), workspace)
    assert board.read(a)["standing"] == "retracted"
    assert board.read(b)["standing"] == "needs_recheck"


def test_channels_are_opt_in_durable_and_concurrent(bulletin):
    _, run, board, _ = bulletin
    opening = BoardEvent(id="open", action="channel_open", summary="Compare approaches", invitees=["b"])
    assert board.event("a", "algebra", opening)
    assert not board.event("a", "algebra", opening)
    channel = events.channels(events.rows(board))[0]
    assert channel["members"] == ["a"]  # Invitation is not consent to join.
    with pytest.raises(ValueError, match="Join"):
        board.event("b", "analysis", BoardEvent(id="early", action="channel_message", channel="a:open", body="hello"))
    board.event("b", "analysis", BoardEvent(id="join", action="channel_join", channel="a:open"))

    def post(i):
        fresh = SolveBoard(board.store, run.id)
        return fresh.event("b", "analysis", BoardEvent(id=f"message-{i}", action="channel_message",
                                                       channel="a:open", body=f"Check case {i}"))
    with ThreadPoolExecutor(max_workers=4) as pool:
        assert all(pool.map(post, range(12)))
    assert len(events.channels(events.rows(board))[0]["events"]) == 14
    with pytest.raises(ValueError, match="creator"):
        board.event("b", "analysis", BoardEvent(id="close", action="channel_close", channel="a:open"))
    board.event("a", "algebra", BoardEvent(id="close", action="channel_close", channel="a:open"))
    with pytest.raises(ValueError, match="No open"):
        post(13)
    with pytest.raises(ValueError, match="immutable"):
        board.event("a", "algebra", opening.model_copy(update={"summary": "Overwritten"}))


def test_registry_marks_old_reports_without_changing_runtime(bulletin):
    _, run, board, _ = bulletin
    run.state = State.SOLVING
    run.native.solve_team.workers["a"] = SolveWorker(id="a", group="g", mode="peer", objective="Assigned direction")
    run.native.solve_team.active_attempts = [{"worker_id": "a", "task_id": "new", "role": "research", "group": "g"}]
    board.store.save(run, "fixture")
    board.event("a", "g", BoardEvent(id="old", action="activity", summary="Earlier work", status="blocked"), task_id="old")
    agent = board.collaboration()["agents"][0]
    assert agent["runtime_status"] == "running" and not agent["report_current"]
    board.event("a", "g", BoardEvent(id="new", action="activity", summary="Current work",
                                      body="An optional long derivation belongs in archives"), task_id="new")
    current = board.collaboration()["agents"][0]
    assert current["report_current"] and "body" not in current["report"]
    run.state = State.PAUSED
    board.store.save(run, "fixture")
    assert not board.collaboration()["agents"][0]["report_current"]
    run.native.solve_team.active_attempts = []
    run.native.solve_team.workers["a"].state = "running"
    board.store.save(run, "stale_fixture")
    assert board.collaboration()["agents"][0]["runtime_status"] != "running"


def test_native_helper_reads_archives_and_submits_identity_bound_events(bulletin):
    _, _, board, workspace = bulletin
    (workspace / "proof.md").write_bytes(b"Statement\r\nProof\r\n")
    key = publish(board, workspace, artifacts=["proof.md"])
    curate(board, [key])
    board.project(workspace)

    def client(*args):
        completed = subprocess.run([sys.executable, str(workspace / "board_client.py"), *args],
                                   cwd=workspace.parent, capture_output=True, text=True, check=True)
        return json.loads(completed.stdout)
    assert client("search", "lemma")["total"] == 0
    assert client("search", "lemma", "--archived")["total"] == 1
    assert client("read", key)["theorem"]["conclusion_step"] == "definition"
    client("event", json.dumps({"id": "work", "action": "activity", "summary": "Checking old lemma", "focus": [key]}))
    changed, errors = board.ingest_events("actual-worker", "group", workspace, task_id="current")
    assert changed and not errors
    assert board.read(key)["usage"]["recorded_reads"] == 1
    assert {e["actor"] for e in events.rows(board)} == {"actual-worker"}
    assert not board.ingest_events("actual-worker", "group", workspace, task_id="current")[0]
    sha = board.read(key)["artifacts"][0]["sha256"]
    assert client("material", sha)["text"] == "Statement\r\nProof\r\n"
    (workspace / f"bulletin/materials/{sha}.txt").write_text("Changed proof")
    tampered = subprocess.run([sys.executable, str(workspace / "board_client.py"), "material", sha],
                              capture_output=True, text=True)
    assert tampered.returncode == 1 and "frozen hash" in tampered.stderr
    spoof = {"id": "spoof", "action": "activity", "summary": "false", "actor": "supervisor"}
    rejected = subprocess.run([sys.executable, str(workspace / "board_client.py"), "event", json.dumps(spoof)],
                              capture_output=True, text=True)
    assert rejected.returncode == 1 and "unknown field" in rejected.stderr
    # Bypassing the helper must still fail the authoritative controller validation.
    atomic_write(workspace / "outbox-events/spoof.json", json_text(spoof))
    assert board.ingest_events("actual-worker", "group", workspace, task_id="current")[1]


def test_hosted_tools_support_same_graph_and_cooperation(bulletin):
    _, _, board, workspace = bulletin
    key = publish(board, workspace)
    bridge = BoardTools(board, "hosted", "g", workspace, task_id="turn")
    assert bridge.execute("solve_board_explore", {"key": key, "depth": 1})["nodes"][0]["key"] == key
    assert bridge.execute("solve_board_read", {"key": key})["theorem"]["proof_steps"]
    bridge.execute("solve_board_event", {"event_json": json.dumps({"id": "open", "action": "channel_open", "summary": "Need a bound"})})
    assert bridge.execute("solve_board_channel", {"key": "hosted:open"})["members"] == ["hosted"]
    assert bridge.execute("solve_board_activity", {})["channels"][0]["purpose"] == "Need a bound"
    with pytest.raises(ValueError):
        bridge.execute("solve_board_event", {"event_json": json.dumps({"id": "bad", "action": "archive", "summary": "not authorized"})})


def test_browser_metadata_is_compact_and_archive_endpoints_are_run_scoped(bulletin):
    engine, run, board, workspace = bulletin
    key = publish(board, workspace)
    curate(board, [key])
    board.event("a", "g", BoardEvent(id="open", action="channel_open", summary="Discussion"))
    _, other = setup(board.store, CampaignBackend())
    with serving(WebService(board.store.root)) as (client, _):
        value = client.get(f"/api/runs/{run.id}").json()["solve_team"]
        assert "body" not in value["messages"][0] and value["messages"][0]["archived"]
        for action, reference in [("solve-message", key), ("solve-channel", "a:open")]:
            assert client.get(f"/api/runs/{run.id}/{action}", params={"key": reference}).status_code == 200
            assert client.get(f"/api/runs/{other.id}/{action}", params={"key": reference}).status_code == 400
            assert client.get(f"/api/runs/{run.id}/{action}", params={"key": "../../private"}).status_code == 400


def test_two_native_researchers_coordinate_without_extra_agents(store):
    def research(backend, author, workspace, kwargs, turn):
        action = {"id": "open", "action": "channel_open", "summary": "Check addition boundaries"} if author == "primary" else {
            "id": "join", "action": "channel_join", "channel": "primary:open"}
        if author != "primary":
            deadline = time.monotonic() + 8
            while time.monotonic() < deadline:
                index = json.loads((workspace / "bulletin/collaboration/index.json").read_text())
                if index["channels"]:
                    break
                time.sleep(.02)
            assert index["channels"]
        def emit(event):
            subprocess.run([sys.executable, str(workspace / "board_client.py"), "event", json.dumps(event)],
                           check=True, capture_output=True)
        emit(action)
        emit({"id": "progress", "action": "activity", "summary": "Working on base case", "status": "working"})
        if author != "primary":
            emit({"id": "answer", "action": "channel_message", "channel": "primary:open", "body": "n=0 also reduces by definition"})

    engine, created = setup(store, CampaignBackend(research=research, agents=2), parallel=2)
    result = engine.drive(created.id)
    assert result.state == State.COMPLETED
    board = SolveBoard(store, result.id)
    channel = events.channels(events.rows(board))[0]
    assert len(channel["members"]) == 2
    assert any(e["body"] == "n=0 also reduces by definition" for e in channel["events"])
    assert len(result.native.solve_team.workers) == 2
    assert not result.native.solve_team.active_attempts
    assert all(not a["report_current"] for a in board.collaboration()["agents"])


def test_low_usage_is_advisory_not_automatic_deletion(bulletin, monkeypatch):
    _, _, board, workspace = bulletin
    key = publish(board, workspace)
    assert "NOT mean unused" in suggestions(board)["note"]
    assert not board.read(key)["archived"]
    assert key not in {v["key"] for v in suggestions(board)["candidates"]}  # New and unreviewed.
    version = board.read(key)["content_sha256"]
    board.review(BoardReview(key=key, content_sha256=version, verdict="needs_work",
                             rationale="Keep the idea, proof still needs inspection"),
                 "review", snapshot_hashes={key: version})

    class Later(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime.now(tz) + timedelta(minutes=11)

    monkeypatch.setattr("mathlottery.solve.bulletin.curation.datetime", Later)
    assert [v["key"] for v in suggestions(board)["candidates"]] == [key]
    assert not board.read(key)["archived"]
    board.event("b", "g", BoardEvent(id="read", action="read", focus=[key]))
    assert not suggestions(board)["candidates"]


def test_supervisor_curation_checkpoint_and_race_feedback_do_not_abort_research(store):
    def supervise(backend, payload, context, kwargs):
        if not context["signals"]:
            note = next(n for n in context["board"]["nodes"] if n["key"] == "prior:note")
            payload["board_curation"] = [{"key": note["key"], "content_sha256": note["content_sha256"],
                                          "action": "archive", "reason": "Old scratch note"}]
    backend = CampaignBackend(supervision=supervise)
    engine, created = setup(store, backend)
    board = SolveBoard(store, created.id)
    workspace = store.run_dir(created.id) / "workspace"
    workspace.mkdir(exist_ok=True)
    board.publish("prior", "g", Message(id="note", kind="intent", title="Old scratch note", body="No result"), workspace)
    result = engine.drive(created.id)
    assert result.state == State.COMPLETED and board.read("prior:note")["archived"]
    assert events.rows(board, "solve_board_curation")[0]["actor"] == "supervisor"

    def invalid(backend, payload, context, kwargs):
        payload["board_curation"] = [{"key": "missing:note", "content_sha256": "0" * 64,
                                      "action": "archive", "reason": "Invalid stale reference"}]
    engine, created = setup(store, CampaignBackend(supervision=invalid))
    result = engine.drive(created.id)
    assert result.state == State.COMPLETED
    assert "exact version" in result.native.solve_team.campaign.decisions[-1]["curation_error"]


def test_event_ingestion_rejects_workspace_escape(bulletin, tmp_path):
    _, _, board, workspace = bulletin
    outside = tmp_path / "external.json"
    outside.write_text(json_text({"id": "outside", "action": "activity", "summary": "Not from workspace"}))
    (workspace / "outbox-events").mkdir()
    (workspace / "outbox-events/escape.json").symlink_to(outside)
    changed, errors = board.ingest_events("a", "g", workspace)
    assert not changed and errors and not events.rows(board)
