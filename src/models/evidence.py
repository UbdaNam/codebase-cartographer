"""Evidence and citation contracts shared across graph and state models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.models.enums import AnalysisMethod, ConfidenceBand
from src.utils.ids import normalize_relative_path


class EvidenceRecord(BaseModel):
    """Evidence captured from analysis-root-relative source material."""

    model_config = ConfigDict(extra="forbid")

    source_path: str
    line_start: int | None = None
    line_end: int | None = None
    language: str | None = None
    analysis_method: AnalysisMethod
    confidence: ConfidenceBand = ConfidenceBand.UNKNOWN
    excerpt: str | None = None
    symbol_name: str | None = None
    content_redacted: bool = False

    @field_validator("source_path")
    @classmethod
    def validate_source_path(cls, value: str) -> str:
        return normalize_relative_path(value)

    @model_validator(mode="after")
    def validate_line_range(self) -> "EvidenceRecord":
        if self.line_start is not None and self.line_start < 1:
            raise ValueError("line_start must be positive when provided")
        if self.line_end is not None and self.line_end < 1:
            raise ValueError("line_end must be positive when provided")
        if self.line_start is not None and self.line_end is not None and self.line_end < self.line_start:
            raise ValueError("line_end must be greater than or equal to line_start")
        return self


class Citation(BaseModel):
    """Citation-friendly evidence payload for reports and future answers."""

    model_config = ConfigDict(extra="forbid")

    source_path: str
    line_start: int | None = None
    line_end: int | None = None
    symbol_name: str | None = None
    analysis_method: AnalysisMethod
    confidence: ConfidenceBand = ConfidenceBand.UNKNOWN
    excerpt: str | None = None
    note: str | None = None
    content_redacted: bool = False

    @field_validator("source_path")
    @classmethod
    def validate_source_path(cls, value: str) -> str:
        return normalize_relative_path(value)

    @model_validator(mode="after")
    def validate_line_range(self) -> "Citation":
        if self.line_start is not None and self.line_start < 1:
            raise ValueError("line_start must be positive when provided")
        if self.line_end is not None and self.line_end < 1:
            raise ValueError("line_end must be positive when provided")
        if self.line_start is not None and self.line_end is not None and self.line_end < self.line_start:
            raise ValueError("line_end must be greater than or equal to line_start")
        return self


class EvidenceCollection(BaseModel):
    """Reusable container for structured evidence and citations."""

    model_config = ConfigDict(extra="forbid")

    evidence: list[EvidenceRecord] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
