"""Append-only supervisor opinions bound to immutable board versions.

These are Solve opinions, not independent verification or formal certificates.
"""

import json

from mathlottery.domain.common import digest, now
from mathlottery.storage.core import json_text


def content_hash(message):
    return digest(json_text({
        key: value for key, value in message.items()
        if key not in {"standing", "supervisor_review", "content_sha256"}
    }))


def review_basis(target, values):
    return digest(json_text({
        "content_sha256": target["content_sha256"],
        "prerequisites": {
            dep: [values[dep]["standing"], (values[dep].get("supervisor_review") or {}).get("id")]
            for dep in target["depends_on"]
        },
        "objections": sorted(v["key"] for v in values.values() if v["kind"] == "objection"
                             and v["target"] == target["key"] and v["standing"] != "retracted"),
    }))


def review_targets(board, limit=20):
    """Review new evidence, not the same unresolved lemma every timer tick."""
    values = {m["key"]: m for m in board.messages()}
    return [m["key"] for m in values.values() if m.get("theorem") and m["standing"] != "retracted"
            and (m.get("supervisor_review") or {}).get("basis_sha256") != review_basis(m, values)][:limit]


def project_reviews(board, values):
    with board.store.connect() as db:
        reviews = [json.loads(row[0]) for row in db.execute(
            "SELECT data FROM solve_board_reviews WHERE run_id=? ORDER BY seq", (board.run_id,)
        )]
    latest = {review["key"]: review for review in reviews}
    retracted = {v["target"] for v in values if v["kind"] == "retraction"}
    objections = {}
    for value in values:
        if value["kind"] == "objection" and value["target"] and value["key"] not in retracted:
            objections.setdefault(value["target"], set()).add(value["key"])
    by_key = {}
    for value in values:
        value["content_sha256"] = content_hash(value)
        review = latest.get(value["key"])
        value["supervisor_review"] = review
        value["standing"] = "retracted" if value["key"] in retracted else "unverified"
        unresolved = objections.get(value["key"], set()) - set((review or {}).get("addressed_objections", []))
        if value["standing"] == "unverified" and unresolved:
            value["standing"] = "needs_recheck"
        elif value["standing"] == "unverified" and review:
            stale = review["content_sha256"] != value["content_sha256"] or any(
                by_key[dep]["standing"] != "supervisor_accepted"
                or review["dependency_reviews"].get(dep)
                != (by_key[dep].get("supervisor_review") or {}).get("id")
                for dep in value["depends_on"]
            )
            value["standing"] = "needs_recheck" if stale else {
                "accepted": "supervisor_accepted", "rejected": "supervisor_rejected",
                "needs_work": "needs_recheck",
            }[review["verdict"]]
        if any(by_key[dep]["standing"] in {
            "needs_recheck", "retracted", "supervisor_rejected"
        } for dep in value["depends_on"]):
            if value["standing"] != "retracted":
                value["standing"] = "needs_recheck"
        by_key[value["key"]] = value
    return values


def record_review(board, review, task_id, *, snapshot_hashes):
    identifier = f"{task_id}:{review.key}"
    with board.store.connect() as db:
        old = db.execute("SELECT data FROM solve_board_reviews WHERE run_id=? AND key=?",
                         (board.run_id, identifier)).fetchone()
        if old:
            previous = json.loads(old[0])
            if any(previous[k] != v for k, v in review.model_dump(mode="json").items()):
                raise ValueError("A supervisor review receipt is immutable")
            return previous
    values = {v["key"]: v for v in board.messages()}
    target = values.get(review.key)
    if (target is None or target["content_sha256"] != review.content_sha256
            or snapshot_hashes.get(review.key) != review.content_sha256):
        raise ValueError("Board review must cite an exact version in the supervisor's snapshot")
    if review.verdict == "accepted":
        theorem = target.get("theorem")
        if not theorem or theorem["remaining_obligations"]:
            raise ValueError("Accept only a theorem with a proof chain and no remaining obligations")
        if set(review.checked_steps) != {step["id"] for step in theorem["proof_steps"]}:
            raise ValueError("A theorem review must cover every proof step")
        if target["standing"] == "retracted":
            raise ValueError("A retracted theorem cannot be accepted")
        if any(values[dep]["standing"] != "supervisor_accepted" for dep in target["depends_on"]):
            raise ValueError("Accept prerequisite theorems before their dependent theorem")
        active_objections = {v["key"] for v in values.values() if v["kind"] == "objection"
                             and v["target"] == review.key and v["standing"] != "retracted"}
        if not active_objections <= set(review.addressed_objections):
            raise ValueError("Address each outstanding objection explicitly before accepting")
    if any(key not in values or values[key]["kind"] != "objection"
           or values[key]["target"] != review.key or key not in snapshot_hashes
           for key in review.addressed_objections):
        raise ValueError("Address only objections to this theorem in the supervisor snapshot")
    value = {
        **review.model_dump(mode="json"), "id": identifier, "task_id": task_id,
        "dependency_reviews": {
            dep: (values[dep].get("supervisor_review") or {}).get("id")
            for dep in target["depends_on"]
        },
        "basis_sha256": review_basis(target, values),
    }
    with board.store.connect() as db:
        db.execute("BEGIN IMMEDIATE")
        old = db.execute("SELECT data FROM solve_board_reviews WHERE run_id=? AND key=?",
                         (board.run_id, value["id"])).fetchone()
        if old:
            # Replay of the same supervisor receipt is idempotent, including after
            # another review has invalidated this one's dependency snapshot.
            previous = json.loads(old[0])
            if any(previous[k] != v for k, v in review.model_dump(mode="json").items()):
                raise ValueError("A supervisor review receipt is immutable")
            return previous
        value["time"] = now()
        db.execute("INSERT INTO solve_board_reviews(run_id,key,data) VALUES(?,?,?)",
                   (board.run_id, value["id"], json_text(value)))
    return value
