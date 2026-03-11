"""Analysis artifact and deterministic serialization contracts."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator

from src.models.enums import AnalysisMethod, ConfidenceBand, SkipReason, SupportStatus
from src.models.evidence import Citation, EvidenceRecord
from src.utils.ids import build_artifact_id, canonicalize_json_value, normalize_relative_path


class SerializationMetadata(BaseModel):
    """Metadata shared by deterministic `.cartography` payloads."""

    model_config = ConfigDict(extra="forbid")

    version: str = "1.0"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    run_id: str
    artifact_dir: str | None = None

    @model_validator(mode="after")
    def validate_artifact_dir(self) -> "SerializationMetadata":
        if self.artifact_dir:
            self.artifact_dir = normalize_relative_path(self.artifact_dir)
        return self


class AnalysisArtifact(BaseModel):
    """Typed record describing a produced or planned analysis artifact."""

    model_config = ConfigDict(extra="forbid")

    artifact_id: str | None = None
    artifact_kind: str
    logical_name: str
    support_status: SupportStatus = SupportStatus.SUPPORTED
    analysis_method: AnalysisMethod = AnalysisMethod.STATIC_ANALYSIS
    confidence: ConfidenceBand | None = None
    skip_reason: SkipReason | None = None
    evidence: list[EvidenceRecord] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    serialization_path: str | None = None

    @field_serializer("metadata")
    def serialize_metadata(self, value: dict[str, Any]) -> dict[str, Any]:
        return canonicalize_json_value(value)

    @model_validator(mode="after")
    def finalize_identity(self) -> "AnalysisArtifact":
        if self.serialization_path:
            self.serialization_path = normalize_relative_path(self.serialization_path)
        if self.skip_reason and self.support_status == SupportStatus.SUPPORTED:
            raise ValueError("skip_reason cannot be set when support_status is supported")
        if self.artifact_id is None:
            self.artifact_id = build_artifact_id(
                self.artifact_kind,
                logical_name=self.logical_name,
                serialization_path=self.serialization_path,
            )
        return self


class ArtifactPayload(BaseModel):
    """Deterministic payload wrapper for serialized analysis artifacts."""

    model_config = ConfigDict(extra="forbid")

    metadata: SerializationMetadata
    artifacts: list[AnalysisArtifact] = Field(default_factory=list)

    @field_serializer("artifacts")
    def serialize_artifacts(self, value: list[AnalysisArtifact]) -> list[dict[str, Any]]:
        ordered = sorted(value, key=lambda artifact: artifact.artifact_id or "")
        return [canonicalize_json_value(artifact.model_dump(mode="json")) for artifact in ordered]


def to_canonical_json(model: BaseModel) -> str:
    """Serialize a model to deterministic, pretty-printed JSON."""

    payload = canonicalize_json_value(model.model_dump(mode="json"))
    return json.dumps(payload, indent=2, sort_keys=True)
