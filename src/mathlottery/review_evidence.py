"""Explicit, bounded source snapshots for a fresh independent reviewer."""

from __future__ import annotations

import os
import stat
from pathlib import Path
from uuid import uuid4

from mathlottery.models import Candidate, ReviewEvidence, ReviewSource, Run, digest, now
from mathlottery.storage import json_text
from mathlottery.web.artifacts import _allowed, read_formal_artifact

MAX_FILES = 20
MAX_TOTAL_BYTES = 2_000_000
CHAT_MAX_TOTAL_BYTES = 128_000
EXCLUDED_DIRECTORIES = {
    "research-history", "submissions", "sessions", "logs", "cache", "caches",
    "auth", "credentials", "codex-home",
}


def selectable_source(relative: str) -> bool:
    return (
        relative.startswith("workspace/") and _allowed(relative)
        and not any(part.casefold() in EXCLUDED_DIRECTORIES for part in relative.split("/")[:-1])
    )


def manifest(evidence: ReviewEvidence | None) -> dict | None:
    if evidence is None:
        return None
    result = evidence.model_dump(mode="json", exclude={"files"})
    result["files"] = [item.model_dump(exclude={"content"}) for item in evidence.files]
    return result


def validate(evidence: ReviewEvidence, candidate: Candidate, mode: str, *, bound=True) -> None:
    if not 1 <= len(evidence.files) <= MAX_FILES:
        raise ValueError("Select between 1 and 20 proof source files")
    if evidence.candidate_sha256 != candidate.sha256 or (
        bound and evidence.candidate_id != candidate.id
    ):
        raise ValueError("Submitted proof sources do not match the review candidate")
    paths = [item.path for item in evidence.files]
    if len(set(paths)) != len(paths):
        raise ValueError("Select each proof source only once")
    total = 0
    for item in evidence.files:
        if not selectable_source(item.path):
            raise ValueError("Select formal sources from the solver workspace only")
        data = item.content.encode("utf-8")
        if b"\0" in data or len(data) != item.size or digest(item.content) != item.sha256:
            raise ValueError("Submitted proof source integrity check failed")
        if len(data) > 1_000_000:
            raise ValueError("Each proof source must be at most 1 MB")
        total += len(data)
    limit = CHAT_MAX_TOTAL_BYTES if mode == "chat" else MAX_TOTAL_BYTES
    if total > limit:
        if mode == "chat":
            raise ValueError("Chat includes proof sources in its prompt; select at most 128 KB total")
        raise ValueError("Select at most 2 MB of proof sources in total")


def capture(root: Path, source: Run, paths: list[str], mode: str) -> ReviewEvidence | None:
    """The caller must hold the idle source run's lock and check its candidate."""
    if not paths:
        return None
    if len(paths) > MAX_FILES:
        raise ValueError("Select at most 20 proof source files")
    if len(paths) != len(set(paths)):
        raise ValueError("Select each proof source only once")
    files = []
    for relative in paths:
        if not selectable_source(relative):
            raise ValueError("Select formal sources from the solver workspace only")
        data = read_formal_artifact(root, relative)
        content = data.decode("utf-8")
        files.append(ReviewSource(path=relative, size=len(data), sha256=digest(content), content=content))
        limit = CHAT_MAX_TOTAL_BYTES if mode == "chat" else MAX_TOTAL_BYTES
        if sum(item.size for item in files) > limit:
            raise ValueError(
                "Chat includes proof sources in its prompt; select at most 128 KB total"
                if mode == "chat" else "Select at most 2 MB of proof sources in total"
            )
    candidate = source.candidates[-1]
    evidence = ReviewEvidence(
        source_run_id=source.id, source_candidate_id=candidate.id,
        candidate_sha256=candidate.sha256, captured_at=now(), files=files,
    )
    validate(evidence, candidate, mode, bound=False)
    return evidence


def _write_confined(root: Path, relative: str, data: bytes) -> None:
    """Atomic projection using directory descriptors; never follow swapped parents."""
    directory = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    temporary = None
    try:
        parts = relative.split("/")
        for part in parts[:-1]:
            try:
                os.mkdir(part, 0o700, dir_fd=directory)
            except FileExistsError:
                pass
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            os.close(directory)
            directory = child
        try:
            info = os.stat(parts[-1], dir_fd=directory, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise ValueError("Submitted evidence projection must use regular, unlinked files")
        name = f".evidence-{uuid4().hex}.tmp"
        descriptor = os.open(
            name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=directory,
        )
        temporary = name
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, parts[-1], src_dir_fd=directory, dst_dir_fd=directory)
        temporary = None
    finally:
        if temporary is not None:
            os.unlink(temporary, dir_fd=directory)
        os.close(directory)


def project(run: Run, workspace: Path) -> None:
    evidence = run.review_evidence
    if evidence is None:
        return
    validate(evidence, run.candidates[-1], run.mode)
    for item in evidence.files:
        relative = "submitted-evidence/" + item.path.removeprefix("workspace/")
        _write_confined(workspace, relative, item.content.encode("utf-8"))
    _write_confined(workspace, "submitted-evidence/manifest.json", json_text(manifest(evidence)).encode())
