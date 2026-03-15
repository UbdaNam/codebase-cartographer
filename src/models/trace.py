"""Trace-event contracts for Archivist and Navigator."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator

from src.models.enums import ConfidenceBand
from src.models.semantic import EvidenceReference
from src.utils.ids import canonicalize_json_value, stable_id

TraceMethodType = Literal["static", "graph", "lineage", "llm", "synthesis", "reuse"]
TraceReuseStatus = Literal["created", "regenerated", "reused", "skipped"]


class TraceEvent(BaseModel):
    """Append-only audit event for final-stage actions."""

    model_config = ConfigDict(extra="forbid")

    event_id: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    run_id: str
    agent: str
    action: str
    input_summary: dict[str, Any] = Field(default_factory=dict)
    output_summary: dict[str, Any] = Field(default_factory=dict)
    evidence_sources: list[EvidenceReference] = Field(default_factory=list)
    confidence: ConfidenceBand = ConfidenceBand.UNKNOWN
    method_type: TraceMethodType
    reuse_status: TraceReuseStatus | None = None

    @field_serializer("input_summary", "output_summary")
    def serialize_dicts(self, value: dict[str, Any]) -> dict[str, Any]:
        return canonicalize_json_value(value)

    @model_validator(mode="after")
    def finalize_identity(self) -> "TraceEvent":
        if self.event_id is None:
            self.event_id = stable_id("trace_event", self.run_id, self.agent, self.action, self.timestamp.isoformat())
        return self
