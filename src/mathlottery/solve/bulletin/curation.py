"""Reversible visibility changes, independent of proof truth and content hashes."""

import json
from collections import Counter
from datetime import datetime, timezone

from mathlottery.domain.common import now
from mathlottery.solve.bulletin.events import registry, rows
from mathlottery.storage.core import json_text


def annotate(board, values):
    latest = {item["key"]: item for item in rows(board, "solve_board_curation")}
    reads = Counter(key for event in rows(board) if event["action"] == "read" for key in event["focus"])
    users = {}
    for value in values:
        for dependency in value["depends_on"]:
            users.setdefault(dependency, []).append(value["key"])
    for value in values:
        decision = latest.get(value["key"])
        value.update(archived=bool(decision and decision["action"] == "archive"),
                     curation=decision, usage={"recorded_reads": reads[value["key"]],
                                               "dependents": users.get(value["key"], []),
                                               "filesystem_reads_complete": False})
    return values


def protected(values, agents):
    """Keep live dependencies and unresolved objections visible, regardless of popularity."""
    keys = set()
    for value in values:
        if not value["archived"]:
            keys.update(value["depends_on"])
        if value["kind"] == "objection" and value["standing"] != "retracted":
            target = next((v for v in values if v["key"] == value["target"]), None)
            addressed = (target.get("supervisor_review") or {}).get("addressed_objections", []) if target else []
            if value["key"] not in addressed:
                keys.update([value["key"], value["target"]])
    for agent in agents:
        if agent["report_current"]:
            keys.update(agent["report"]["focus"])
    return keys


def suggestions(board):
    from mathlottery.solve.coordination_policy import view

    values = board.messages()
    run = board.store.load(board.run_id)
    policy = view(run)["policy"]
    pinned = protected(values, registry(board, run))
    current = datetime.now(timezone.utc)
    latest_synthesis = next((v["key"] for v in reversed(values) if v["author"] == "supervisor"
                             and v["title"] == "Supervisor synthesis"), None)
    def reason(value):
        if value["standing"] == "retracted":
            return "Retracted version; retain evidence but consider hiding from default discovery"
        if value["author"] == "supervisor" and value["title"] == "Supervisor synthesis" and value["key"] != latest_synthesis:
            return "Earlier synthesis; check whether the latest one preserves its useful conclusions"
        return "Older low-recorded-use entry; direct file reads are not measured"

    eligible = [v for v in values if not v["archived"] and v["key"] not in pinned
                and (v["standing"] == "retracted" or v["usage"]["recorded_reads"] <= policy["archive_read_threshold"])
                and (v["standing"] == "retracted" or not v.get("theorem") or v.get("supervisor_review"))
                and (current - datetime.fromisoformat(v["time"])).total_seconds() >= policy["archive_min_age_seconds"]]
    eligible.sort(key=lambda v: (v["standing"] != "retracted", not reason(v).startswith("Earlier synthesis")))
    return {"candidates": [
        {"key": v["key"], "content_sha256": v["content_sha256"], "title": v["title"],
         "standing": v["standing"], "usage": v["usage"], "reason": reason(v)}
        for v in eligible
    ][:30], "note": "Suggestions only: missing read receipts do NOT mean unused or unimportant. "
        "Native direct filesystem reads are not counted. Review the mathematical value before archiving."}


def curate(board, actions, task_id, *, snapshot_hashes):
    if len({a.key for a in actions}) != len(actions):
        raise ValueError("One curation action per exact message version")
    if not actions:
        return
    values = board.messages()
    by_key = {v["key"]: v for v in values}
    agents = registry(board)
    with board.store.connect() as db:
        db.execute("BEGIN IMMEDIATE")
        pending = []
        for action in actions:
            identifier = f"{task_id}:{action.key}"
            previous = db.execute("SELECT data FROM solve_board_curation WHERE run_id=? AND key=?",
                                  (board.run_id, identifier)).fetchone()
            payload = action.model_dump(mode="json")
            if previous:
                old = json.loads(previous[0])
                if any(old[k] != v for k, v in payload.items()):
                    raise ValueError("Curation receipts are immutable")
                continue
            value = by_key.get(action.key)
            if (value is None or value["content_sha256"] != action.content_sha256
                    or snapshot_hashes.get(action.key) != action.content_sha256):
                raise ValueError("Curation must cite an exact version in the supervisor snapshot")
            pending.append((identifier, payload))
        # Recheck live dependencies inside the write lock: a new publication may have
        # arrived since the supervisor snapshot. Never silently hide that prerequisite.
        live = [json.loads(row[0]) for row in db.execute(
            "SELECT data FROM solve_messages WHERE run_id=? ORDER BY seq", (board.run_id,),
        )]
        visibility = {item["key"]: item["action"] == "archive"
                      for item in rows(board, "solve_board_curation", db)}
        visibility.update({p["key"]: p["action"] == "archive" for _, p in pending})
        for value in live:
            saved = by_key.get(value["key"], {})
            value.update(archived=visibility.get(value["key"], False),
                         standing=saved.get("standing", "unverified"),
                         supervisor_review=saved.get("supervisor_review"))
        # Read the latest focus ledger under the same lock as curation/publication.
        latest_reports = {e["actor"]: e for e in rows(board, db=db) if e["action"] == "activity"}
        for agent in agents:
            report = latest_reports.get(agent["actor"])
            agent["report"] = report
            agent["report_current"] = bool(agent["runtime_status"] == "running" and report
                                           and report.get("task_id") == agent["task_id"])
        pinned = protected(live, agents)
        for identifier, payload in pending:
            if payload["action"] == "archive" and payload["key"] in pinned:
                raise ValueError("Cannot archive a live prerequisite, current focus or unresolved objection")
            db.execute("INSERT INTO solve_board_curation(run_id,key,data) VALUES(?,?,?)",
                       (board.run_id, identifier, json_text({**payload, "id": identifier,
                        "actor": "supervisor", "task_id": task_id, "time": now()})))
