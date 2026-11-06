"""Append-only, run-scoped Solve messages. Mathematical claims remain unverified."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Literal

from pydantic import Field

from mathlottery.models import Model, digest, now
from mathlottery.solve.board_reviews import project_reviews, record_review
from mathlottery.solve.bulletin import curation, events, navigation
from mathlottery.solve.bulletin.contracts import BoardEvent
from mathlottery.solve.contracts import TheoremRecord
from mathlottery.storage.core import Store, atomic_write, json_text, safe_path


class Message(Model):
    id: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,80}$")
    kind: Literal["result", "question", "objection", "failed_route", "retraction", "intent"]
    title: str = Field(min_length=1, max_length=300)
    body: str = Field(min_length=1, max_length=30000)
    assumptions: list[str] = Field(default_factory=list, max_length=100)
    artifacts: list[str] = Field(default_factory=list, max_length=30)
    depends_on: list[str] = Field(default_factory=list, max_length=100)
    target: str | None = None
    # A solver's own check is evidence to inspect, never an independent verdict.
    check_status: Literal["unverified", "author_checked"] = "unverified"
    theorem: TheoremRecord | None = None
    tags: list[str] = Field(default_factory=list, max_length=30)
    aliases: list[str] = Field(default_factory=list, max_length=10)


class SolveBoard:
    def __init__(self, store: Store, run_id: str):
        self.store, self.run_id = store, run_id
        self._observed = {}
        store.run_dir(run_id)
        with store.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS solve_messages (
                seq INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL, key TEXT NOT NULL, data TEXT NOT NULL,
                UNIQUE(run_id, key))""")
            db.execute("""CREATE TABLE IF NOT EXISTS solve_board_reviews (
                seq INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL, key TEXT NOT NULL, data TEXT NOT NULL,
                UNIQUE(run_id, key))""")
        events.initialize(self)

    def publish(self, author: str, group: str, message: Message, workspace: Path) -> bool:
        key = f"{author}:{message.id}"
        artifacts = []
        for relative in message.artifacts:
            path = safe_path(workspace, relative)
            if not path.is_file():
                raise ValueError(f"Shared artifact is missing: {relative}")
            if path.stat().st_size > 2_000_000:
                raise ValueError(
                    "Share a small proof/source artifact, not a large build or dataset"
                )
            # Freeze the bytes; later edits cannot change what a message cited.
            content = path.read_bytes()
            if len(content) > 2_000_000:
                raise ValueError("Shared artifact grew beyond the publication limit")
            text = content.decode("utf-8")
            sha = digest(text)
            location = f"solve-board/materials/{sha}.txt"
            atomic_write(safe_path(self.store.run_dir(self.run_id), location), text)
            artifacts.append({"source": relative, "path": location, "sha256": sha})
        payload = message.model_dump(mode="json")
        payload.update(key=key, author=author, group=group, artifacts=artifacts)
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            old = db.execute(
                "SELECT data FROM solve_messages WHERE run_id=? AND key=?", (self.run_id, key)
            ).fetchone()
            if old:
                previous = json.loads(old[0])
                previous.pop("time", None)
                previous.setdefault("theorem", None)
                previous.setdefault("tags", [])
                previous.setdefault("aliases", [])
                if previous != payload:
                    raise ValueError(
                        "Published messages are immutable; use a new ID to correct one"
                    )
                return False
            for dependency in [*message.depends_on, *([message.target] if message.target else [])]:
                row = db.execute(
                    "SELECT data FROM solve_messages WHERE run_id=? AND key=?",
                    (self.run_id, dependency),
                ).fetchone()
                if not row:
                    raise ValueError("Message dependency/target must exist in this run")
                if message.kind == "retraction" and dependency == message.target:
                    if json.loads(row[0])["author"] != author:
                        raise ValueError(
                            "Retract your own message; use objection for another author's work"
                        )
            if message.kind == "retraction" and not message.target:
                raise ValueError("Retraction requires a target")
            payload["time"] = now()
            db.execute(
                "INSERT INTO solve_messages(run_id,key,data) VALUES(?,?,?)",
                (self.run_id, key, json_text(payload)),
            )
        return True

    def messages(self) -> list[dict]:
        with self.store.connect() as db:
            values = [
                json.loads(row[0])
                for row in db.execute(
                    "SELECT data FROM solve_messages WHERE run_id=? ORDER BY seq",
                    (self.run_id,),
                )
            ]
        retracted = {v["target"] for v in values if v["kind"] == "retraction"}
        challenged = {v["target"] for v in values if v["kind"] == "objection" and v["target"]}
        affected = retracted | challenged
        # Dependencies point to existing messages, so chronological propagation is sufficient.
        for value in values:
            if any(dep in affected for dep in value["depends_on"]):
                affected.add(value["key"])
            value["standing"] = (
                "retracted"
                if value["key"] in retracted
                else "needs_recheck"
                if value["key"] in affected
                else "unverified"
            )
        return curation.annotate(self, project_reviews(self, values))

    def review(self, value, task_id, *, snapshot_hashes):
        return record_review(self, value, task_id, snapshot_hashes=snapshot_hashes)

    def revision(self):
        with self.store.connect() as db:
            return tuple(db.execute(
                f"SELECT COALESCE(MAX(seq),0) FROM {table} WHERE run_id=?", (self.run_id,)
            ).fetchone()[0] for table in ("solve_messages", "solve_board_reviews",
                                          "solve_board_events", "solve_board_curation"))

    def cards(self):
        return [navigation.card(v) for v in self.messages()]

    def graph(self, *, include_archived=False):
        return navigation.graph(self.cards(), include_archived)

    def read(self, key):
        value = next((v for v in self.messages() if v["key"] == key), None)
        if value is None:
            raise ValueError("No such message in this run")
        return value

    def event(self, actor, group, value, *, task_id=None):
        return events.register(self, actor, group, value, task_id=task_id)

    def collaboration(self, run=None):
        return events.overview(self, run)

    def curate(self, actions, task_id, *, snapshot_hashes):
        return curation.curate(self, actions, task_id, snapshot_hashes=snapshot_hashes)

    def project(self, workspace: Path) -> None:
        from mathlottery.solve.bulletin.projection import project

        project(self, workspace)

    def ingest_events(self, author, group, workspace, *, task_id=None):
        changed, errors = False, []
        processed = 0
        for original in sorted(safe_path(workspace, "outbox-events").glob("*.json")):
            try:
                path = safe_path(workspace, str(original.relative_to(workspace)))
                stat = path.stat()
                stamp = (stat.st_mtime_ns, stat.st_size)
                if self._observed.get(path) == stamp:
                    continue
                if processed >= 1000:
                    break
                processed += 1
                if stat.st_size > 30000:
                    raise ValueError("Board event exceeds 30 KB")
                with path.open("rb") as stream:
                    content = stream.read(30001)
                if len(content) > 30000:
                    raise ValueError("Board event exceeds 30 KB")
                event = BoardEvent.model_validate_json(content)
                changed = self.event(author, group, event, task_id=task_id) or changed
                self._observed[path] = stamp
            except (ValueError, OSError, UnicodeError) as error:
                errors.append(f"{original.name}: {error}")
        return changed, errors

    def ingest(self, author: str, group: str, workspace: Path) -> tuple[bool, list[str]]:
        folder = safe_path(workspace, "outbox")
        changed = False
        receipts_path = safe_path(workspace, "bulletin/publications.json")
        try:
            receipts = json.loads(receipts_path.read_text())
        except (OSError, ValueError):
            receipts = {}
        if not isinstance(receipts, dict):
            receipts = {}
        receipts = {name: r for name, r in receipts.items() if isinstance(r, dict)
                    and r.get("status") in {"published", "rejected"}
                    and (r["status"] != "rejected" or "error" in r)}
        # Bound new publication work, not the first filenames forever. Old files
        # remain as durable evidence and must not starve later publications.
        processed = 0
        for path in sorted(folder.glob("*.json")):
            try:
                path = safe_path(workspace, str(path.relative_to(workspace)))
                stat = path.stat()
                stamp = (stat.st_mtime_ns, stat.st_size)
                if self._observed.get(path) == stamp:
                    continue
                if processed >= 1000:
                    break
                processed += 1
                if stat.st_size > 100_000:
                    raise ValueError("Board message exceeds 100 KB")
                with path.open("rb") as stream:
                    content = stream.read(100_001)
                if len(content) > 100_000:
                    raise ValueError("Board message exceeds 100 KB")
                message = Message.model_validate_json(content)
                changed = self.publish(author, group, message, workspace) or changed
                self._observed[path] = stamp
                receipts[path.name] = {"status": "published", "key": f"{author}:{message.id}",
                                       "input_sha256": digest(content.decode("utf-8"))}
            except (ValueError, OSError, UnicodeError) as error:
                receipts[path.name] = {"status": "rejected", "error": str(error),
                    "hint": "Use python board_client.py validate FILE, then publish FILE. "
                            "Required envelope: id, kind, title, body; metadata is server-owned. "
                            "Keep the mathematical statement and proof intact when repairing the envelope."}
        from mathlottery.solve.bulletin.projection import write

        write(receipts_path, json_text(receipts))
        return changed, [f"{name}: {r['error']}" for name, r in receipts.items() if r["status"] == "rejected"]

    def context(self, *, hosted=False, material_limit=256_000):
        values = self.messages()
        if not hosted:
            return json_text(values)
        contents, omitted, size = {}, [], 0
        for value in reversed(values):
            for artifact in value["artifacts"]:
                key = artifact["sha256"]
                if key in contents:
                    continue
                path = safe_path(self.store.run_dir(self.run_id), artifact["path"])
                if size + path.stat().st_size > material_limit:
                    omitted.append(key)
                    continue
                contents[key] = path.read_text()
                size += path.stat().st_size
        return json_text(
            {
                "messages": values,
                "material_text": contents,
                "omitted_materials": omitted,
                "note": "Hosted tools cannot retrieve omitted local files. Request the needed derivation in a future checkpoint; do not assume its proof.",
            }
        )

    def material(self, sha256: str) -> bytes:
        if not re.fullmatch(r"[a-f0-9]{64}", sha256) or not any(
            a["sha256"] == sha256 for message in self.messages() for a in message["artifacts"]
        ):
            raise ValueError("Choose a published Solve material from this run")
        path = safe_path(self.store.run_dir(self.run_id), f"solve-board/materials/{sha256}.txt")
        if not path.is_file() or path.stat().st_size > 2_000_000:
            raise ValueError("Published material is unavailable or exceeds its size limit")
        content = path.read_bytes()
        if len(content) > 2_000_000 or digest(content.decode("utf-8")) != sha256:
            raise ValueError("Published material no longer matches its frozen hash")
        return content
