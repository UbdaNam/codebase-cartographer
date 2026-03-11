"""Graph node, edge, and payload contracts."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator

from src.models.enums import (
    AnalysisMethod,
    ConfidenceBand,
    EdgeKind,
    NodeKind,
    SkipReason,
    SupportStatus,
)
from src.models.evidence import EvidenceRecord
from src.utils.ids import build_edge_id, build_node_id, canonicalize_json_value, normalize_relative_path


class GraphNodeBase(BaseModel):
    """Common graph node fields shared by specialized node contracts."""

    model_config = ConfigDict(extra="forbid")

    node_id: str | None = None
    kind: NodeKind
    canonical_name: str
    path: str | None = None
    language_or_dialect: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    evidence: list[EvidenceRecord] = Field(default_factory=list)
    support_status: SupportStatus = SupportStatus.SUPPORTED
    confidence: ConfidenceBand | None = None
    skip_reason: SkipReason | None = None

    @field_serializer("metadata")
    def serialize_metadata(self, value: dict[str, Any]) -> dict[str, Any]:
        return canonicalize_json_value(value)

    @model_validator(mode="after")
    def finalize_identity(self) -> "GraphNodeBase":
        normalized_path = normalize_relative_path(self.path) if self.path else None
        if normalized_path:
            self.path = normalized_path
        if self.skip_reason and self.support_status == SupportStatus.SUPPORTED:
            raise ValueError("skip_reason cannot be set when support_status is supported")
        if self.node_id is None:
            self.node_id = build_node_id(self.kind, canonical_name=self.canonical_name, path=self.path)
        return self


class ModuleNode(GraphNodeBase):
    kind: Literal[NodeKind.MODULE] = NodeKind.MODULE
    relative_path: str
    module_name: str

    @model_validator(mode="before")
    @classmethod
    def populate_module_defaults(cls, data: Any) -> Any:
        if isinstance(data, dict):
            relative_path = data.get("relative_path")
            module_name = data.get("module_name")
            if relative_path and not data.get("path"):
                data["path"] = relative_path
            if module_name and not data.get("canonical_name"):
                data["canonical_name"] = module_name
        return data

    @model_validator(mode="after")
    def normalize_relative_path_field(self) -> "ModuleNode":
        self.relative_path = normalize_relative_path(self.relative_path)
        self.path = self.relative_path
        return self


class DatasetNode(GraphNodeBase):
    kind: Literal[NodeKind.DATASET] = NodeKind.DATASET
    dataset_name: str
    platform: str | None = None
    namespace: str | None = None

    @model_validator(mode="before")
    @classmethod
    def populate_dataset_defaults(cls, data: Any) -> Any:
        if isinstance(data, dict) and not data.get("canonical_name"):
            dataset_name = data.get("dataset_name")
            namespace = data.get("namespace")
            if dataset_name:
                data["canonical_name"] = f"{namespace}.{dataset_name}" if namespace else dataset_name
        return data


class TransformationNode(GraphNodeBase):
    kind: Literal[NodeKind.TRANSFORMATION] = NodeKind.TRANSFORMATION
    transformation_name: str
    operation_type: str | None = None

    @model_validator(mode="before")
    @classmethod
    def populate_transformation_defaults(cls, data: Any) -> Any:
        if isinstance(data, dict) and not data.get("canonical_name"):
            transformation_name = data.get("transformation_name")
            if transformation_name:
                data["canonical_name"] = transformation_name
        return data


GraphNode = ModuleNode | DatasetNode | TransformationNode


class GraphEdge(BaseModel):
    """Typed relationship connecting two graph nodes."""

    model_config = ConfigDict(extra="forbid")

    edge_id: str | None = None
    source_node_id: str
    target_node_id: str
    kind: EdgeKind
    evidence: list[EvidenceRecord] = Field(default_factory=list)
    analysis_method: AnalysisMethod = AnalysisMethod.STATIC_ANALYSIS
    confidence: ConfidenceBand | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    support_status: SupportStatus = SupportStatus.SUPPORTED
    skip_reason: SkipReason | None = None

    @field_serializer("metadata")
    def serialize_metadata(self, value: dict[str, Any]) -> dict[str, Any]:
        return canonicalize_json_value(value)

    @model_validator(mode="after")
    def finalize_identity(self) -> "GraphEdge":
        if self.skip_reason and self.support_status == SupportStatus.SUPPORTED:
            raise ValueError("skip_reason cannot be set when support_status is supported")
        if self.edge_id is None:
            self.edge_id = build_edge_id(
                self.kind,
                source_node_id=self.source_node_id,
                target_node_id=self.target_node_id,
            )
        return self


class GraphPayload(BaseModel):
    """Deterministic graph container intended for `.cartography` outputs."""

    model_config = ConfigDict(extra="forbid")

    version: str = "1.0"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    run_id: str
    graph_metadata: dict[str, Any] = Field(default_factory=dict)
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)

    @field_serializer("graph_metadata")
    def serialize_graph_metadata(self, value: dict[str, Any]) -> dict[str, Any]:
        return canonicalize_json_value(value)

    @field_serializer("nodes")
    def serialize_nodes(self, value: list[GraphNode]) -> list[dict[str, Any]]:
        ordered = sorted(value, key=lambda node: node.node_id or "")
        return [canonicalize_json_value(node.model_dump(mode="json")) for node in ordered]

    @field_serializer("edges")
    def serialize_edges(self, value: list[GraphEdge]) -> list[dict[str, Any]]:
        ordered = sorted(value, key=lambda edge: edge.edge_id or "")
        return [canonicalize_json_value(edge.model_dump(mode="json")) for edge in ordered]
