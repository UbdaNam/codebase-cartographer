"""Navigator request and response contracts."""

from __future__ import annotations

from typing import Any
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator, model_validator

from src.models.enums import AnalysisMethod, ConfidenceBand
from src.models.semantic import EvidenceReference
from src.utils.ids import normalize_relative_path

NavigatorQueryType = Literal["find_implementation", "trace_lineage", "blast_radius", "explain_module"]
NavigatorDirection = Literal["upstream", "downstream", "both"]
NavigatorTrustLabel = Literal["static_analysis", "graph_inference", "artifact_reuse", "llm_inference"]


class NavigatorRequest(BaseModel):
    """Typed request surface for Navigator queries."""

    model_config = ConfigDict(extra="forbid")

    query_type: NavigatorQueryType | None = None
    query_text: str
    target_identifier: str | None = None
    include_inference: bool = True
    direction: NavigatorDirection | None = None
    max_results: int = 5
    run_id: str | None = None

    @model_validator(mode="after")
    def validate_request(self) -> "NavigatorRequest":
        if not self.query_text.strip():
            raise ValueError("query_text must not be empty")
        if self.max_results < 1:
            raise ValueError("max_results must be positive")
        if self.query_type == "trace_lineage" and self.direction is None:
            self.direction = "both"
        return self


class NavigatorCitation(BaseModel):
    """Citation attached to a Navigator answer item."""

    model_config = ConfigDict(extra="forbid")

    source_file: str
    line_start: int | None = None
    line_end: int | None = None
    analysis_method: AnalysisMethod
    trust_label: NavigatorTrustLabel
    artifact_reference: str | None = None

    @field_validator("source_file")
    @classmethod
    def validate_source_file(cls, value: str) -> str:
        return normalize_relative_path(value)

    @field_validator("artifact_reference")
    @classmethod
    def validate_artifact_reference(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.replace("\\", "/")


class NavigatorAnswerItem(BaseModel):
    """One structured answer item in a Navigator response."""

    model_config = ConfigDict(extra="forbid")

    title: str
    answer_text: str
    confidence: ConfidenceBand = ConfidenceBand.UNKNOWN
    citations: list[NavigatorCitation] = Field(default_factory=list)
    observed_facts: list[str] = Field(default_factory=list)
    inferred_notes: list[str] = Field(default_factory=list)
    warning_codes: list[str] = Field(default_factory=list)

    @field_serializer("observed_facts", "inferred_notes")
    def serialize_text_lists(self, value: list[str]) -> list[str]:
        return [item for item in value]

    @field_serializer("warning_codes")
    def serialize_warning_codes(self, value: list[str]) -> list[str]:
        return sorted(dict.fromkeys(value))


class NavigatorResponse(BaseModel):
    """Full structured Navigator response."""

    model_config = ConfigDict(extra="forbid")

    request: NavigatorRequest
    summary: str
    results: list[NavigatorAnswerItem] = Field(default_factory=list)
    partial_result_flags: list[str] = Field(default_factory=list)
    trace_event_ids: list[str] = Field(default_factory=list)
    used_model_synthesis: bool = False

    @field_serializer("partial_result_flags", "trace_event_ids")
    def serialize_lists(self, value: list[str]) -> list[str]:
        return sorted(dict.fromkeys(value))


class NavigatorToolEnvelope(BaseModel):
    """Structured payload returned by one Navigator tool invocation."""

    model_config = ConfigDict(extra="forbid")

    tool_name: NavigatorQueryType
    answer_items: list[NavigatorAnswerItem] = Field(default_factory=list)
    evidence_references: list[EvidenceReference] = Field(default_factory=list)
    partial_result_flags: list[str] = Field(default_factory=list)

    @field_serializer("answer_items")
    def serialize_answer_items(self, value: list[NavigatorAnswerItem]) -> list[dict[str, Any]]:
        ordered = sorted(value, key=lambda item: item.title.lower())
        return [item.model_dump(mode="json") for item in ordered]

    @field_serializer("partial_result_flags")
    def serialize_partial_flags(self, value: list[str]) -> list[str]:
        return sorted(dict.fromkeys(value))


class NavigatorSynthesisPayload(BaseModel):
    """Structured synthesis response returned by the LLM answer step."""

    model_config = ConfigDict(extra="forbid")

    summary: str
    observed_facts: list[str] = Field(default_factory=list)
    inferred_notes: list[str] = Field(default_factory=list)

    @field_serializer("observed_facts", "inferred_notes")
    def serialize_text_lists(self, value: list[str]) -> list[str]:
        return [item for item in value]
