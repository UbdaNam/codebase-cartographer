"""Archivist artifact contracts for the final stage."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator, model_validator

from src.models.artifacts import SerializationMetadata
from src.models.enums import ConfidenceBand
from src.models.semantic import EvidenceReference
from src.utils.ids import canonicalize_json_value, normalize_relative_path, stable_id


class CodebaseSectionEntry(BaseModel):
    """Structured section item used to render CODEBASE.md."""

    model_config = ConfigDict(extra="forbid")

    title: str
    summary: str
    citations: list[EvidenceReference] = Field(default_factory=list)
    confidence: ConfidenceBand = ConfidenceBand.UNKNOWN
    is_inferred: bool = False


class CodebaseContextDocument(BaseModel):
    """Structured content for the living CODEBASE document."""

    model_config = ConfigDict(extra="forbid")

    metadata: SerializationMetadata
    analysis_root: str
    architecture_overview: str
    critical_path_entries: list[CodebaseSectionEntry] = Field(default_factory=list)
    data_sources: list[CodebaseSectionEntry] = Field(default_factory=list)
    data_sinks: list[CodebaseSectionEntry] = Field(default_factory=list)
    known_debt_entries: list[CodebaseSectionEntry] = Field(default_factory=list)
    recent_change_velocity_entries: list[CodebaseSectionEntry] = Field(default_factory=list)
    module_purpose_index: list[CodebaseSectionEntry] = Field(default_factory=list)
    evidence_references: list[EvidenceReference] = Field(default_factory=list)
    warning_codes: list[str] = Field(default_factory=list)
    is_partial: bool = False

    @field_validator("analysis_root")
    @classmethod
    def validate_analysis_root(cls, value: str) -> str:
        return value.replace("\\", "/")

    @field_serializer("warning_codes")
    def serialize_warning_codes(self, value: list[str]) -> list[str]:
        return sorted(dict.fromkeys(value))

    @field_serializer(
        "critical_path_entries",
        "data_sources",
        "data_sinks",
        "known_debt_entries",
        "recent_change_velocity_entries",
        "module_purpose_index",
        "evidence_references",
    )
    def serialize_lists(self, value: list[Any]) -> list[Any]:
        if value and isinstance(value[0], BaseModel):
            return [canonicalize_json_value(item.model_dump(mode="json")) for item in value]
        return canonicalize_json_value(value)


class OnboardingQuestionSection(BaseModel):
    """One Day-One question rendered into the onboarding brief."""

    model_config = ConfigDict(extra="forbid")

    question_id: str
    question_text: str
    observed_facts: list[str] = Field(default_factory=list)
    inferred_conclusions: list[str] = Field(default_factory=list)
    citations: list[EvidenceReference] = Field(default_factory=list)
    confidence: ConfidenceBand = ConfidenceBand.UNKNOWN
    is_partial: bool = False

    @field_serializer("observed_facts", "inferred_conclusions")
    def serialize_text_lists(self, value: list[str]) -> list[str]:
        return [item for item in value]


class OnboardingBrief(BaseModel):
    """Structured content for onboarding_brief.md."""

    model_config = ConfigDict(extra="forbid")

    metadata: SerializationMetadata
    analysis_root: str
    sections: list[OnboardingQuestionSection] = Field(default_factory=list)
    warning_codes: list[str] = Field(default_factory=list)
    is_partial: bool = False

    @field_validator("analysis_root")
    @classmethod
    def validate_analysis_root(cls, value: str) -> str:
        return value.replace("\\", "/")

    @field_serializer("warning_codes")
    def serialize_warning_codes(self, value: list[str]) -> list[str]:
        return sorted(dict.fromkeys(value))


class SemanticIndexEntry(BaseModel):
    """One semantic retrieval entry persisted in the semantic index."""

    model_config = ConfigDict(extra="forbid")

    entry_id: str | None = None
    module_id: str
    module_path: str
    purpose_statement: str
    domain_cluster: str | None = None
    retrieval_tokens: list[str] = Field(default_factory=list)
    embedding_vector: list[float] | None = None
    evidence_references: list[EvidenceReference] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("module_path")
    @classmethod
    def validate_module_path(cls, value: str) -> str:
        return normalize_relative_path(value)

    @field_serializer("retrieval_tokens")
    def serialize_retrieval_tokens(self, value: list[str]) -> list[str]:
        return sorted(dict.fromkeys(value))

    @model_validator(mode="after")
    def finalize_identity(self) -> "SemanticIndexEntry":
        if self.entry_id is None:
            self.entry_id = stable_id("semantic_index_entry", self.module_id, self.module_path)
        return self


class SemanticIndexSnapshot(BaseModel):
    """Semantic index metadata and entries for one run."""

    model_config = ConfigDict(extra="forbid")

    snapshot_id: str | None = None
    run_id: str
    commit_hash: str | None = None
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    entry_count: int = 0
    embedding_model: str | None = None
    used_fallback_indexing: bool = False
    source_module_ids: list[str] = Field(default_factory=list)
    warning_codes: list[str] = Field(default_factory=list)
    entries: list[SemanticIndexEntry] = Field(default_factory=list)

    @field_serializer("source_module_ids", "warning_codes")
    def serialize_lists(self, value: list[str]) -> list[str]:
        return sorted(dict.fromkeys(value))

    @field_serializer("entries")
    def serialize_entries(self, value: list[SemanticIndexEntry]) -> list[dict[str, Any]]:
        ordered = sorted(value, key=lambda item: (item.module_path, item.module_id))
        return [canonicalize_json_value(item.model_dump(mode="json")) for item in ordered]

    @model_validator(mode="after")
    def finalize_identity(self) -> "SemanticIndexSnapshot":
        if self.snapshot_id is None:
            self.snapshot_id = stable_id("semantic_index_snapshot", self.run_id, self.commit_hash or "-")
        if not self.entry_count:
            self.entry_count = len(self.entries)
        return self


class IncrementalBaseline(BaseModel):
    """Incremental baseline metadata for reuse decisions."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    commit_hash: str | None = None
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    source_files: list[str] = Field(default_factory=list)
    upstream_artifact_paths: list[str] = Field(default_factory=list)
    dependency_keys: list[str] = Field(default_factory=list)
    reusable_artifacts: list[str] = Field(default_factory=list)

    @field_serializer("source_files", "upstream_artifact_paths", "dependency_keys", "reusable_artifacts")
    def serialize_paths(self, value: list[str]) -> list[str]:
        return sorted(dict.fromkeys(item.replace("\\", "/") for item in value))


class ArchivistArtifactBundle(BaseModel):
    """Summary of final-stage artifact outputs for one run."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    analysis_root: str
    codebase_md_path: str
    onboarding_brief_path: str
    lineage_graph_path: str
    semantic_index_path: str
    trace_log_path: str
    incremental_baseline_path: str
    reused_artifact_paths: list[str] = Field(default_factory=list)
    regenerated_artifact_paths: list[str] = Field(default_factory=list)
    partial_result_flags: list[str] = Field(default_factory=list)
    warning_codes: list[str] = Field(default_factory=list)

    @field_validator(
        "analysis_root",
        "codebase_md_path",
        "onboarding_brief_path",
        "lineage_graph_path",
        "semantic_index_path",
        "trace_log_path",
        "incremental_baseline_path",
    )
    @classmethod
    def validate_paths(cls, value: str) -> str:
        return value.replace("\\", "/")

    @field_serializer("reused_artifact_paths", "regenerated_artifact_paths", "partial_result_flags", "warning_codes")
    def serialize_lists(self, value: list[str]) -> list[str]:
        return sorted(dict.fromkeys(item.replace("\\", "/") for item in value))
