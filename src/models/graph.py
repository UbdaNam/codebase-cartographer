"""Graph node, edge, and payload contracts."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator, model_validator

from src.models.enums import AnalysisMethod, ConfidenceBand, EdgeKind, NodeKind, SkipReason, SupportStatus
from src.models.evidence import EvidenceRecord
from src.utils.ids import build_dataset_id, build_edge_id, build_node_id, build_transformation_id, canonicalize_json_value, normalize_relative_path


class GraphNodeBase(BaseModel):
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
    import_targets: list[str] = Field(default_factory=list)
    public_symbol_count: int = 0
    class_count: int = 0
    function_count: int = 0
    pagerank_score: float | None = None
    inbound_import_count: int = 0
    outbound_import_count: int = 0
    change_velocity_recent: int | None = None
    is_high_velocity_core: bool = False
    dead_code_candidate: bool = False
    warnings: list[str] = Field(default_factory=list)

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
    display_name: str | None = None
    source_kinds: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def populate_dataset_defaults(cls, data: Any) -> Any:
        if isinstance(data, dict):
            dataset_name = data.get("dataset_name")
            namespace = data.get("namespace")
            canonical_name = data.get("canonical_name")
            if dataset_name and not canonical_name:
                data["canonical_name"] = f"{namespace}.{dataset_name}" if namespace else dataset_name
            if dataset_name and not data.get("display_name"):
                data["display_name"] = dataset_name
        return data

    @model_validator(mode="after")
    def finalize_dataset_identity(self) -> "DatasetNode":
        if self.node_id is None:
            self.node_id = build_dataset_id(self.canonical_name)
        return self


class TransformationNode(GraphNodeBase):
    kind: Literal[NodeKind.TRANSFORMATION] = NodeKind.TRANSFORMATION
    transformation_name: str
    operation_type: str | None = None
    module_or_file_id: str | None = None
    transformation_kind: str | None = None
    display_name: str | None = None
    warnings: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def populate_transformation_defaults(cls, data: Any) -> Any:
        if isinstance(data, dict):
            transformation_name = data.get("transformation_name")
            if transformation_name and not data.get("canonical_name"):
                data["canonical_name"] = transformation_name
            if transformation_name and not data.get("display_name"):
                data["display_name"] = transformation_name
        return data

    @model_validator(mode="after")
    def finalize_transformation_identity(self) -> "TransformationNode":
        if self.node_id is None:
            identity_path = self.path or self.module_or_file_id or self.canonical_name
            self.node_id = build_transformation_id(identity_path, self.canonical_name)
        return self


GraphNode = ModuleNode | DatasetNode | TransformationNode


class GraphEdge(BaseModel):
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
            self.edge_id = build_edge_id(self.kind, source_node_id=self.source_node_id, target_node_id=self.target_node_id)
        return self


class GraphPayload(BaseModel):
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


class SurveyHub(BaseModel):
    model_config = ConfigDict(extra="forbid")
    module_id: str
    relative_path: str
    score: float

    @field_validator("relative_path")
    @classmethod
    def validate_relative_path(cls, value: str) -> str:
        return normalize_relative_path(value)


class SurveyCycle(BaseModel):
    model_config = ConfigDict(extra="forbid")
    module_ids: list[str]
    relative_paths: list[str]

    @field_serializer("module_ids")
    def serialize_module_ids(self, value: list[str]) -> list[str]:
        return sorted(value)

    @field_serializer("relative_paths")
    def serialize_relative_paths(self, value: list[str]) -> list[str]:
        return sorted(normalize_relative_path(path) for path in value)


class VelocityRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    module_id: str
    relative_path: str
    lookback_days: int
    change_count: int
    is_high_velocity_core: bool = False

    @field_validator("relative_path")
    @classmethod
    def validate_relative_path(cls, value: str) -> str:
        return normalize_relative_path(value)


class DeadCodeCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    module_id: str
    relative_path: str
    reason_codes: list[str] = Field(default_factory=list)
    confidence: ConfidenceBand = ConfidenceBand.LOW
    evidence: list[EvidenceRecord] = Field(default_factory=list)

    @field_validator("relative_path")
    @classmethod
    def validate_relative_path(cls, value: str) -> str:
        return normalize_relative_path(value)

    @field_serializer("reason_codes")
    def serialize_reason_codes(self, value: list[str]) -> list[str]:
        return sorted(value)


class SurveySummaryPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: str = "1.0"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    run_id: str
    analysis_root: str
    module_count: int
    import_edge_count: int
    circular_dependency_group_count: int
    high_velocity_file_count: int
    high_velocity_core_count: int
    dead_code_candidate_count: int
    top_hubs: list[SurveyHub] = Field(default_factory=list)
    circular_dependencies: list[SurveyCycle] = Field(default_factory=list)
    high_velocity_files: list[VelocityRecord] = Field(default_factory=list)
    dead_code_candidates: list[DeadCodeCandidate] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    partial_result_flags: list[str] = Field(default_factory=list)
    stats: dict[str, Any] = Field(default_factory=dict)

    @field_validator("analysis_root")
    @classmethod
    def validate_analysis_root(cls, value: str) -> str:
        return value.replace("\\", "/")

    @field_serializer("top_hubs")
    def serialize_top_hubs(self, value: list[SurveyHub]) -> list[dict[str, Any]]:
        ordered = sorted(value, key=lambda item: (-item.score, item.relative_path, item.module_id))
        return [canonicalize_json_value(item.model_dump(mode="json")) for item in ordered]

    @field_serializer("circular_dependencies")
    def serialize_cycles(self, value: list[SurveyCycle]) -> list[dict[str, Any]]:
        ordered = sorted(value, key=lambda item: tuple(item.relative_paths))
        return [canonicalize_json_value(item.model_dump(mode="json")) for item in ordered]

    @field_serializer("high_velocity_files")
    def serialize_velocity(self, value: list[VelocityRecord]) -> list[dict[str, Any]]:
        ordered = sorted(value, key=lambda item: (-item.change_count, item.relative_path, item.module_id))
        return [canonicalize_json_value(item.model_dump(mode="json")) for item in ordered]

    @field_serializer("dead_code_candidates")
    def serialize_dead_code(self, value: list[DeadCodeCandidate]) -> list[dict[str, Any]]:
        ordered = sorted(value, key=lambda item: (item.relative_path, item.module_id))
        return [canonicalize_json_value(item.model_dump(mode="json")) for item in ordered]

    @field_serializer("warnings")
    def serialize_warnings(self, value: list[str]) -> list[str]:
        return sorted(dict.fromkeys(value))

    @field_serializer("partial_result_flags")
    def serialize_partial_flags(self, value: list[str]) -> list[str]:
        return sorted(dict.fromkeys(value))

    @field_serializer("stats")
    def serialize_stats(self, value: dict[str, Any]) -> dict[str, Any]:
        return canonicalize_json_value(value)


class LineageSummaryPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: str = "1.0"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    run_id: str
    analysis_root: str
    dataset_count: int
    transformation_count: int
    edge_count: int
    sql_signal_count: int
    python_signal_count: int
    yaml_signal_count: int
    warnings: list[str] = Field(default_factory=list)
    partial_result_flags: list[str] = Field(default_factory=list)
    stats: dict[str, Any] = Field(default_factory=dict)

    @field_validator("analysis_root")
    @classmethod
    def validate_analysis_root(cls, value: str) -> str:
        return value.replace("\\", "/")

    @field_serializer("warnings")
    def serialize_warnings(self, value: list[str]) -> list[str]:
        return sorted(dict.fromkeys(value))

    @field_serializer("partial_result_flags")
    def serialize_partial_flags(self, value: list[str]) -> list[str]:
        return sorted(dict.fromkeys(value))

    @field_serializer("stats")
    def serialize_stats(self, value: dict[str, Any]) -> dict[str, Any]:
        return canonicalize_json_value(value)
