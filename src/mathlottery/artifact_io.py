"""Descriptor-based artifact I/O; never follow symlinks in a snapshot path."""

import os
import stat
from pathlib import Path
from uuid import uuid4


def validate_relative(relative: str):
    if not relative or any(p in {"", ".", ".."} for p in relative.split("/")) or "\\" in relative:
        raise ValueError("Snapshot paths must be relative without traversal")


def read_confined(root: Path, relative: str, limit: int) -> bytes:
    validate_relative(relative)
    descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        parts = relative.split("/")
        for part in parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        file = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=descriptor)
        with os.fdopen(file, "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise ValueError("Snapshot source must be a regular, unlinked file")
            if info.st_size > limit:
                raise ValueError("Snapshot file size limit exceeded")
            data = stream.read(limit + 1)
            if len(data) > limit:
                raise ValueError("Snapshot file size limit exceeded")
            return data
    finally:
        os.close(descriptor)


def write_confined(root: Path, relative: str, data: bytes) -> None:
    """Atomic projection using directory descriptors; never follow swapped parents."""
    validate_relative(relative)
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
