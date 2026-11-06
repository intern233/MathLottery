"""Append-only run-local activity and opt-in channels; never dispatches agents."""

import json

from mathlottery.domain.common import now
from mathlottery.storage.core import json_text


def initialize(board):
    with board.store.connect() as db:
        for table in ("solve_board_events", "solve_board_curation"):
            db.execute(f"""CREATE TABLE IF NOT EXISTS {table} (
                seq INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL,
                key TEXT NOT NULL, data TEXT NOT NULL, UNIQUE(run_id,key))""")


def rows(board, table="solve_board_events", db=None):
    if db is None:
        with board.store.connect() as connection:
            return rows(board, table, connection)
    if table not in {"solve_board_events", "solve_board_curation"}:
        raise ValueError("Unknown board ledger")
    return [json.loads(row[0]) for row in db.execute(
        f"SELECT data FROM {table} WHERE run_id=? ORDER BY seq", (board.run_id,),
    )]


def channels(events):
    result = {}
    for event in events:
        action, actor = event["action"], event["actor"]
        if action == "channel_open":
            result[event["key"]] = {
                "key": event["key"], "creator": actor, "purpose": event["summary"],
                "invitees": event["invitees"], "members": [actor], "focus": event["focus"],
                "closed": False, "events": [event], "updated_at": event["time"],
                "responses": {actor: "joined"}, "read_through": {},
            }
        elif action.startswith("channel_") and event["channel"] in result:
            channel = result[event["channel"]]
            if action == "channel_join" and actor not in channel["members"]:
                channel["members"].append(actor)
            if action == "channel_join":
                channel["responses"][actor] = "joined"
            elif action == "channel_leave":
                channel["members"] = [m for m in channel["members"] if m != actor]
                channel["responses"][actor] = "left"
            elif action == "channel_close":
                channel["closed"] = True
            elif action in {"channel_defer", "channel_decline"}:
                channel["responses"][actor] = "deferred" if action == "channel_defer" else "declined"
            elif action == "channel_ack":
                keys = [e["key"] for e in channel["events"]]
                previous = channel["read_through"].get(actor)
                target = event["through_event"]
                if target in keys and (previous not in keys or keys.index(target) > keys.index(previous)):
                    channel["read_through"][actor] = target
            channel["events"].append(event)
            channel["updated_at"] = event["time"]
    return list(result.values())


def register(board, actor, group, event, *, task_id=None):
    payload = {**event.model_dump(mode="json"), "actor": actor, "group": group,
               "key": f"{actor}:{event.id}"}
    # The transaction serializes joins/leaves/messages and survives concurrent writers/replay.
    with board.store.connect() as db:
        db.execute("BEGIN IMMEDIATE")
        previous = db.execute("SELECT data FROM solve_board_events WHERE run_id=? AND key=?",
                              (board.run_id, payload["key"])).fetchone()
        if previous:
            old = json.loads(previous[0])
            defaults = {"topic": "", "approach": "", "intent": "explore",
                        "overlap_reason": "", "through_event": None}
            if any(old.get(k, defaults.get(k)) != value for k, value in payload.items()):
                raise ValueError("Board events are immutable; use a new ID")
            return False
        known = {row[0] for row in db.execute(
            "SELECT key FROM solve_messages WHERE run_id=?", (board.run_id,),
        )}
        if not set(event.focus) <= known:
            raise ValueError("Activity/read/channel references must exist in this run")
        if event.action.startswith("channel_") and event.action != "channel_open":
            channel = next((c for c in channels(rows(board, db=db)) if c["key"] == event.channel), None)
            if channel is None or (channel["closed"] and event.action != "channel_ack"):
                raise ValueError("No open channel with this key in this run")
            if event.action in {"channel_message", "channel_leave"} and actor not in channel["members"]:
                raise ValueError("Join a channel yourself before posting or leaving")
            if event.action == "channel_close" and actor != channel["creator"]:
                raise ValueError("Only the channel creator can close it")
            if event.action in {"channel_defer", "channel_decline"}:
                if actor not in channel["invitees"] or actor in channel["members"]:
                    raise ValueError("Only an invited non-member can defer or decline; members can leave")
            if event.action == "channel_ack" and event.through_event not in {
                e["key"] for e in channel["events"]
            }:
                raise ValueError("Acknowledge an observed event in this channel, not a future event")
        payload.update(task_id=task_id, time=now())
        db.execute("INSERT INTO solve_board_events(run_id,key,data) VALUES(?,?,?)",
                   (board.run_id, payload["key"], json_text(payload)))
    return True


def registry(board, run=None, events=None):
    """Separate actual scheduler state from a researcher's dated, self-reported intent."""
    run = run or board.store.load(board.run_id)
    events = rows(board) if events is None else events
    latest = {e["actor"]: e for e in events if e["action"] == "activity"}
    team = run.native.solve_team
    active = {a["worker_id"]: a for a in team.active_attempts}
    history = {h["worker_id"]: h for h in run.native.history if h.get("worker_id")}
    identities = set(team.workers) | set(active) | set(latest) | set(history)
    output = []
    for actor in sorted(identities):
        worker = team.workers.get(actor)
        attempt = active.get(actor)
        report = latest.get(actor)
        task = (attempt or history.get(actor) or {}).get("task_id")
        running = bool(attempt and str(run.state) == "SOLVING")
        status = worker.state if worker else "idle"
        if status == "running" and not attempt:
            status = "interrupted"
        output.append({
            "actor": actor, "group": worker.group if worker else "supervision",
            "role": "supervision" if actor == "supervisor" else "research",
            "objective": worker.objective if worker else "Review evidence and coordinate research",
            "runtime_status": "running" if running else "interrupted" if attempt else (
                status),
            "task_id": task, "started_at": attempt.get("started_at") if attempt else None,
            "report": {key: report[key] for key in (
                "key", "time", "task_id", "summary", "status", "focus",
            )} | {key: report.get(key, "explore" if key == "intent" else "") for key in (
                "topic", "approach", "intent", "overlap_reason",
            )} if report else None,
            "report_current": bool(running and report and report.get("task_id") == task),
        })
    return output


def overview(board, run=None):
    events = rows(board)
    return {
        "agents": registry(board, run, events),
        "channels": [{k: v for k, v in channel.items() if k != "events"} | {
            "event_count": len(channel["events"]),
        } for channel in channels(events)],
        "event_count": len(events),
        "note": "Group objectives are suggestions, not compulsory research routes. "
                "Channels are public within this run; joining is voluntary. Reports are self-reported, "
                "not verified progress. Nothing here starts or changes an agent's account or resources.",
    }
