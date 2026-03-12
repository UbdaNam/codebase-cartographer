"""Hydrologist lineage graph helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
import re

import networkx as nx

from src.models.enums import AnalysisMethod, ConfidenceBand, EdgeKind, SupportStatus
from src.models.evidence import EvidenceRecord
from src.models.graph import DatasetNode, GraphEdge, TransformationNode
from src.utils.ids import (
    build_dataset_id,
    build_lineage_signal_id,
    build_transformation_id,
    canonicalize_name,
    normalize_relative_path,
)


@dataclass(frozen=True)
class LineageSignal:
    source_kind: str
    file_path: str
    dataset_name: str
    role: str
    language: str
    line_start: int | None = None
    line_end: int | None = None
    transformation_name: str | None = None
    module_or_file_id: str | None = None
    analysis_method: AnalysisMethod = AnalysisMethod.STATIC_ANALYSIS
    confidence: ConfidenceBand = ConfidenceBand.MEDIUM
    is_partial: bool = False
    warnings: tuple[str, ...] = field(default_factory=tuple)

    @property
    def signal_id(self) -> str:
        return build_lineage_signal_id(self.file_path, self.dataset_name, self.source_kind, self.line_start)


def normalize_dataset_identifier(raw: str) -> str:
    cleaned = raw.strip().strip("`\"'[]()")
    cleaned = cleaned.replace("`", "")
    cleaned = cleaned.replace('"', "")
    cleaned = cleaned.replace("'", "")
    cleaned = cleaned.replace("\\", "/").replace(":", ".")
    cleaned = re.sub(r"\s+", "", cleaned)
    cleaned = cleaned.rstrip(";")
    if cleaned.startswith("./"):
        cleaned = cleaned[2:]
    cleaned = cleaned.replace("/", ".")
    cleaned = re.sub(r"\.{2,}", ".", cleaned)
    return canonicalize_name(cleaned).replace(" ", "")


def line_number_for_offset(content: str, offset: int) -> int:
    return content.count("\n", 0, offset) + 1


def build_signal_evidence(signal: LineageSignal) -> EvidenceRecord:
    return EvidenceRecord(
        source_path=signal.file_path,
        line_start=signal.line_start,
        line_end=signal.line_end,
        language=signal.language,
        analysis_method=signal.analysis_method,
        confidence=signal.confidence,
        symbol_name=signal.transformation_name,
        content_redacted=False,
    )


def build_dataset_node(dataset_name: str, signals: list[LineageSignal]) -> DatasetNode:
    canonical_name = normalize_dataset_identifier(dataset_name)
    first = signals[0]
    return DatasetNode(
        node_id=build_dataset_id(canonical_name),
        dataset_name=canonical_name.split(".")[-1],
        canonical_name=canonical_name,
        namespace=".".join(canonical_name.split(".")[:-1]) or None,
        display_name=dataset_name,
        language_or_dialect=first.language,
        support_status=SupportStatus.PARTIAL if any(signal.is_partial for signal in signals) else SupportStatus.SUPPORTED,
        confidence=ConfidenceBand.LOW if any(signal.is_partial for signal in signals) else first.confidence,
        evidence=[build_signal_evidence(signal) for signal in signals],
        source_kinds=sorted({signal.source_kind for signal in signals}),
        warnings=sorted({warning for signal in signals for warning in signal.warnings}),
        metadata={"signal_ids": sorted(signal.signal_id for signal in signals)},
    )


def build_transformation_node(file_path: str, transformation_name: str, signals: list[LineageSignal], *, module_or_file_id: str | None = None) -> TransformationNode:
    normalized_file = normalize_relative_path(file_path)
    partial = any(signal.is_partial for signal in signals)
    operation_type = "/".join(sorted({signal.source_kind for signal in signals}))
    return TransformationNode(
        node_id=build_transformation_id(normalized_file, transformation_name),
        transformation_name=transformation_name,
        canonical_name=f"{normalized_file}:{transformation_name}",
        display_name=transformation_name,
        path=normalized_file,
        module_or_file_id=module_or_file_id,
        transformation_kind=operation_type,
        operation_type=operation_type,
        language_or_dialect=signals[0].language,
        support_status=SupportStatus.PARTIAL if partial else SupportStatus.SUPPORTED,
        confidence=ConfidenceBand.LOW if partial else signals[0].confidence,
        evidence=[build_signal_evidence(signal) for signal in signals],
        warnings=sorted({warning for signal in signals for warning in signal.warnings}),
        metadata={"signal_ids": sorted(signal.signal_id for signal in signals)},
    )


def build_lineage_edges(dataset_nodes: dict[str, DatasetNode], transformation_nodes: dict[str, TransformationNode], signals: list[LineageSignal]) -> list[GraphEdge]:
    del dataset_nodes, transformation_nodes
    grouped: dict[tuple[str, str, str], list[LineageSignal]] = {}
    for signal in signals:
        dataset_id = build_dataset_id(normalize_dataset_identifier(signal.dataset_name))
        transformation_id = build_transformation_id(signal.file_path, signal.transformation_name or normalize_relative_path(signal.file_path))
        kind = EdgeKind.CONSUMES if signal.role == "input" else EdgeKind.PRODUCES
        source_id, target_id = (dataset_id, transformation_id) if signal.role == "input" else (transformation_id, dataset_id)
        grouped.setdefault((source_id, target_id, kind.value), []).append(signal)

    edges: dict[str, GraphEdge] = {}
    for (source_id, target_id, kind_value), bucket in grouped.items():
        partial = any(signal.is_partial for signal in bucket)
        edge = GraphEdge(
            source_node_id=source_id,
            target_node_id=target_id,
            kind=EdgeKind(kind_value),
            analysis_method=AnalysisMethod.STATIC_ANALYSIS if all(signal.analysis_method == AnalysisMethod.STATIC_ANALYSIS for signal in bucket) else AnalysisMethod.HEURISTIC,
            confidence=ConfidenceBand.LOW if partial else bucket[0].confidence,
            evidence=[build_signal_evidence(signal) for signal in bucket],
            support_status=SupportStatus.PARTIAL if partial else SupportStatus.SUPPORTED,
            metadata={
                "signal_ids": sorted(signal.signal_id for signal in bucket),
                "source_kinds": sorted({signal.source_kind for signal in bucket}),
            },
        )
        edges[edge.edge_id] = edge
    return [edges[key] for key in sorted(edges)]


def build_lineage_graph(dataset_nodes: list[DatasetNode], transformation_nodes: list[TransformationNode], edges: list[GraphEdge]) -> nx.DiGraph:
    graph = nx.DiGraph()
    for node in sorted(dataset_nodes + transformation_nodes, key=lambda item: item.node_id or ""):
        graph.add_node(node.node_id, kind=node.kind.value, canonical_name=node.canonical_name)
    for edge in sorted(edges, key=lambda item: item.edge_id or ""):
        graph.add_edge(edge.source_node_id, edge.target_node_id, kind=edge.kind.value)
    return graph
