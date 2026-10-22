"""Bounded access to Lean sources produced inside a research or review workspace."""

from __future__ import annotations

import os
import stat
from pathlib import Path, PurePosixPath

MAX_SOURCE_BYTES = 1_000_000
MAX_FILES = 100
MAX_ENTRIES = 2000
MAX_DEPTH = 12
WORKSPACES = {"workspace", "review-workspaces"}
SKIP_DIRECTORIES = {"node_modules", "__pycache__", "build"}


def _allowed(relative: str) -> bool:
    parts = relative.split("/")
    return (
        len(parts) >= 2
        and parts[0] in WORKSPACES
        and all(part and not part.startswith(".") and "\\" not in part and "\0" not in part for part in parts)
        and not any(part in SKIP_DIRECTORIES for part in parts[:-1])
        and (PurePosixPath(relative).suffix == ".lean" or parts[-1] in {"lean-toolchain", "lakefile.toml"})
    )


def _source_path(root: Path, relative: str) -> Path:
    if not _allowed(relative):
        raise ValueError("Choose a Lean source or project file inside this run's workspace")
    path = root
    for part in relative.split("/"):
        path /= part
        if path.is_symlink():
            raise ValueError("Linked files are not available through the browser")
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Source must stay inside this run")
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ValueError("Only regular, unlinked source files can be downloaded")
    return path


def list_formal_artifacts(root: Path) -> dict:
    """Do not descend into Lean dependencies, dot directories or linked directories."""
    root = Path(root)
    items, truncated = [], False
    pending = [root / name for name in sorted(WORKSPACES, reverse=True)]
    visited = 0
    while pending:
        directory = pending.pop()
        if directory.is_symlink() or not directory.is_dir():
            continue
        depth = len(directory.relative_to(root).parts)
        try:
            with os.scandir(directory) as entries:
                for entry in entries:
                    visited += 1
                    if visited > MAX_ENTRIES:
                        return {"items": sorted(items, key=lambda item: item["path"]), "truncated": True}
                    if entry.name.startswith(".") or entry.is_symlink():
                        continue
                    if entry.is_dir(follow_symlinks=False):
                        if entry.name not in SKIP_DIRECTORIES:
                            if depth < MAX_DEPTH:
                                pending.append(Path(entry.path))
                            else:
                                truncated = True
                        continue
                    relative = Path(entry.path).relative_to(root).as_posix()
                    if not _allowed(relative):
                        continue
                    try:
                        info = _source_path(root, relative).stat()
                    except (OSError, ValueError):
                        continue
                    if len(items) >= MAX_FILES:
                        return {"items": sorted(items, key=lambda item: item["path"]), "truncated": True}
                    items.append({"path": relative, "size": info.st_size, "downloadable": info.st_size <= MAX_SOURCE_BYTES})
        except OSError:
            continue  # A running research process may remove a directory while it is listed.
    return {"items": sorted(items, key=lambda item: item["path"]), "truncated": truncated}


def read_formal_artifact(root: Path, relative: str) -> bytes:
    root = Path(root)
    _source_path(root, relative)
    # Hold directory descriptors so a running agent cannot swap a parent for a
    # symlink between validation and opening the requested source.
    directory = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        parts = relative.split("/")
        for part in parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            os.close(directory)
            directory = child
        descriptor = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
    finally:
        os.close(directory)
    with os.fdopen(descriptor, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError("Only regular, unlinked source files can be downloaded")
        if info.st_size > MAX_SOURCE_BYTES:
            raise ValueError("Source exceeds the 1 MB browser limit; inspect it locally")
        data = stream.read(MAX_SOURCE_BYTES + 1)
    if len(data) > MAX_SOURCE_BYTES:
        raise ValueError("Source exceeds the 1 MB browser limit; inspect it locally")
    if b"\0" in data:
        raise ValueError("Source is not a text file")
    data.decode("utf-8")
    return data
