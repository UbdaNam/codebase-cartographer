"""Run, pipeline, and query-state contracts."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_serializer, field_validator, model_validator

from src.models.enums import RunStatus, SkipReason, SupportStatus
from src.models.evidence import Citation, EvidenceRecord
from src.utils.ids import canonicalize_json_value, normalize_relative_path


class RunContext(BaseModel):
    """Stable metadata describing an analysis run and its artifact locations."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    run_id: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime | None = None
    branch: str = "local"
    repo_root: str
    artifact_dir: str = Field(
        validation_alias=AliasChoices("artifact_dir", "artifact_root"),
        serialization_alias="artifact_dir",
    )
    status: RunStatus = RunStatus.RUNNING
    summary_path: str | None = None
    warnings: list[str] = Field(default_factory=list)
    generated_artifact_paths: list[str] = Field(default_factory=list)

    @field_validator("summary_path")
    @classmethod
    def validate_summary_path(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.replace("\\", "/")

    @field_serializer("generated_artifact_paths")
    def serialize_generated_paths(self, value: list[str]) -> list[str]:
        return sorted(path.replace("\\", "/") for path in value)


class RunSummary(BaseModel):
    """Compact run result surface used by the CLI and orchestrator."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    status: RunStatus
    message: str
    manifest_path: str | None = None
    inventory_summary_path: str | None = None
    artifact_paths: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    inventory_stats: dict[str, int] = Field(default_factory=dict)

    @field_validator("manifest_path", "inventory_summary_path")
    @classmethod
    def validate_optional_paths(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.replace("\\", "/")

    @field_serializer("artifact_paths")
    def serialize_artifact_paths(self, value: list[str]) -> list[str]:
        return sorted(path.replace("\\", "/") for path in value)

    @field_serializer("inventory_stats")
    def serialize_inventory_stats(self, value: dict[str, int]) -> dict[str, int]:
        return canonicalize_json_value(value)


class SkippedSummary(BaseModel):
    """Structured skipped-input summary for graceful degradation reporting."""

    model_config = ConfigDict(extra="forbid")

    path: str
    support_status: SupportStatus = SupportStatus.SKIPPED
    skip_reason: SkipReason
    count: int = 1
    is_secret_sensitive: bool = False

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        return normalize_relative_path(value)


class AnalysisState(BaseModel):
    """Shared state for future pipeline execution and artifact tracking."""

    model_config = ConfigDict(extra="forbid")

    run_context: RunContext
    stage_name: str
    stage_stats: dict[str, Any] = Field(default_factory=dict)
    skipped_file_summaries: list[SkippedSummary] = Field(default_factory=list)
    artifact_references: list[str] = Field(default_factory=list)
    partial_results: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    agent_handoffs: list[str] = Field(default_factory=list)

    @field_serializer("stage_stats")
    def serialize_stage_stats(self, value: dict[str, Any]) -> dict[str, Any]:
        return canonicalize_json_value(value)

    @field_serializer("artifact_references")
    def serialize_artifact_references(self, value: list[str]) -> list[str]:
        return sorted(path.replace("\\", "/") for path in value)


class NavigatorToolCall(BaseModel):
    """Recorded tool interaction for future query workflows."""

    model_config = ConfigDict(extra="forbid")

    tool_name: str
    status: str
    detail: str | None = None


class NavigatorState(BaseModel):
    """LangGraph-ready query state without requiring workflow execution."""

    model_config = ConfigDict(extra="forbid")

    incoming_query: str
    artifact_references: list[str] = Field(default_factory=list)
    retrieved_evidence: list[EvidenceRecord] = Field(default_factory=list)
    tool_history: list[NavigatorToolCall] = Field(default_factory=list)
    working_notes: list[str] = Field(default_factory=list)
    final_answer: str | None = None
    citations: list[Citation] = Field(default_factory=list)

    @field_serializer("artifact_references")
    def serialize_artifact_references(self, value: list[str]) -> list[str]:
        return sorted(path.replace("\\", "/") for path in value)

    @model_validator(mode="after")
    def validate_query(self) -> "NavigatorState":
        if not self.incoming_query.strip():
            raise ValueError("incoming_query must not be empty")
        return self
