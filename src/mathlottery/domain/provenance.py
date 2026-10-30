"""Immutable discovery and review source linkage."""

from __future__ import annotations

from pydantic import Field

from mathlottery.domain.common import Model


class ReviewSource(Model):
    """An exact UTF-8 source snapshot, not a claim of successful verification."""

    path: str = Field(min_length=1, max_length=2048)
    size: int = Field(ge=0, le=1_000_000)
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    content: str = Field(max_length=1_000_000)


class ReviewEvidence(Model):
    source_run_id: str = Field(pattern=r"^run-[a-f0-9]{12}$")
    source_candidate_id: str = Field(pattern=r"^candidate-[a-f0-9]{12}$")
    candidate_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    candidate_id: str | None = Field(default=None, pattern=r"^candidate-[a-f0-9]{12}$")
    captured_at: str
    files: list[ReviewSource] = Field(min_length=1, max_length=20)


class DiscoveryFile(Model):
    path: str
    size: int = Field(ge=0)
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")


class DiscoveryContext(Model):
    """Frozen Find material selected by the user, never an inherited reviewer memory."""

    source_run_id: str = Field(pattern=r"^run-[a-f0-9]{12}$")
    problem_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    captured_at: str
    files: list[DiscoveryFile] = Field(default_factory=list)
    omitted: list[str] = Field(default_factory=list)


class ReviewProvenance(Model):
    """Exact solver linkage, including reviews with no file attachments."""

    source_run_id: str = Field(pattern=r"^run-[a-f0-9]{12}$")
    source_candidate_id: str = Field(pattern=r"^candidate-[a-f0-9]{12}$")
    candidate_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
