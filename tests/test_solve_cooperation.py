"""Voluntary research, reliable messages and bounded continuation; no model billing."""

import json
import subprocess
import sys
import threading
import time

import pytest
from test_solve_campaign import CampaignBackend, setup

from mathlottery.models import SolveWorker, State
from mathlottery.solve.board import Message, SolveBoard
from mathlottery.solve.board_tools import BoardTools
from mathlottery.solve.bulletin import events, inbox, navigation
from mathlottery.solve.bulletin.contracts import BoardEvent
from mathlottery.solve.supervision_prompts import publication_feedback
from mathlottery.storage.core import atomic_write, json_text


@pytest.fixture
def shared(store):
    _, run = setup(store, CampaignBackend(), parallel=2)
    workspace = store.run_dir(run.id) / "workspace"
    workspace.mkdir(exist_ok=True)
    return run, SolveBoard(store, run.id), workspace


def event(board, actor, identifier, action, **kwargs):
    return board.event(actor, "research", BoardEvent(id=identifier, action=action, **kwargs),
                       task_id=f"task-{actor}")


def test_invitation_response_and_exact_read_receipt_survive_replay(shared):
    run, board, workspace = shared
    event(board, "a", "bounds", "channel_open", summary="Compare endpoint bounds", invitees=["b"])
    channel = "a:bounds"
    assert inbox.view(board, "b")["invitations"][0]["status"] == "pending"
    bridge = BoardTools(board, "b", "research", workspace)
    bridge.execute("solve_board_channel", {"key": channel})
    assert not inbox.view(board, "b")["unread_channels"]
    assert inbox.view(board, "b")["invitations"]  # A read is not a join or acceptance.
    event(board, "a", "later", "channel_message", channel=channel, body="New estimate")
    event(board, "b", "old-read", "channel_ack", channel=channel, through_event="a:bounds")
    assert inbox.view(board, "b")["unread_channels"][0]["count"] == 1
    with pytest.raises(ValueError, match="observed event"):
        event(board, "b", "future", "channel_ack", channel=channel, through_event="a:future")
    event(board, "b", "defer", "channel_defer", channel=channel, summary="Finishing a calculation")
    assert inbox.view(board, "b")["invitations"][0]["status"] == "deferred"
    event(board, "b", "decline", "channel_decline", channel=channel, summary="A different approach is useful")
    assert not inbox.view(board, "b")["invitations"]
    assert not inbox.view(board, "b")["unread_channels"]
    event(board, "b", "join", "channel_join", channel=channel)
    assert not event(SolveBoard(board.store, run.id), "b", "join", "channel_join", channel=channel)
    assert "b" in events.channels(events.rows(board))[0]["members"]
    with pytest.raises(ValueError, match="non-member"):
        event(board, "b", "bad-decline", "channel_decline", channel=channel, summary="Cannot decline after joining")
    # A read queued just before closure can still be acknowledged afterwards.
    event(board, "a", "close", "channel_close", channel=channel)
    assert event(board, "b", "late-ack", "channel_ack", channel=channel, through_event="a:later")
    with pytest.raises(ValueError, match="No open channel"):
        event(board, "b", "late-post", "channel_message", channel=channel, body="Cannot post after closure")


@pytest.mark.parametrize("topic", ["endpoint bound", "边界估计"])
def test_work_declarations_warn_without_locking_and_expire_with_attempt(shared, topic):
    run, board, _ = shared
    run.state = State.SOLVING
    for actor in ("a", "b"):
        run.native.solve_team.workers[actor] = SolveWorker(id=actor, group="research", mode="peer",
                                                          objective="Optional idea", state="running")
        run.native.solve_team.active_attempts.append({"worker_id": actor, "task_id": f"task-{actor}",
                                                       "workspace": f"solve-workspaces/{actor}"})
    board.store.save(run, "running")
    event(board, "a", "work", "activity", summary="Derive an injection", topic=topic,
          approach="Combinatorial injection")
    event(board, "b", "work", "activity", summary="Enumerate cases", topic=topic,
          approach="Exact enumeration", intent="check", overlap_reason="Independent check of edge cases")
    mine = inbox.view(board, "b")
    assert mine["possible_overlaps"][0]["actor"] == "a"
    event(board, "a", "channel", "channel_open", summary=f"{topic} Enumerate cases")
    assert inbox.view(board, "b")["related_channels"][0]["channel"] == "a:channel"
    assert len(events.registry(board)) == 2
    run.native.solve_team.active_attempts = [a for a in run.native.solve_team.active_attempts if a["worker_id"] != "a"]
    run.native.solve_team.workers["a"].state = "completed"
    board.store.save(run, "returned")
    assert not inbox.view(board, "b")["possible_overlaps"]
    assert next(a for a in events.registry(board) if a["actor"] == "a")["report"]["topic"] == topic


