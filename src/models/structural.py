"""Typed structural analysis models for Stage 3."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator, model_validator

from src.models.artifacts import SerializationMetadata
from src.models.enums import AnalysisMethod, ConfidenceBand, SupportStatus
from src.models.evidence import EvidenceRecord
from src.models.repository_input import PreparedRepository
from src.utils.ids import canonicalize_json_value, normalize_relative_path, stable_id


class StructuralSymbolKind(StrEnum):
    MODULE = "module"
    IMPORT = "import"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    STATEMENT = "statement"
    MAPPING = "mapping"


class ParseStatus(StrEnum):
    PARSED = "parsed"
    PARTIAL = "partial"
    SKIPPED = "skipped"
    FAILED = "failed"
    UNSUPPORTED = "unsupported"


class LanguageRoute(BaseModel):
    """Centralized parser routing result for one manifest record."""

    model_config = ConfigDict(extra="forbid")

    normalized_language: str
    parser_language: str | None = None
    support_status: SupportStatus
    deep_parse_eligible: bool
    notes: list[str] = Field(default_factory=list)


class StructuralRecord(BaseModel):
    """One extracted structural fact."""

    model_config = ConfigDict(extra="forbid")

    record_id: str | None = None
    file_path: str
    language: str
    symbol_kind: StructuralSymbolKind
    symbol_name: str | None = None
    container_name: str | None = None
    signature: str | None = None
    analysis_method: AnalysisMethod = AnalysisMethod.STATIC_ANALYSIS
    support_status: SupportStatus = SupportStatus.SUPPORTED
    confidence: ConfidenceBand = ConfidenceBand.MEDIUM
    warnings: list[str] = Field(default_factory=list)
    evidence: list[EvidenceRecord] = Field(default_factory=list)

    @field_validator("file_path")
    @classmethod
    def validate_file_path(cls, value: str) -> str:
        return normalize_relative_path(value)

    @model_validator(mode="after")
    def finalize_identity(self) -> "StructuralRecord":
        if self.record_id is None:
            self.record_id = stable_id(
                "structural_record",
                self.file_path,
                self.symbol_kind.value,
                self.symbol_name or "-",
                self.container_name or "-",
                self.signature or "-",
            )
        return self


class StructuralFileResult(BaseModel):
    """Full structural outcome for one file."""

    model_config = ConfigDict(extra="forbid")

    file_result_id: str | None = None
    manifest_file_id: str
    file_path: str
    language: str
    support_status: SupportStatus
    parse_status: ParseStatus
    is_partial: bool = False
    records: list[StructuralRecord] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    error_code: str | None = None
    root_node_type: str | None = None
    node_count: int = 0

    @field_validator("file_path")
    @classmethod
    def validate_file_path(cls, value: str) -> str:
        return normalize_relative_path(value)

    @model_validator(mode="after")
    def finalize_identity(self) -> "StructuralFileResult":
        if self.file_result_id is None:
            self.file_result_id = stable_id("structural_file", self.manifest_file_id, self.file_path)
        return self


class StructuralSummary(BaseModel):
    """Run-level structural analysis summary."""

    model_config = ConfigDict(extra="forbid")

    total_files: int = 0
    parsed_files: int = 0
    partial_files: int = 0
    skipped_files: int = 0
    failed_files: int = 0
    unsupported_files: int = 0
    record_count: int = 0


class StructuralIndexPayload(BaseModel):
    """Deterministic structural index artifact."""

    model_config = ConfigDict(extra="forbid")

    metadata: SerializationMetadata
    prepared_repository: PreparedRepository
    file_results: list[StructuralFileResult] = Field(default_factory=list)
    summary: StructuralSummary = Field(default_factory=StructuralSummary)

    @field_serializer("file_results")
    def serialize_file_results(self, value: list[StructuralFileResult]) -> list[dict]:
        ordered = sorted(value, key=lambda item: item.file_path)
        return [canonicalize_json_value(item.model_dump(mode="json")) for item in ordered]


class AstIndexEntry(BaseModel):
    """Compact AST metadata per analyzed file."""

    model_config = ConfigDict(extra="forbid")

    manifest_file_id: str
    file_path: str
    language: str
    root_node_type: str | None = None
    node_count: int = 0
    has_error: bool = False

    @field_validator("file_path")
    @classmethod
    def validate_file_path(cls, value: str) -> str:
        return normalize_relative_path(value)


class AstIndexPayload(BaseModel):
    """Deterministic AST summary artifact."""

    model_config = ConfigDict(extra="forbid")

    metadata: SerializationMetadata
    prepared_repository: PreparedRepository
    entries: list[AstIndexEntry] = Field(default_factory=list)

    @field_serializer("entries")
    def serialize_entries(self, value: list[AstIndexEntry]) -> list[dict]:
        ordered = sorted(value, key=lambda item: item.file_path)
        return [canonicalize_json_value(item.model_dump(mode="json")) for item in ordered]
