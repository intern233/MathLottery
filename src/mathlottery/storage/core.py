from __future__ import annotations

import fcntl
import json
import os
import sqlite3
import tempfile
from contextlib import contextmanager
from pathlib import Path

from mathlottery.models import Problem, Run, now


def safe_path(root: Path, relative: str) -> Path:
    root = root.resolve()
    path = (root / relative).resolve()
    if path == root or not path.is_relative_to(root):
        raise ValueError("Artifact path must stay inside its allowed directory")
    return path


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=".pending-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def json_text(value) -> str:
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


class Store:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.internal = self.root / ".mathlottery"
        self.internal.mkdir(parents=True, exist_ok=True)
        self.db_path = self.internal / "state.sqlite3"
        with self.connect() as db:
            db.executescript("""
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS runs (
                    id TEXT PRIMARY KEY, updated_at TEXT NOT NULL, data TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS events (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL, data TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS problems (
                    id TEXT PRIMARY KEY, source_url TEXT, data TEXT NOT NULL
                );
            """)
            # One paper may contain many different open problems. Preserve existing rows
            # while removing the old one-problem-per-URL constraint in a single transaction.
            indexes = db.execute("PRAGMA index_list(problems)").fetchall()
            unique_source = any(
                row[2]
                and [col[2] for col in db.execute("SELECT * FROM pragma_index_info(?)", (row[1],))]
                == ["source_url"]
                for row in indexes
            )
            if unique_source:
                db.execute("BEGIN IMMEDIATE")
                db.execute(
                    "CREATE TABLE problems_migration (id TEXT PRIMARY KEY, source_url TEXT, data TEXT NOT NULL)"
                )
                db.execute(
                    "INSERT INTO problems_migration SELECT id, source_url, data FROM problems"
                )
                db.execute("DROP TABLE problems")
                db.execute("ALTER TABLE problems_migration RENAME TO problems")

    def connect(self):
        db = sqlite3.connect(self.db_path, timeout=10)
        db.execute("PRAGMA synchronous=FULL")
        return db

    def run_dir(self, run_id: str) -> Path:
        import re

        if not re.fullmatch(r"run-[a-f0-9]{12}", run_id):
            raise ValueError("Invalid run ID")
        return safe_path(self.root / "runs", run_id)

    @contextmanager
    def lock(self, run_id: str):
        self.run_dir(run_id)
        folder = self.internal / "locks"
        folder.mkdir(exist_ok=True)
        with (folder / f"{run_id}.lock").open("a") as handle:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise ValueError("This run is already active in another process") from exc
            try:
                yield
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)

    def save(self, run: Run, event: str, **details) -> None:
        run.revision += 1
        run.updated_at = now()
        entry = {
            "time": run.updated_at,
            "iteration": run.iteration,
            "revision": run.revision,
            "event": event,
            "mode": run.mode,
            "model": run.config.get("backend", {}).get("model"),
            "state": run.state,
            "phase": run.phase,
            **details,
        }
        with self.connect() as db:
            db.execute(
                "INSERT INTO runs VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET "
                "updated_at=excluded.updated_at, data=excluded.data",
                (run.id, run.updated_at, json_text(run)),
            )
            db.execute(
                "INSERT INTO events (run_id, data) VALUES (?, ?)",
                (run.id, json.dumps(entry, ensure_ascii=False)),
            )
        self.project(run)

    def project(self, run: Run) -> None:
        folder = self.run_dir(run.id)
        atomic_write(folder / "metadata.json", json_text(run))
        atomic_write(folder / "usage.json", json_text(run.usage))
        atomic_write(folder / "checkpoints" / f"{run.revision:06d}.json", json_text(run))
        with self.connect() as db:
            rows = db.execute("SELECT data FROM events WHERE run_id=? ORDER BY seq", (run.id,))
            atomic_write(folder / "events.jsonl", "".join(row[0] + "\n" for row in rows))
        if run.problem:
            atomic_write(folder / "problem.json", json_text(run.problem))

    def load(self, run_id: str) -> Run:
        self.run_dir(run_id)
        with self.connect() as db:
            row = db.execute("SELECT data FROM runs WHERE id=?", (run_id,)).fetchone()
        if not row:
            raise ValueError(f"Unknown run: {run_id}")
        return Run.model_validate_json(row[0])

    def list_runs(self) -> list[Run]:
        with self.connect() as db:
            return [
                Run.model_validate_json(row[0])
                for row in db.execute("SELECT data FROM runs ORDER BY updated_at DESC")
            ]

    def save_problem(self, problem: Problem) -> Problem:
        with self.connect() as db:
            if problem.source_url:
                rows = db.execute(
                    "SELECT id, data FROM problems WHERE source_url=?", (problem.source_url,)
                ).fetchall()
                for identifier, data in rows:
                    if json.loads(data)["statement"] == problem.statement:
                        problem = problem.model_copy(update={"id": identifier})
                        break
            db.execute(
                "INSERT INTO problems VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET "
                "source_url=excluded.source_url, data=excluded.data",
                (problem.id, problem.source_url, json_text(problem)),
            )
        folder = safe_path(self.root / "problems", problem.id)
        atomic_write(folder / "problem.json", json_text(problem))
        atomic_write(folder / "statement.md", f"# {problem.title}\n\n{problem.statement}\n")
        atomic_write(
            folder / "references.json", json_text([r.model_dump() for r in problem.references])
        )
        atomic_write(
            folder / "literature.md",
            "\n\n".join(f"[{r.title or r.url}]({r.url})\n\n{r.summary}" for r in problem.references)
            + "\n",
        )
        return problem

    def load_problem(self, problem_id: str) -> Problem:
        with self.connect() as db:
            row = db.execute("SELECT data FROM problems WHERE id=?", (problem_id,)).fetchone()
        if not row:
            raise ValueError(f"Unknown problem: {problem_id}; use `mathlottery add` first")
        return Problem.model_validate_json(row[0])

    def list_problems(self) -> list[Problem]:
        with self.connect() as db:
            return [
                Problem.model_validate_json(row[0])
                for row in db.execute("SELECT data FROM problems ORDER BY id")
            ]
