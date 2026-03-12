"""Repository preparation, inventory, structural analysis, Surveyor, and Hydrologist orchestration."""

from __future__ import annotations

import os
from pathlib import Path

from src.agents.hydrologist import HydrologistAgent
from src.agents.surveyor import SurveyorAgent
from src.analyzers.repository_manifest import build_repository_manifest
from src.analyzers.tree_sitter_analyzer import TreeSitterAnalyzer
from src.config import AppSettings
from src.models.run_metadata import RunStatus, RunSummary
from src.utils.repository_preparation import prepare_repository
from src.utils.artifacts import create_run_context, finalize_run, initialize_artifact_dirs, write_hydrologist_artifacts, write_inventory_artifacts, write_surveyor_artifacts, write_structural_artifacts
from src.utils.logging import create_logger, log_event


class CartographyOrchestrator:
    def __init__(self, settings: AppSettings):
        self.settings = settings

    def analyze(self, repo: str | Path | None = None) -> RunSummary:
        self.settings.artifact_dir = self.settings.resolved_artifact_dir()
        repository_target = repo if repo is not None else self.settings.repo_root
        directories = initialize_artifact_dirs(self.settings)
        branch = os.getenv('SPECIFY_FEATURE', 'local')
        context, run_dir = create_run_context(self.settings, branch=branch)
        logger = create_logger(directories['logs'] / f'{context.run_id}.log', context.run_id)
        prepared_repository = prepare_repository(repository_target, self.settings)
        self.settings.repo_root = Path(prepared_repository.local_repo_path)
        context.repo_root = prepared_repository.local_repo_path
        log_event(logger, event='run_started', run_id=context.run_id, repo_root=str(self.settings.repo_root), prepared_repo_path=prepared_repository.local_repo_path, reuse_mode=prepared_repository.reuse_mode.value)

        manifest = build_repository_manifest(self.settings)
        manifest_path, summary_path = write_inventory_artifacts(run_dir, manifest, self.settings)
        structural_index, ast_index = TreeSitterAnalyzer().analyze_manifest(prepared_repository, manifest, run_id=context.run_id, artifact_dir=str(self.settings.resolved_artifact_dir()))
        structural_index_path, ast_index_path, structural_summary_path = write_structural_artifacts(run_dir, structural_index, ast_index, self.settings)
        module_graph, survey_summary = SurveyorAgent(self.settings).analyze(prepared_repository, manifest, structural_index, run_id=context.run_id, artifact_dir=str(self.settings.resolved_artifact_dir()))
        module_graph_path, survey_summary_path = write_surveyor_artifacts(run_dir, module_graph, survey_summary, self.settings)
        lineage_graph, lineage_summary = HydrologistAgent(self.settings).analyze(prepared_repository, manifest, structural_index, module_graph, run_id=context.run_id, artifact_dir=str(self.settings.resolved_artifact_dir()))
        lineage_graph_path, lineage_summary_path = write_hydrologist_artifacts(run_dir, lineage_graph, lineage_summary, self.settings)

        summary = RunSummary(
            run_id=context.run_id,
            status=RunStatus.COMPLETED,
            message='Stage 5 Hydrologist analysis completed with deterministic architectural and lineage artifacts.',
            prepared_repo_path=prepared_repository.local_repo_path,
            manifest_path=str(manifest_path),
            inventory_summary_path=str(summary_path),
            structural_summary_path=str(structural_summary_path),
            module_graph_path=str(module_graph_path),
            survey_summary_path=str(survey_summary_path),
            lineage_graph_path=str(lineage_graph_path),
            lineage_summary_path=str(lineage_summary_path),
            artifact_paths=[str(manifest_path), str(summary_path), str(structural_index_path), str(ast_index_path), str(structural_summary_path), str(module_graph_path), str(survey_summary_path), str(lineage_graph_path), str(lineage_summary_path)],
            warnings=[f'skipped:{manifest.summary.skipped_count}', f'unsupported:{manifest.summary.unsupported_count}', f'partial:{manifest.summary.partial_count}', f'structural_partial:{structural_index.summary.partial_files}', *survey_summary.partial_result_flags, *lineage_summary.partial_result_flags],
            inventory_stats={'total_candidates': manifest.summary.total_candidates, 'supported_count': manifest.summary.supported_count, 'partial_count': manifest.summary.partial_count, 'unsupported_count': manifest.summary.unsupported_count, 'skipped_count': manifest.summary.skipped_count, 'parse_eligible_count': manifest.summary.parse_eligible_count, 'bytes_considered': manifest.summary.bytes_considered, 'bytes_scanned': manifest.summary.bytes_scanned},
            structural_stats={'total_files': structural_index.summary.total_files, 'parsed_files': structural_index.summary.parsed_files, 'partial_files': structural_index.summary.partial_files, 'skipped_files': structural_index.summary.skipped_files, 'failed_files': structural_index.summary.failed_files, 'unsupported_files': structural_index.summary.unsupported_files, 'record_count': structural_index.summary.record_count},
            survey_stats={key: int(value) for key, value in survey_summary.stats.items() if isinstance(value, int)},
            lineage_stats={key: int(value) for key, value in lineage_summary.stats.items() if isinstance(value, int)},
        )
        context.generated_artifact_paths = summary.artifact_paths
        finalize_run(context, run_dir, summary, status=RunStatus.COMPLETED)
        log_event(logger, event='run_completed', run_id=context.run_id, manifest_path=str(manifest_path), summary_path=str(summary_path), structural_index_path=str(structural_index_path), ast_index_path=str(ast_index_path), module_graph_path=str(module_graph_path), survey_summary_path=str(survey_summary_path), lineage_graph_path=str(lineage_graph_path), lineage_summary_path=str(lineage_summary_path), supported_count=manifest.summary.supported_count, partial_count=manifest.summary.partial_count, skipped_count=manifest.summary.skipped_count, unsupported_count=manifest.summary.unsupported_count, parse_eligible_count=manifest.summary.parse_eligible_count, structural_record_count=structural_index.summary.record_count, module_count=survey_summary.module_count, import_edge_count=survey_summary.import_edge_count, dataset_count=lineage_summary.dataset_count, transformation_count=lineage_summary.transformation_count, lineage_edge_count=lineage_summary.edge_count)
        return summary

    def query(self, question: str) -> str:
        return f'Query support is not implemented in Stage 4. Received question: {question}'


Stage0Orchestrator = CartographyOrchestrator