def test_tags_aliases_and_punctuation_help_retrieval_without_merging_claims(shared):
    _, board, workspace = shared
    for actor in ("a", "b"):
        board.publish(actor, "research", Message(id="bound", kind="result", title="Endpoint calculation",
                      body="Not yet a proof", tags=["q-binomial"], aliases=["Gaussian polynomial", "高斯多项式"]), workspace)
    assert len(navigation.search(board.cards(), "Gaussian-polynomial")["messages"]) == 2
    assert len(navigation.search(board.cards(), "高斯多项式")["messages"]) == 2
    assert all(m["standing"] == "unverified" for m in board.messages())
    assert "not mathematical equivalence" in navigation.search(board.cards(), "bound")["search_scope"]


def test_native_preflight_and_controller_rejection_receipts(shared):
    run, board, workspace = shared
    board.project(workspace)
    helper = workspace / "board_client.py"
    draft = workspace / "draft.json"
    atomic_write(draft, json_text({"summary": "Missing envelope", "body": "Preserve this derivation"}))

    def invoke(action):
        return subprocess.run([sys.executable, str(helper), action, "draft.json"],
                              cwd=workspace, capture_output=True, text=True, timeout=10)

    bad = invoke("publish")
    assert bad.returncode == 1 and "input.id: required" in bad.stderr
    assert not list((workspace / "outbox").glob("*.json"))
    good = {"id": "note", "kind": "intent", "title": "My route", "body": "Preserve this derivation"}
    atomic_write(draft, json_text(good))
    assert json.loads(invoke("validate").stdout)["queued"] is False
    assert json.loads(invoke("publish").stdout)["queued"] is True
    changed, errors = board.ingest("primary", "research", workspace)
    assert changed and not errors
    receipts = json.loads((workspace / "bulletin/publications.json").read_text())
    assert next(iter(receipts.values()))["key"] == "primary:note"
    atomic_write(workspace / "outbox/broken.json", json_text({"summary": "Wrong envelope"}))
    board.ingest("primary", "research", workspace)
    rejected = publication_feedback(run, board)
    assert rejected[0]["status"] == "rejected" and "validate" in rejected[0]["hint"]
    assert len(board.messages()) == 1
    # Correcting an unpublished envelope is safe; published content remains immutable.
    atomic_write(workspace / "outbox/broken.json", json_text({**good, "id": "fixed"}))
    _, errors = SolveBoard(board.store, run.id).ingest("primary", "research", workspace)
    assert not errors and not publication_feedback(run, board)
    atomic_write(workspace / "outbox/broken.json", json_text({**good, "id": "fixed", "body": "Changed proof"}))
    _, errors = board.ingest("primary", "research", workspace)
    assert any("immutable" in e for e in errors)


def test_old_event_receipts_remain_replayable_with_new_optional_fields(shared):
    _, board, _ = shared
    value = BoardEvent(id="old", action="activity", summary="An old work declaration")
    board.event("a", "research", value)
    with board.store.connect() as db:
        old = events.rows(board, db=db)[0]
        for key in ("topic", "approach", "intent", "overlap_reason", "through_event"):
            old.pop(key)
        db.execute("UPDATE solve_board_events SET data=? WHERE run_id=? AND key=?",
                   (json_text(old), board.run_id, "a:old"))
    assert not board.event("a", "research", value)
    assert events.registry(board)[0]["report"]["topic"] == ""


def test_peer_continues_while_primary_occupies_supervisor_slot(store):
    from collections import Counter

    resumed = threading.Event()
    counts = Counter()

    def research(backend, author, workspace, kwargs, turn):
        counts[author] += 1
        if author == "primary" and counts[author] == 1:
            assert resumed.wait(5), "An idle peer should not wait for the shared supervisor slot"
        elif author != "primary" and counts[author] == 2:
            assert not any(c["author"] == "supervisor" and "Purpose: review" in c["prompt"] for c in backend.calls)
            resumed.set()

    backend = CampaignBackend(agents=2, complete=False, research=research)
    engine, created = setup(store, backend, parallel=2, calls=7)
    run = engine.drive(created.id)
    assert run.state == State.COMPLETED, run.last_error
    assert resumed.is_set() and run.iteration <= 7
    continued = [h for h in run.native.history if h.get("dispatch_reason") == "autonomous_continuation_while_review_pending"]
    assert continued
    assert all(h["worker_id"] != "primary" for h in continued[:1])
    assert "Optional group suggestion (not a compulsory route)" in next(c["prompt"] for c in backend.calls if c["author"] != "supervisor")
    peer_calls = [c for c in backend.calls if c["author"] not in {"primary", "supervisor"}]
    assert peer_calls[1]["session"] == "session-" + peer_calls[1]["author"]


