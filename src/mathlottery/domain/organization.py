"""Editorial input snapshots and bilingual report outputs."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from mathlottery.domain.common import Model
from mathlottery.domain.provenance import DiscoveryFile


class OrganizationContext(Model):
    """An immutable evidence bundle for an independent editorial session."""

    source_run_id: str = Field(pattern=r"^run-[a-f0-9]{12}$")
    source_revision: int = Field(ge=0)
    source_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    problem_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    captured_at: str
    language: Literal["zh", "en"] = "zh"
    # None preserves the output contract of historical single-language checkpoints.
    report_languages: list[Literal["zh", "en"]] | None = None
    instructions: str | None = Field(default=None, max_length=30000)
    candidate_hashes: list[dict] = Field(default_factory=list)
    files: list[DiscoveryFile] = Field(default_factory=list)
    omitted: list[str] = Field(default_factory=list)
    lineage: list[dict] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def complete_report_languages(self):
        if self.report_languages is not None and (
            len(self.report_languages) != 2 or set(self.report_languages) != {"zh", "en"}
        ):
            raise ValueError("New organization tasks require both zh and en reports")
        return self


class OrganizationDocument(Model):
    """One language of an editorial report and its independently rendered PDF."""

    markdown: str = Field(min_length=1, max_length=500000)
    markdown_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    created_at: str
    pdf_status: Literal["pending", "ready", "failed"] = "pending"
    pdf_error: str | None = None
    pdf_details: dict = Field(default_factory=dict)


class OrganizationReport(OrganizationDocument):
    """Primary-language output plus translations, never a candidate or review."""

    translations: dict[Literal["zh", "en"], OrganizationDocument] = Field(default_factory=dict)
