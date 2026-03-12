"""Surveyor agent for Stage 4 architectural analysis."""

from __future__ import annotations

from pathlib import Path

from src.config import AppSettings
from src.graph.survey import (
    GRAPH_LANGUAGES,
    build_import_edges,
    build_import_graph,
    build_module_node,
    compute_high_velocity_core,
    compute_pagerank,
    compute_strongly_connected_components,
    detect_dead_code_candidates,
    extract_git_velocity,
)
from src.models.enums import AnalysisMethod
from src.models.graph import GraphPayload, SurveySummaryPayload, VelocityRecord
from src.models.manifest import RepositoryManifest
from src.models.repository_input import PreparedRepository
from src.models.structural import ParseStatus, StructuralIndexPayload


class SurveyorAgent:
    """Consume structural outputs and emit module graph intelligence."""

    def __init__(self, settings: AppSettings):
        self.settings = settings

    def analyze(
        self,
        prepared_repository: PreparedRepository,
        manifest: RepositoryManifest,
        structural_index: StructuralIndexPayload,
        *,
        run_id: str,
        artifact_dir: str,
    ) -> tuple[GraphPayload, SurveySummaryPayload]:
        del manifest
        repo_root = Path(prepared_repository.local_repo_path)
        warnings: list[str] = []
        partial_flags: list[str] = []

        module_results = [
            result
            for result in structural_index.file_results
            if result.language in GRAPH_LANGUAGES and result.parse_status in {ParseStatus.PARSED, ParseStatus.PARTIAL}
        ]
        module_nodes = [build_module_node(result) for result in module_results]
        module_by_id = {node.node_id: node for node in module_nodes}

        edges, unresolved_imports, import_targets_by_path = build_import_edges(repo_root, module_nodes, module_results)
        for unresolved in unresolved_imports:
            warnings.append(f"unresolved_import:{unresolved.source_path}:{unresolved.target}")
        if unresolved_imports:
            partial_flags.append("unresolved_imports")

        for node in module_nodes:
            node.import_targets = import_targets_by_path.get(node.relative_path, [])

        graph = build_import_graph(module_nodes, edges)
        hubs = compute_pagerank(graph, module_by_id)
        cycles = compute_strongly_connected_components(graph, module_by_id)
        if (repo_root / ".git").exists():
            velocity_by_path, velocity_warnings = extract_git_velocity(
                repo_root,
                days=self.settings.git_velocity_lookback_days,
            )
        else:
            velocity_by_path, velocity_warnings = {}, ["git_velocity_unavailable:not_a_git_repo"]
        warnings.extend(velocity_warnings)
        if velocity_warnings:
            partial_flags.append("git_velocity_unavailable")

        module_id_by_path = {node.relative_path: node.node_id for node in module_nodes}
        high_velocity_core = compute_high_velocity_core(
            velocity_by_path,
            lookback_days=self.settings.git_velocity_lookback_days,
            change_share_threshold=self.settings.high_velocity_core_change_share,
            module_id_by_path=module_id_by_path,
        )
        high_velocity_paths = {record.relative_path for record in high_velocity_core}
        high_velocity_records = [
            VelocityRecord(
                module_id=module_id_by_path.get(path, path),
                relative_path=path,
                lookback_days=self.settings.git_velocity_lookback_days,
                change_count=count,
                is_high_velocity_core=path in high_velocity_paths,
            )
            for path, count in sorted(velocity_by_path.items(), key=lambda item: (-item[1], item[0]))
        ]

        dead_code_candidates = detect_dead_code_candidates(module_by_id, graph, velocity_by_path)
        dead_code_paths = {candidate.relative_path for candidate in dead_code_candidates}

        hub_scores = {hub.module_id: hub.score for hub in hubs}
        for node in module_nodes:
            node.pagerank_score = hub_scores.get(node.node_id)
            node.inbound_import_count = graph.in_degree(node.node_id)
            node.outbound_import_count = graph.out_degree(node.node_id)
            node.change_velocity_recent = velocity_by_path.get(node.relative_path)
            node.is_high_velocity_core = node.relative_path in high_velocity_paths
            node.dead_code_candidate = node.relative_path in dead_code_paths
            if node.relative_path in dead_code_paths:
                node.warnings.append("heuristic_dead_code_candidate")
            if any(item.source_path == node.relative_path for item in unresolved_imports):
                node.warnings.append("contains_unresolved_imports")

        graph_payload = GraphPayload(
            run_id=run_id,
            graph_metadata={
                "analysis_method": AnalysisMethod.GRAPH_INFERENCE.value,
                "analysis_root": prepared_repository.local_repo_path,
                "module_count": len(module_nodes),
                "import_edge_count": len(edges),
                "unresolved_import_count": len(unresolved_imports),
                "top_hubs": [hub.model_dump(mode="json") for hub in hubs[:10]],
                "circular_dependency_groups": [cycle.model_dump(mode="json") for cycle in cycles],
                "high_velocity_core": [record.model_dump(mode="json") for record in high_velocity_core],
                "warnings": sorted(dict.fromkeys(warnings)),
                "partial_result_flags": sorted(dict.fromkeys(partial_flags)),
                "artifact_dir": artifact_dir.replace("\\", "/"),
            },
            nodes=module_nodes,
            edges=edges,
        )

        summary_payload = SurveySummaryPayload(
            run_id=run_id,
            analysis_root=prepared_repository.local_repo_path,
            module_count=len(module_nodes),
            import_edge_count=len(edges),
            circular_dependency_group_count=len(cycles),
            high_velocity_file_count=len(high_velocity_records),
            high_velocity_core_count=len(high_velocity_core),
            dead_code_candidate_count=len(dead_code_candidates),
            top_hubs=hubs[:10],
            circular_dependencies=cycles,
            high_velocity_files=high_velocity_records,
            dead_code_candidates=dead_code_candidates,
            warnings=warnings,
            partial_result_flags=partial_flags,
            stats={
                "module_count": len(module_nodes),
                "import_edge_count": len(edges),
                "unresolved_import_count": len(unresolved_imports),
                "graph_node_count": graph.number_of_nodes(),
                "graph_edge_count": graph.number_of_edges(),
                "high_velocity_file_count": len(high_velocity_records),
                "high_velocity_core_count": len(high_velocity_core),
                "dead_code_candidate_count": len(dead_code_candidates),
            },
        )
        return graph_payload, summary_payload
