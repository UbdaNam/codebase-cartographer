"""Typed semantic artifact contracts for Stage 6 Semanticist."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator, model_validator

from src.models.artifacts import SerializationMetadata
from src.models.enums import AnalysisMethod, ConfidenceBand
from src.utils.ids import (
    build_day_one_answer_id,
    build_domain_id,
    build_drift_id,
    build_evidence_reference_id,
    build_semantic_profile_id,
    canonicalize_json_value,
    normalize_relative_path,
)


class EvidenceReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reference_id: str | None = None
    source_kind: str
    artifact_path: str | None = None
    repository_path: str
    line_start: int | None = None
    line_end: int | None = None
    quoted_text: str | None = None
    observed_or_inferred: Literal["observed", "graph_inference", "llm_inference"]
    analysis_method: AnalysisMethod
    confidence: ConfidenceBand = ConfidenceBand.UNKNOWN

    @field_validator("repository_path")
    @classmethod
    def validate_repository_path(cls, value: str) -> str:
        return normalize_relative_path(value)

    @field_validator("artifact_path")
    @classmethod
    def validate_artifact_path(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.replace("\\", "/")

    @model_validator(mode="after")
    def finalize_identity(self) -> "EvidenceReference":
        if self.reference_id is None:
            self.reference_id = build_evidence_reference_id(
                self.source_kind,
                self.repository_path,
                self.line_start,
                self.line_end,
            )
        return self


class PurposeEvidenceBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bundle_id: str
    module_id: str
    module_path: str
    imports: list[str] = Field(default_factory=list)
    public_api_signals: list[str] = Field(default_factory=list)
    graph_metrics: dict[str, Any] = Field(default_factory=dict)
    lineage_relationships: dict[str, list[str]] = Field(default_factory=dict)
    git_velocity_signals: dict[str, Any] = Field(default_factory=dict)
    code_excerpt_refs: list[EvidenceReference] = Field(default_factory=list)
    documentation_refs: list[EvidenceReference] = Field(default_factory=list)
    analysis_methods: list[AnalysisMethod] = Field(default_factory=list)

    @field_validator("module_path")
    @classmethod
    def validate_module_path(cls, value: str) -> str:
        return normalize_relative_path(value)

    @field_serializer("graph_metrics", "git_velocity_signals")
    def serialize_metadata(self, value: dict[str, Any]) -> dict[str, Any]:
        return canonicalize_json_value(value)

    @field_serializer("analysis_methods")
    def serialize_methods(self, value: list[AnalysisMethod]) -> list[str]:
        return [item.value for item in value]


class SemanticModuleProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    semantic_profile_id: str | None = None
    module_id: str
    relative_path: str
    language: str
    purpose_statement: str
    purpose_confidence: ConfidenceBand = ConfidenceBand.UNKNOWN
    domain_id: str | None = None
    domain_label: str | None = None
    evidence_references: list[EvidenceReference] = Field(default_factory=list)
    source_excerpt_refs: list[EvidenceReference] = Field(default_factory=list)
    doc_drift_status: str = "unchecked"
    warning_codes: list[str] = Field(default_factory=list)
    is_partial: bool = False
    evidence_bundle: PurposeEvidenceBundle

    @field_validator("relative_path")
    @classmethod
    def validate_relative_path(cls, value: str) -> str:
        return normalize_relative_path(value)

    @field_serializer("warning_codes")
    def serialize_warning_codes(self, value: list[str]) -> list[str]:
        return sorted(dict.fromkeys(value))

    @model_validator(mode="after")
    def finalize_identity(self) -> "SemanticModuleProfile":
        if self.semantic_profile_id is None:
            self.semantic_profile_id = build_semantic_profile_id(self.module_id)
        return self


class DocumentationDriftRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    drift_id: str | None = None
    module_id: str
    module_path: str
    observed_documentation: str
    inferred_purpose: str
    drift_type: Literal["contradiction", "omission", "outdated", "insufficient_evidence"]
    confidence: ConfidenceBand = ConfidenceBand.UNKNOWN
    evidence_references: list[EvidenceReference] = Field(default_factory=list)
    is_partial: bool = False
    warning_codes: list[str] = Field(default_factory=list)

    @field_validator("module_path")
    @classmethod
    def validate_module_path(cls, value: str) -> str:
        return normalize_relative_path(value)

    @field_serializer("warning_codes")
    def serialize_warning_codes(self, value: list[str]) -> list[str]:
        return sorted(dict.fromkeys(value))

    @model_validator(mode="after")
    def finalize_identity(self) -> "DocumentationDriftRecord":
        if self.drift_id is None:
            self.drift_id = build_drift_id(self.module_id, self.drift_type, self.module_path)
        return self


class DomainAssignment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    module_id: str
    domain_id: str
    assignment_confidence: ConfidenceBand = ConfidenceBand.UNKNOWN
    assignment_signals: list[str] = Field(default_factory=list)

    @field_serializer("assignment_signals")
    def serialize_assignment_signals(self, value: list[str]) -> list[str]:
        return sorted(dict.fromkeys(value))


class DomainCluster(BaseModel):
    model_config = ConfigDict(extra="forbid")

    domain_id: str | None = None
    label: str
    summary: str
    confidence: ConfidenceBand = ConfidenceBand.UNKNOWN
    module_ids: list[str] = Field(default_factory=list)
    primary_signals: list[str] = Field(default_factory=list)
    is_partial: bool = False
    assignments: list[DomainAssignment] = Field(default_factory=list)

    @field_serializer("module_ids")
    def serialize_module_ids(self, value: list[str]) -> list[str]:
        return sorted(dict.fromkeys(value))

    @field_serializer("primary_signals")
    def serialize_primary_signals(self, value: list[str]) -> list[str]:
        return sorted(dict.fromkeys(value))

    @model_validator(mode="after")
    def finalize_identity(self) -> "DomainCluster":
        if self.domain_id is None:
            self.domain_id = build_domain_id(self.label)
        return self


class DayOneAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer_id: str | None = None
    question_id: str
    question_text: str
    answer_text: str
    confidence: ConfidenceBand = ConfidenceBand.UNKNOWN
    evidence_references: list[EvidenceReference] = Field(default_factory=list)
    supporting_module_ids: list[str] = Field(default_factory=list)
    supporting_dataset_ids: list[str] = Field(default_factory=list)
    is_partial: bool = False
    warning_codes: list[str] = Field(default_factory=list)

    @field_serializer("supporting_module_ids", "supporting_dataset_ids", "warning_codes")
    def serialize_unique_lists(self, value: list[str]) -> list[str]:
        return sorted(dict.fromkeys(value))

    @model_validator(mode="after")
    def finalize_identity(self) -> "DayOneAnswer":
        if self.answer_id is None:
            self.answer_id = build_day_one_answer_id(self.question_id)
        return self


class SemanticRunLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    analyzed_module_count: int = 0
    partial_module_count: int = 0
    drift_record_count: int = 0
    domain_count: int = 0
    provider_request_count: int = 0
    estimated_prompt_tokens: int = 0
    estimated_completion_tokens: int = 0
    budget_exhausted: bool = False
    warning_codes: list[str] = Field(default_factory=list)

    @field_serializer("warning_codes")
    def serialize_warning_codes(self, value: list[str]) -> list[str]:
        return sorted(dict.fromkeys(value))


class SemanticArtifactBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metadata: SerializationMetadata
    analysis_root: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    warnings: list[str] = Field(default_factory=list)
    partial_result_flags: list[str] = Field(default_factory=list)

    @field_validator("analysis_root")
    @classmethod
    def validate_analysis_root(cls, value: str) -> str:
        return value.replace("\\", "/")

    @field_serializer("warnings", "partial_result_flags")
    def serialize_string_lists(self, value: list[str]) -> list[str]:
        return sorted(dict.fromkeys(value))


class ModuleSemanticsPayload(SemanticArtifactBase):
    profiles: list[SemanticModuleProfile] = Field(default_factory=list)
    ledger: SemanticRunLedger

    @field_serializer("profiles")
    def serialize_profiles(self, value: list[SemanticModuleProfile]) -> list[dict[str, Any]]:
        ordered = sorted(value, key=lambda item: (item.relative_path, item.module_id))
        return [canonicalize_json_value(item.model_dump(mode="json")) for item in ordered]


class DocumentationDriftPayload(SemanticArtifactBase):
    drift_records: list[DocumentationDriftRecord] = Field(default_factory=list)
    ledger: SemanticRunLedger

    @field_serializer("drift_records")
    def serialize_records(self, value: list[DocumentationDriftRecord]) -> list[dict[str, Any]]:
        ordered = sorted(value, key=lambda item: (item.module_path, item.drift_type, item.drift_id or ""))
        return [canonicalize_json_value(item.model_dump(mode="json")) for item in ordered]


class DomainMapPayload(SemanticArtifactBase):
    domains: list[DomainCluster] = Field(default_factory=list)
    ledger: SemanticRunLedger

    @field_serializer("domains")
    def serialize_domains(self, value: list[DomainCluster]) -> list[dict[str, Any]]:
        ordered = sorted(value, key=lambda item: (item.label.lower(), item.domain_id or ""))
        return [canonicalize_json_value(item.model_dump(mode="json")) for item in ordered]


class DayOneAnswersPayload(SemanticArtifactBase):
    answers: list[DayOneAnswer] = Field(default_factory=list)
    ledger: SemanticRunLedger

    @field_serializer("answers")
    def serialize_answers(self, value: list[DayOneAnswer]) -> list[dict[str, Any]]:
        ordered = sorted(value, key=lambda item: item.question_id)
        return [canonicalize_json_value(item.model_dump(mode="json")) for item in ordered]
