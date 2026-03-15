"""Repository preparation through Archivist orchestration."""

from __future__ import annotations

import os
from pathlib import Path

from src.agents.archivist import ArchivistAgent
from src.agents.hydrologist import HydrologistAgent
from src.agents.navigator import NavigatorAgent
from src.agents.semanticist import SemanticistAgent
from src.agents.surveyor import SurveyorAgent
from src.analyzers.repository_manifest import build_repository_manifest
from src.analyzers.tree_sitter_analyzer import TreeSitterAnalyzer
from src.config import AppSettings
from src.models.archivist import SemanticIndexSnapshot
from src.models.graph import GraphPayload, LineageSummaryPayload, SurveySummaryPayload
from src.models.manifest import RepositoryManifest
from src.models.navigator import NavigatorRequest
from src.models.run_metadata import RunStatus, RunSummary
from src.models.semantic import DayOneAnswersPayload, DocumentationDriftPayload, DomainMapPayload, ModuleSemanticsPayload
from src.models.structural import AstIndexPayload, StructuralIndexPayload
from src.utils.incremental import load_latest_successful_summary, plan_incremental_refresh
from src.utils.repository_preparation import prepare_repository
from src.utils.artifacts import (
    create_run_context,
    finalize_run,
    initialize_artifact_dirs,
    mirror_artifact,
    write_archivist_artifacts,
    write_hydrologist_artifacts,
    write_inventory_artifacts,
    write_semanticist_artifacts,
    write_surveyor_artifacts,
    write_structural_artifacts,
)
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
        incremental_plan = plan_incremental_refresh(self.settings.repo_root, directories['runs'])
        previous_summary, previous_run_dir = load_latest_successful_summary(directories['runs'])
        reused_artifact_paths: list[str] = []
        regenerated_artifact_paths: list[str] = []

        manifest: RepositoryManifest
        structural_index: StructuralIndexPayload
        ast_index: AstIndexPayload
        module_graph: GraphPayload
        survey_summary: SurveySummaryPayload
        lineage_graph: GraphPayload
        lineage_summary: LineageSummaryPayload
        module_semantics: ModuleSemanticsPayload
        documentation_drift: DocumentationDriftPayload
        domain_map: DomainMapPayload
        day_one_answers: DayOneAnswersPayload

        if incremental_plan.reuse_inventory and previous_run_dir is not None:
            manifest = RepositoryManifest.model_validate_json((previous_run_dir / "manifest.json").read_text(encoding="utf-8"))
            reused_artifact_paths.extend(["manifest.json", "inventory_summary.json"])
        else:
            manifest = build_repository_manifest(self.settings)
            regenerated_artifact_paths.extend(["manifest.json", "inventory_summary.json"])
        manifest_path, summary_path = write_inventory_artifacts(run_dir, manifest, self.settings)

        if incremental_plan.reuse_structural and previous_run_dir is not None:
            structural_index = StructuralIndexPayload.model_validate_json((previous_run_dir / "structural_index.json").read_text(encoding="utf-8"))
            ast_index = AstIndexPayload.model_validate_json((previous_run_dir / "ast_index.json").read_text(encoding="utf-8"))
            reused_artifact_paths.extend(["structural_index.json", "ast_index.json", "structural_summary.json"])
        else:
            structural_index, ast_index = TreeSitterAnalyzer().analyze_manifest(
                prepared_repository,
                manifest,
                run_id=context.run_id,
                artifact_dir=str(self.settings.resolved_artifact_dir()),
            )
            regenerated_artifact_paths.extend(["structural_index.json", "ast_index.json", "structural_summary.json"])
        structural_index_path, ast_index_path, structural_summary_path = write_structural_artifacts(run_dir, structural_index, ast_index, self.settings)

        if incremental_plan.reuse_surveyor and previous_run_dir is not None:
            module_graph = GraphPayload.model_validate_json((previous_run_dir / "module_graph.json").read_text(encoding="utf-8"))
            survey_summary = SurveySummaryPayload.model_validate_json((previous_run_dir / "survey_summary.json").read_text(encoding="utf-8"))
            reused_artifact_paths.extend(["module_graph.json", "survey_summary.json"])
        else:
            module_graph, survey_summary = SurveyorAgent(self.settings).analyze(
                prepared_repository,
                manifest,
                structural_index,
                run_id=context.run_id,
                artifact_dir=str(self.settings.resolved_artifact_dir()),
            )
            regenerated_artifact_paths.extend(["module_graph.json", "survey_summary.json"])
        module_graph_path, survey_summary_path = write_surveyor_artifacts(run_dir, module_graph, survey_summary, self.settings)

        if incremental_plan.reuse_hydrologist and previous_run_dir is not None:
            lineage_graph = GraphPayload.model_validate_json((previous_run_dir / "lineage_graph.json").read_text(encoding="utf-8"))
            lineage_summary = LineageSummaryPayload.model_validate_json((previous_run_dir / "lineage_summary.json").read_text(encoding="utf-8"))
            reused_artifact_paths.extend(["lineage_graph.json", "lineage_summary.json"])
        else:
            lineage_graph, lineage_summary = HydrologistAgent(self.settings).analyze(
                prepared_repository,
                manifest,
                structural_index,
                module_graph,
                run_id=context.run_id,
                artifact_dir=str(self.settings.resolved_artifact_dir()),
            )
            regenerated_artifact_paths.extend(["lineage_graph.json", "lineage_summary.json"])
        lineage_graph_path, lineage_summary_path = write_hydrologist_artifacts(run_dir, lineage_graph, lineage_summary, self.settings)

        if incremental_plan.reuse_semanticist and previous_run_dir is not None:
            module_semantics = ModuleSemanticsPayload.model_validate_json((previous_run_dir / "module_semantics.json").read_text(encoding="utf-8"))
            documentation_drift = DocumentationDriftPayload.model_validate_json((previous_run_dir / "documentation_drift.json").read_text(encoding="utf-8"))
            domain_map = DomainMapPayload.model_validate_json((previous_run_dir / "domain_map.json").read_text(encoding="utf-8"))
            day_one_answers = DayOneAnswersPayload.model_validate_json((previous_run_dir / "day_one_answers.json").read_text(encoding="utf-8"))
            reused_artifact_paths.extend(["module_semantics.json", "documentation_drift.json", "domain_map.json", "day_one_answers.json"])
        else:
            semantic_result = SemanticistAgent(self.settings).analyze(
                prepared_repository,
                manifest,
                structural_index,
                module_graph,
                lineage_graph,
                run_id=context.run_id,
                artifact_dir=str(self.settings.resolved_artifact_dir()),
                logger=logger,
            )
            module_semantics = semantic_result.module_semantics
            documentation_drift = semantic_result.documentation_drift
            domain_map = semantic_result.domain_map
            day_one_answers = semantic_result.day_one_answers
            regenerated_artifact_paths.extend(["module_semantics.json", "documentation_drift.json", "domain_map.json", "day_one_answers.json"])
        module_semantics_path, documentation_drift_path, domain_map_path, day_one_answers_path = write_semanticist_artifacts(
            run_dir,
            module_semantics,
            documentation_drift,
            domain_map,
            day_one_answers,
            self.settings,
        )

        if incremental_plan.reuse_archivist and previous_run_dir is not None:
            for name in ("CODEBASE.md", "onboarding_brief.md", "cartography_trace.jsonl", "incremental_baseline.json"):
                source = previous_run_dir / name
                if source.exists():
                    mirror_artifact(source, run_dir / name)
            semantic_index_source = previous_run_dir / "semantic_index"
            if semantic_index_source.exists():
                mirror_artifact(semantic_index_source, run_dir / "semantic_index")
            codebase_md_path = self.settings.codebase_md_path(run_dir)
            onboarding_brief_path = self.settings.onboarding_brief_path(run_dir)
            trace_log_path = self.settings.trace_log_path(run_dir)
            incremental_baseline_path = self.settings.incremental_baseline_path(run_dir)
            semantic_index_path = self.settings.semantic_index_dir(run_dir)
            mirror_artifact(codebase_md_path, self.settings.latest_codebase_md_path())
            mirror_artifact(onboarding_brief_path, self.settings.latest_onboarding_brief_path())
            mirror_artifact(lineage_graph_path, self.settings.latest_lineage_graph_path())
            if semantic_index_path.exists():
                mirror_artifact(semantic_index_path, self.settings.latest_semantic_index_dir())
            if trace_log_path.exists():
                mirror_artifact(trace_log_path, self.settings.latest_trace_log_path())
            reused_artifact_paths.extend(["CODEBASE.md", "onboarding_brief.md", "semantic_index", "cartography_trace.jsonl", "incremental_baseline.json"])
            semantic_index_snapshot = SemanticIndexSnapshot.model_validate_json((semantic_index_path / "snapshot.json").read_text(encoding="utf-8"))
            archivist_warning_codes: list[str] = ["incremental_archivist_reuse"]
            archivist_partial_flags: list[str] = []
            trace_event_ids: list[str] = []
        else:
            archivist_result = ArchivistAgent(self.settings).analyze(
                repo_root=self.settings.repo_root,
                run_id=context.run_id,
                artifact_dir=str(self.settings.resolved_artifact_dir()),
                run_dir=run_dir,
                module_graph=module_graph,
                survey_summary=survey_summary,
                lineage_graph=lineage_graph,
                module_semantics=module_semantics,
                documentation_drift=documentation_drift,
                domain_map=domain_map,
                day_one_answers=day_one_answers,
                reused_artifact_paths=reused_artifact_paths,
                regenerated_artifact_paths=regenerated_artifact_paths,
                logger=logger,
            )
            archivist_bundle = write_archivist_artifacts(
                run_dir,
                codebase_md=archivist_result.codebase_markdown,
                onboarding_brief_md=archivist_result.onboarding_markdown,
                lineage_graph=lineage_graph,
                semantic_index_snapshot=archivist_result.semantic_index_snapshot,
                trace_log_path=self.settings.trace_log_path(run_dir),
                incremental_baseline=archivist_result.incremental_baseline,
                settings=self.settings,
                reused_artifact_paths=reused_artifact_paths,
                regenerated_artifact_paths=regenerated_artifact_paths,
                partial_result_flags=archivist_result.partial_result_flags,
                warning_codes=archivist_result.warning_codes,
            )
            codebase_md_path = Path(archivist_bundle.codebase_md_path)
            onboarding_brief_path = Path(archivist_bundle.onboarding_brief_path)
            semantic_index_path = Path(archivist_bundle.semantic_index_path)
            trace_log_path = Path(archivist_bundle.trace_log_path)
            incremental_baseline_path = Path(archivist_bundle.incremental_baseline_path)
            semantic_index_snapshot = archivist_result.semantic_index_snapshot
            archivist_warning_codes = archivist_result.warning_codes
            archivist_partial_flags = archivist_result.partial_result_flags
            trace_event_ids = archivist_result.trace_event_ids
            regenerated_artifact_paths.extend(["CODEBASE.md", "onboarding_brief.md", "semantic_index", "cartography_trace.jsonl", "incremental_baseline.json"])

        summary = RunSummary(
            run_id=context.run_id,
            status=RunStatus.COMPLETED,
            message='Stage 7 Archivist analysis completed with final living artifacts, semantic retrieval, and Navigator-ready outputs.',
            prepared_repo_path=prepared_repository.local_repo_path,
            manifest_path=str(manifest_path),
            inventory_summary_path=str(summary_path),
            structural_summary_path=str(structural_summary_path),
            module_graph_path=str(module_graph_path),
            survey_summary_path=str(survey_summary_path),
            lineage_graph_path=str(lineage_graph_path),
            lineage_summary_path=str(lineage_summary_path),
            module_semantics_path=str(module_semantics_path),
            documentation_drift_path=str(documentation_drift_path),
            domain_map_path=str(domain_map_path),
            day_one_answers_path=str(day_one_answers_path),
            codebase_md_path=str(codebase_md_path),
            onboarding_brief_path=str(onboarding_brief_path),
            semantic_index_path=str(semantic_index_path),
            trace_log_path=str(trace_log_path),
            incremental_baseline_path=str(incremental_baseline_path),
            artifact_paths=[
                str(manifest_path),
                str(summary_path),
                str(structural_index_path),
                str(ast_index_path),
                str(structural_summary_path),
                str(module_graph_path),
                str(survey_summary_path),
                str(lineage_graph_path),
                str(lineage_summary_path),
                str(module_semantics_path),
                str(documentation_drift_path),
                str(domain_map_path),
                str(day_one_answers_path),
                str(codebase_md_path),
                str(onboarding_brief_path),
                str(semantic_index_path),
                str(trace_log_path),
                str(incremental_baseline_path),
            ],
            warnings=[
                f'skipped:{manifest.summary.skipped_count}',
                f'unsupported:{manifest.summary.unsupported_count}',
                f'partial:{manifest.summary.partial_count}',
                f'structural_partial:{structural_index.summary.partial_files}',
                *survey_summary.partial_result_flags,
                *lineage_summary.partial_result_flags,
                *module_semantics.ledger.warning_codes,
                *incremental_plan.warning_codes,
                *archivist_warning_codes,
            ],
            inventory_stats={'total_candidates': manifest.summary.total_candidates, 'supported_count': manifest.summary.supported_count, 'partial_count': manifest.summary.partial_count, 'unsupported_count': manifest.summary.unsupported_count, 'skipped_count': manifest.summary.skipped_count, 'parse_eligible_count': manifest.summary.parse_eligible_count, 'bytes_considered': manifest.summary.bytes_considered, 'bytes_scanned': manifest.summary.bytes_scanned},
            structural_stats={'total_files': structural_index.summary.total_files, 'parsed_files': structural_index.summary.parsed_files, 'partial_files': structural_index.summary.partial_files, 'skipped_files': structural_index.summary.skipped_files, 'failed_files': structural_index.summary.failed_files, 'unsupported_files': structural_index.summary.unsupported_files, 'record_count': structural_index.summary.record_count},
            survey_stats={key: int(value) for key, value in survey_summary.stats.items() if isinstance(value, int)},
            lineage_stats={key: int(value) for key, value in lineage_summary.stats.items() if isinstance(value, int)},
            semantic_stats={
                'analyzed_module_count': module_semantics.ledger.analyzed_module_count,
                'partial_module_count': module_semantics.ledger.partial_module_count,
                'drift_record_count': module_semantics.ledger.drift_record_count,
                'domain_count': module_semantics.ledger.domain_count,
                'provider_request_count': module_semantics.ledger.provider_request_count,
            },
            archivist_stats={
                'semantic_index_entry_count': semantic_index_snapshot.entry_count,
                'trace_event_count': len(trace_event_ids),
                'reused_artifact_count': len(reused_artifact_paths),
                'regenerated_artifact_count': len(regenerated_artifact_paths),
            },
        )
        context.generated_artifact_paths = summary.artifact_paths
        finalize_run(context, run_dir, summary, status=RunStatus.COMPLETED)
        log_event(logger, event='run_completed', run_id=context.run_id, manifest_path=str(manifest_path), summary_path=str(summary_path), structural_index_path=str(structural_index_path), ast_index_path=str(ast_index_path), module_graph_path=str(module_graph_path), survey_summary_path=str(survey_summary_path), lineage_graph_path=str(lineage_graph_path), lineage_summary_path=str(lineage_summary_path), module_semantics_path=str(module_semantics_path), documentation_drift_path=str(documentation_drift_path), domain_map_path=str(domain_map_path), day_one_answers_path=str(day_one_answers_path), codebase_md_path=str(codebase_md_path), onboarding_brief_path=str(onboarding_brief_path), semantic_index_path=str(semantic_index_path), trace_log_path=str(trace_log_path), supported_count=manifest.summary.supported_count, partial_count=manifest.summary.partial_count, skipped_count=manifest.summary.skipped_count, unsupported_count=manifest.summary.unsupported_count, parse_eligible_count=manifest.summary.parse_eligible_count, structural_record_count=structural_index.summary.record_count, module_count=survey_summary.module_count, import_edge_count=survey_summary.import_edge_count, dataset_count=lineage_summary.dataset_count, transformation_count=lineage_summary.transformation_count, lineage_edge_count=lineage_summary.edge_count, semantic_module_count=module_semantics.ledger.analyzed_module_count, drift_record_count=module_semantics.ledger.drift_record_count, domain_count=module_semantics.ledger.domain_count, reused_artifact_count=len(reused_artifact_paths))
        for handler in list(logger.handlers):
            handler.close()
            logger.removeHandler(handler)
        return summary

    def query(
        self,
        question: str,
        *,
        query_type: str | None = None,
        target_identifier: str | None = None,
        direction: str | None = None,
        include_inference: bool = True,
        max_results: int = 5,
        run_id: str | None = None,
    ) -> str:
        response = NavigatorAgent(self.settings).query(
            NavigatorRequest(
                query_type=query_type,  # type: ignore[arg-type]
                query_text=question,
                target_identifier=target_identifier,
                direction=direction,  # type: ignore[arg-type]
                include_inference=include_inference,
                max_results=max_results,
                run_id=run_id,
            )
        )
        return response.model_dump_json(indent=2)


Stage0Orchestrator = CartographyOrchestrator
