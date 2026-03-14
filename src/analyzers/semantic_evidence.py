"""Evidence bundle generation for Semanticist."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterable

from src.config import AppSettings
from src.models.enums import AnalysisMethod, ConfidenceBand
from src.models.evidence import EvidenceRecord
from src.models.graph import DatasetNode, GraphPayload, ModuleNode, TransformationNode
from src.models.semantic import EvidenceReference, PurposeEvidenceBundle
from src.models.structural import StructuralFileResult, StructuralSymbolKind
from src.utils.ids import build_artifact_id, normalize_relative_path


def build_evidence_bundle(
    module_node: ModuleNode,
    structural_result: StructuralFileResult | None,
    lineage_graph: GraphPayload,
    repo_root: Path,
    settings: AppSettings,
) -> PurposeEvidenceBundle:
    source_path = repo_root / module_node.relative_path
    source_text = source_path.read_text(encoding="utf-8", errors="replace") if source_path.exists() else ""
    imports = list(module_node.import_targets[:12])
    public_api_signals = sorted(
        {
            record.symbol_name
            for record in (structural_result.records if structural_result else [])
            if record.symbol_kind in {StructuralSymbolKind.FUNCTION, StructuralSymbolKind.CLASS, StructuralSymbolKind.METHOD}
            and record.symbol_name
            and not record.symbol_name.startswith("_")
        }
    )
    code_excerpt_refs = list(_extract_code_excerpts(module_node.relative_path, source_text, structural_result, settings))
    documentation_refs = list(extract_documentation_refs(module_node.relative_path, source_text, repo_root))
    lineage_relationships = _collect_lineage_relationships(module_node, lineage_graph)
    bundle_id = build_artifact_id("semantic_bundle", logical_name=module_node.module_name, serialization_path=module_node.relative_path)
    return PurposeEvidenceBundle(
        bundle_id=bundle_id,
        module_id=module_node.node_id,
        module_path=module_node.relative_path,
        imports=imports,
        public_api_signals=public_api_signals,
        graph_metrics={
            "pagerank_score": module_node.pagerank_score,
            "inbound_import_count": module_node.inbound_import_count,
            "outbound_import_count": module_node.outbound_import_count,
            "public_symbol_count": module_node.public_symbol_count,
            "class_count": module_node.class_count,
            "function_count": module_node.function_count,
            "dead_code_candidate": module_node.dead_code_candidate,
            "high_velocity_core": module_node.is_high_velocity_core,
        },
        lineage_relationships=lineage_relationships,
        git_velocity_signals={
            "change_velocity_recent": module_node.change_velocity_recent or 0,
        },
        code_excerpt_refs=code_excerpt_refs,
        documentation_refs=documentation_refs,
        analysis_methods=[AnalysisMethod.STATIC_ANALYSIS, AnalysisMethod.GRAPH_INFERENCE],
    )


def extract_documentation_refs(relative_path: str, source_text: str, repo_root: Path) -> Iterable[EvidenceReference]:
    references: list[EvidenceReference] = []
    module_doc = _extract_python_module_docstring(source_text) if relative_path.endswith(".py") else None
    if module_doc:
        references.append(
            EvidenceReference(
                source_kind="module_docstring",
                repository_path=relative_path,
                line_start=1,
                line_end=max(1, module_doc.count("\n") + 1),
                quoted_text=module_doc[:400],
                observed_or_inferred="observed",
                analysis_method=AnalysisMethod.STATIC_ANALYSIS,
                confidence=ConfidenceBand.MEDIUM,
            )
        )
    readme_path = (repo_root / normalize_relative_path(relative_path)).parent / "README.md"
    if readme_path.exists():
        excerpt = readme_path.read_text(encoding="utf-8", errors="replace").strip()[:400]
        if excerpt:
            references.append(
                EvidenceReference(
                    source_kind="nearby_readme",
                    repository_path=normalize_relative_path(str(readme_path.relative_to(repo_root)).replace("\\", "/")),
                    line_start=1,
                    line_end=max(1, excerpt.count("\n") + 1),
                    quoted_text=excerpt,
                    observed_or_inferred="observed",
                    analysis_method=AnalysisMethod.STATIC_ANALYSIS,
                    confidence=ConfidenceBand.LOW,
                )
            )
    return references


def _extract_code_excerpts(
    relative_path: str,
    source_text: str,
    structural_result: StructuralFileResult | None,
    settings: AppSettings,
) -> Iterable[EvidenceReference]:
    if not source_text:
        return []
    source_lines = source_text.splitlines()
    emitted: list[EvidenceReference] = []
    candidates: list[EvidenceRecord] = []
    if structural_result:
        for record in structural_result.records:
            if record.symbol_kind in {StructuralSymbolKind.FUNCTION, StructuralSymbolKind.CLASS, StructuralSymbolKind.METHOD}:
                candidates.extend(record.evidence[:1])
    if not candidates:
        candidates.append(
            EvidenceRecord(
                source_path=relative_path,
                line_start=1,
                line_end=min(len(source_lines), settings.semantic_module_excerpt_lines),
                analysis_method=AnalysisMethod.STATIC_ANALYSIS,
                confidence=ConfidenceBand.LOW,
                content_redacted=False,
            )
        )
    for evidence in candidates[:4]:
        start = max((evidence.line_start or 1) - 1, 0)
        end = min(start + settings.semantic_module_excerpt_lines, len(source_lines))
        excerpt = "\n".join(source_lines[start:end]).strip()
        if not excerpt:
            continue
        emitted.append(
            EvidenceReference(
                source_kind="code_excerpt",
                artifact_path=None,
                repository_path=relative_path,
                line_start=start + 1,
                line_end=end,
                quoted_text=excerpt[:400],
                observed_or_inferred="observed",
                analysis_method=AnalysisMethod.STATIC_ANALYSIS,
                confidence=evidence.confidence,
            )
        )
    return emitted


def _extract_python_module_docstring(source_text: str) -> str | None:
    try:
        module = ast.parse(source_text)
    except SyntaxError:
        return None
    return ast.get_docstring(module)


def _collect_lineage_relationships(module_node: ModuleNode, lineage_graph: GraphPayload) -> dict[str, list[str]]:
    datasets_by_id = {
        node.node_id: node.canonical_name
        for node in lineage_graph.nodes
        if isinstance(node, DatasetNode)
    }
    transformation_ids = {
        node.node_id
        for node in lineage_graph.nodes
        if isinstance(node, TransformationNode)
        and (node.module_or_file_id == module_node.node_id or node.path == module_node.relative_path)
    }
    inputs: set[str] = set()
    outputs: set[str] = set()
    for edge in lineage_graph.edges:
        if edge.target_node_id in transformation_ids and edge.source_node_id in datasets_by_id:
            inputs.add(datasets_by_id[edge.source_node_id])
        if edge.source_node_id in transformation_ids and edge.target_node_id in datasets_by_id:
            outputs.add(datasets_by_id[edge.target_node_id])
    return {"inputs": sorted(inputs), "outputs": sorted(outputs)}