def test_one_continuation_limit_prevents_unreviewed_spin(store):
    from mathlottery.config import Config
    from mathlottery.models import SolveGroup
    from mathlottery.solve.dispatch import queue_continuations

    _, run = setup(store, CampaignBackend(), parallel=2)
    team = run.native.solve_team
    team.groups = [SolveGroup(id="research", agents=2, objective="Any useful approach")]
    team.workers["research-2"] = SolveWorker(id="research-2", group="research", mode="peer",
                                              objective="Suggestion", state="completed")
    team.campaign.decisions = [{"summary": "Initial capacity plan"}]
    signal = {"task_id": "first", "worker_id": "research-2", "status": "partial"}
    team.campaign.signals = [signal]
    queue_continuations(run, Config.model_validate(run.config))
    assert team.campaign.dispatch == ["research-2"]
    team.campaign.dispatch = []
    team.campaign.signals.append({**signal, "task_id": "second"})
    queue_continuations(run, Config.model_validate(run.config))
    assert not team.campaign.dispatch


def test_native_publication_rejection_refreshes_inbox_during_attempt(store):
    def research(backend, author, workspace, kwargs, turn):
        atomic_write(workspace / "outbox/bad.json", json_text({"summary": "Incomplete envelope"}))
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            personal = json.loads((workspace / "bulletin/inbox.json").read_text())
            if personal.get("publication_rejections"):
                assert personal["publication_rejections"][0]["file"] == "bad.json"
                return
            time.sleep(.02)
        pytest.fail("Publication errors must become visible without another successful publication")

    backend = CampaignBackend(research=research)
    engine, created = setup(store, backend)
    run = engine.drive(created.id)
    assert run.state == State.COMPLETED, run.last_error
    context = json.loads((backend.calls[-1]["workspace"] / "supervision-context.json").read_text())
    assert context["publication_feedback"][0]["status"] == "rejected"


def test_five_scripted_agents_share_results_and_decline_invitations(store):
    """An integrated scheduler exercise, not evidence of LLM research performance."""
    from test_solve_campaign import theorem

    ready = threading.Event()
    joined = threading.Barrier(5)
    root_id = None

    def research(backend, author, workspace, kwargs, turn):
        board = SolveBoard(store, root_id)
        saved = store.load(root_id)
        attempt = next(a for a in saved.native.solve_team.active_attempts if a["worker_id"] == author)
        bridge = BoardTools(board, author, "algebra", workspace, task_id=attempt["task_id"])
        def send(identifier, action, **values):
            return bridge.execute("solve_board_event", {"event_json": json.dumps({"id": identifier, "action": action, **values})})
        send("work", "activity", summary="Investigate addition identity", topic="addition identity",
             approach="Definition" if author == "primary" else "Boundary checks", intent="check")
        if author == "primary":
            bridge.execute("solve_board_publish", {"message_json": json.dumps({
                "id": "base", "kind": "result", "title": "Defining equation", "body": "Exact local lemma", "theorem": theorem()})})
            send("invite", "channel_open", summary="Compare boundary checks", invitees=[f"algebra-{i}" for i in range(2, 6)])
            ready.set()
        else:
            assert ready.wait(8)
            assert bridge.execute("solve_board_inbox", {})["invitations"]
            if author == "algebra-5":
                send("decline", "channel_decline", channel="primary:invite", summary="Independent check first")
            else:
                send("join", "channel_join", channel="primary:invite")
                bridge.execute("solve_board_read", {"key": "primary:base"})
                send("reply", "channel_message", channel="primary:invite", body="The defining equation also covers zero")
                bridge.execute("solve_board_publish", {"message_json": json.dumps({
                    "id": "reuse", "kind": "result", "title": "Reuse with scope checked", "body": "Inspect exact conditions",
                    "depends_on": ["primary:base"], "theorem": theorem()})})
        joined.wait(timeout=8)

    backend = CampaignBackend(agents=5, research=research)
    engine, created = setup(store, backend, parallel=5, calls=10)
    root_id = created.id
    run = engine.drive(created.id)
    assert run.state == State.COMPLETED, run.last_error
    board = SolveBoard(store, run.id)
    channel = events.channels(events.rows(board))[0]
    assert len(channel["members"]) == 4 and channel["responses"]["algebra-5"] == "declined"
    assert len([m for m in board.messages() if "primary:base" in m["depends_on"]]) == 3
    assert backend.research_turns == 5
    assert len(run.native.solve_team.workers) == 5
    assert not any(c.reviews for c in run.candidates)
