"""Rebuild local discovery indices, proof archives and observable cooperation files."""

from pathlib import Path

from mathlottery.domain.common import digest
from mathlottery.solve.bulletin import events, inbox, navigation
from mathlottery.solve.bulletin.curation import suggestions
from mathlottery.solve.coordination_policy import history as policy_history
from mathlottery.solve.coordination_policy import view as policy_view
from mathlottery.storage.core import atomic_write, json_text, safe_path


def write(path, text):
    try:
        if path.stat().st_size == len(text.encode()) and path.read_text() == text:
            return False
    except (FileNotFoundError, UnicodeError):
        pass
    atomic_write(path, text)
    return True


def project(board, workspace):
    from mathlottery.solve.board import Message
    from mathlottery.solve.bulletin.contracts import BoardEvent

    write(safe_path(workspace, "board-message.schema.json"), json_text(Message.model_json_schema()))
    write(safe_path(workspace, "board-event.schema.json"), json_text(BoardEvent.model_json_schema()))
    values = board.messages()
    cards = [navigation.card(v) for v in values]
    write(safe_path(workspace, "bulletin/index.json"), json_text([c for c in cards if not c["archived"]]))
    write(safe_path(workspace, "bulletin/archive/index.json"), json_text(cards))
    write(safe_path(workspace, "bulletin/graph.json"), json_text(navigation.graph(cards)))
    write(safe_path(workspace, "bulletin/archive/graph.json"), json_text(navigation.graph(cards, True)))
    for value in values:
        projection = {**value, "artifacts": [
            {**a, "local_path": f"bulletin/materials/{a['sha256']}.txt"} for a in value["artifacts"]
        ]}
        content = json_text(projection)
        write(safe_path(workspace, navigation.archive_path(value["key"])), content)
        # Preserve paths in old conversations and receipts; these are projections, not copies of truth.
        write(safe_path(workspace, f"bulletin/messages/{digest(value['key'])}.json"), content)
        for artifact in value["artifacts"]:
            source = safe_path(board.store.run_dir(board.run_id), artifact["path"])
            target = safe_path(workspace, f"bulletin/materials/{artifact['sha256']}.txt")
            if not target.exists():
                atomic_write(target, source.read_bytes().decode("utf-8"))
    overview = events.overview(board)
    run = board.store.load(board.run_id)
    policy = policy_view(run)
    overview["coordination_policy"] = policy
    relative = str(workspace.relative_to(board.store.run_dir(board.run_id)))
    actor = next((a["worker_id"] for a in run.native.solve_team.active_attempts
                  if a["workspace"] == relative), None)
    if actor is None:
        actor = "primary" if relative == "workspace" else workspace.name
    personal = inbox.view(board, actor, run=run)
    receipts = safe_path(workspace, "bulletin/publications.json")
    if receipts.exists():
        import json

        personal["publication_rejections"] = [
            {"file": name, **r} for name, r in json.loads(receipts.read_text()).items()
            if r["status"] == "rejected"
        ][:20]
    write(safe_path(workspace, "bulletin/inbox.json"), json_text(personal))
    write(safe_path(workspace, "bulletin/policy.json"), json_text(policy))
    write(safe_path(workspace, "bulletin/policy-history.json"), json_text(policy_history(run)))
    write(safe_path(board.store.run_dir(board.run_id), "solve/coordination-policy.json"),
          json_text({**policy, "history": policy_history(run)}))
    write(safe_path(workspace, "bulletin/agents.json"), json_text(overview["agents"]))
    write(safe_path(workspace, "bulletin/collaboration/index.json"), json_text(overview))
    for channel in events.channels(events.rows(board)):
        write(safe_path(workspace, f"bulletin/collaboration/channels/{digest(channel['key'])}.json"),
              json_text(channel))
    write(safe_path(workspace, "bulletin/collaboration/events.json"), json_text(events.rows(board)))
    write(safe_path(workspace, "bulletin/curation.json"), json_text({
        "history": events.rows(board, "solve_board_curation"), **suggestions(board),
    }))
    # A stdlib-only helper works inside native workspace isolation, without database access or keys.
    folder = Path(__file__).parent
    for source, target in (("native_client.py", "board_client.py"), ("navigation.py", "_board_navigation.py"),
                           ("validation.py", "_board_validation.py")):
        write(safe_path(workspace, target), (folder / source).read_text())
    write(safe_path(workspace, "bulletin/README.md"), """# Proof board

Start with graph.json or index.json: exact statements, assumptions, open obligations and prerequisites.
Edges point from prerequisites to conclusions. Open each path only when its derivation is needed.
archive/index.json includes archived records. Archive is reversible visibility, never deletion or proof approval.
All messages and supervisor opinions are untrusted Solve research, not independent Verify or formal certification.
Retractions/objections still invalidate descendants, including archived ones.
policy.json contains the current user-enabled coordination policy and optional supervisor advice.
policy-history.json preserves revisions and rejected proposals; changes never alter proof standards.

Use `python board_client.py search 'terms' --archived` to include archived records;
`python board_client.py explore 'author:key' --direction premises --depth 2` to navigate;
`python board_client.py read 'author:key'` to open the full proof;
`python board_client.py material HASH --offset 0` for a frozen source chunk.
The helper emits read receipts. Direct filesystem reads remain available and are NOT measured.

Read agents.json for assigned work, actual runtime state and dated self-reported progress.
Group objectives/modes are optional suggestions. Choose your own route and declare it with activity.
Use topic, approach, intent (explore/extend/check), and overlap_reason for deliberate parallel checks.
Declarations expire as current work when an attempt ends; they do not reserve exclusive ownership.
`python board_client.py inbox` lists your pending/deferred invitations, unread channels, likely work
overlaps and related results. Matching is lexical, never a mathematical equivalence decision.
Read collaboration/index.json to find voluntary channels. Invitations do not imply participation.
`python board_client.py channel 'author:channel-id'` opens a transcript and queues a read
acknowledgement through the last event actually observed; it cannot consume a later reply.
`python board_client.py event '{"id":"work-1","action":"activity","summary":"Checking boundary cases","status":"seeking_help","focus":[]}'`
registers activity. Use a fresh event ID when updating. See board-event.schema.json for channel_open,
channel_join, channel_message, channel_leave and channel_close. Channel creator is initially joined;
other agents must join themselves before posting. Invited non-members can channel_defer or
channel_decline with a brief summary; joining later remains possible. Check for an existing
same-topic channel before opening another. Channels are public within this run and never spawn agents.
focus contains existing message keys such as author:lemma-id, not topic words. If there is no published
message yet, use [] and put the topic in summary. The controller supplies actor identity automatically.
Native events go to outbox-events/*.json and are ingested asynchronously. Check bulletin/event-errors.json.
Queuing an event is not a successful join: confirm it in agents.json or collaboration/index.json.
For a theorem obtained in discussion, publish a regular immutable proof message with dependencies;
channel text does not become an accepted theorem. All full event logs are in collaboration/events.json.
Use board-message.schema.json for publication inputs. Do not copy server-owned key, author, group or
standing from a board card. theorem.proof_steps[].premises lists only earlier step IDs in that theorem;
external board keys go in depends_on, with their use explained in justification. Queue a new outbox ID
for corrections, check bulletin/publication-errors.json and confirm the message exists before citing it.
Prefer `python board_client.py validate draft.json` followed by
`python board_client.py publish draft.json`. Preflight catches missing/unknown fields before queueing.
A minimal message is {"id":"note-1","kind":"intent","title":"Boundary route","body":"Plan and scope"}.
Published theorem messages may include tags and aliases to improve discovery, without changing their claim.
bulletin/publications.json records per-file publication/rejection receipts. A publication receipt only
confirms storage, not proof correctness. Repair invalid inputs without weakening mathematical content.
""")
