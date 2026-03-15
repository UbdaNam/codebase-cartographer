"""Artifact and run-metadata helpers."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
import shutil
from uuid import uuid4

from src.config import AppSettings
from src.models.archivist import ArchivistArtifactBundle, IncrementalBaseline
from src.models.graph import GraphPayload, LineageSummaryPayload, SurveySummaryPayload
from src.models.manifest import RepositoryManifest
from src.models.run_metadata import RunContext, RunStatus, RunSummary
from src.models.semantic import DayOneAnswersPayload, DocumentationDriftPayload, DomainMapPayload, ModuleSemanticsPayload
from src.models.structural import AstIndexPayload, StructuralIndexPayload


def initialize_artifact_dirs(settings: AppSettings) -> dict[str, Path]:
    """Create and return deterministic artifact directories."""

    root = settings.resolved_artifact_dir()
    runs = root / settings.runs_dir_name
    cache = root / settings.cache_dir_name
    logs = root / settings.logs_dir_name
    repos = root / settings.repos_dir_name
    for directory in (root, runs, cache, logs, repos):
        directory.mkdir(parents=True, exist_ok=True)
    return {"root": root, "runs": runs, "cache": cache, "logs": logs, "repos": repos}


def create_run_context(settings: AppSettings, branch: str = "local") -> tuple[RunContext, Path]:
    """Create a new run context and its directory."""

    directories = initialize_artifact_dirs(settings)
    run_id = uuid4().hex[:12]
    run_dir = directories["runs"] / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    summary_path = run_dir / "run_summary.json"
    context = RunContext(
        run_id=run_id,
        started_at=datetime.now(UTC),
        branch=branch,
        repo_root=str(settings.repo_root),
        artifact_root=str(directories["root"]),
        status=RunStatus.RUNNING,
        summary_path=str(summary_path),
    )
    return context, run_dir


def write_json(path: Path, model: object) -> None:
    """Write a model or primitive payload with deterministic formatting."""

    if hasattr(model, "model_dump"):
        payload = model.model_dump(mode="json")
    else:
        payload = model
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def finalize_run(
    context: RunContext,
    run_dir: Path,
    summary: RunSummary,
    *,
    status: RunStatus = RunStatus.COMPLETED,
) -> RunContext:
    """Update and persist final run metadata."""

    context.finished_at = datetime.now(UTC)
    context.status = status
    write_json(run_dir / "run_metadata.json", context)
    write_json(Path(context.summary_path), summary)
    return context


def write_inventory_artifacts(
    run_dir: Path,
    manifest: RepositoryManifest,
    settings: AppSettings,
) -> tuple[Path, Path]:
    """Persist the Stage 2 inventory manifest and summary artifacts."""

    manifest_path = run_dir / "manifest.json"
    summary_path = settings.inventory_summary_path(run_dir)
    write_json(manifest_path, manifest)
    write_json(summary_path, manifest.summary)
    return manifest_path, summary_path


def write_structural_artifacts(
    run_dir: Path,
    structural_index: StructuralIndexPayload,
    ast_index: AstIndexPayload,
    settings: AppSettings,
) -> tuple[Path, Path, Path]:
    """Persist Stage 3 structural artifacts and summary."""

    structural_index_path = run_dir / "structural_index.json"
    ast_index_path = run_dir / "ast_index.json"
    structural_summary_path = settings.structural_summary_path(run_dir)
    write_json(structural_index_path, structural_index)
    write_json(ast_index_path, ast_index)
    write_json(structural_summary_path, structural_index.summary)
    return structural_index_path, ast_index_path, structural_summary_path


def write_surveyor_artifacts(
    run_dir: Path,
    module_graph: GraphPayload,
    survey_summary: SurveySummaryPayload,
    settings: AppSettings,
) -> tuple[Path, Path]:
    """Persist Stage 4 Surveyor artifacts and summary."""

    module_graph_path = settings.module_graph_path(run_dir)
    survey_summary_path = settings.survey_summary_path(run_dir)
    write_json(module_graph_path, module_graph)
    write_json(survey_summary_path, survey_summary)
    return module_graph_path, survey_summary_path


def write_hydrologist_artifacts(
    run_dir: Path,
    lineage_graph: GraphPayload,
    lineage_summary: LineageSummaryPayload,
    settings: AppSettings,
) -> tuple[Path, Path]:
    """Persist Stage 5 Hydrologist artifacts and summary."""

    lineage_graph_path = settings.lineage_graph_path(run_dir)
    lineage_summary_path = settings.lineage_summary_path(run_dir)
    write_json(lineage_graph_path, lineage_graph)
    write_json(lineage_summary_path, lineage_summary)
    return lineage_graph_path, lineage_summary_path


def write_semanticist_artifacts(
    run_dir: Path,
    module_semantics: ModuleSemanticsPayload,
    documentation_drift: DocumentationDriftPayload,
    domain_map: DomainMapPayload,
    day_one_answers: DayOneAnswersPayload,
    settings: AppSettings,
) -> tuple[Path, Path, Path, Path]:
    """Persist Stage 6 Semanticist artifacts."""

    module_semantics_path = settings.module_semantics_path(run_dir)
    documentation_drift_path = settings.documentation_drift_path(run_dir)
    domain_map_path = settings.domain_map_path(run_dir)
    day_one_answers_path = settings.day_one_answers_path(run_dir)
    write_json(module_semantics_path, module_semantics)
    write_json(documentation_drift_path, documentation_drift)
    write_json(domain_map_path, domain_map)
    write_json(day_one_answers_path, day_one_answers)
    return module_semantics_path, documentation_drift_path, domain_map_path, day_one_answers_path


def write_markdown(path: Path, content: str) -> None:
    """Persist markdown content with a trailing newline."""

    normalized = content.rstrip() + "\n"
    path.write_text(normalized, encoding="utf-8")


def mirror_artifact(source: Path, destination: Path) -> None:
    """Mirror a file or directory into the latest artifact location."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(source, destination)
        return
    shutil.copy2(source, destination)


def write_archivist_artifacts(
    run_dir: Path,
    *,
    codebase_md: str,
    onboarding_brief_md: str,
    lineage_graph: GraphPayload,
    semantic_index_snapshot: object,
    trace_log_path: Path,
    incremental_baseline: IncrementalBaseline,
    settings: AppSettings,
    reused_artifact_paths: list[str] | None = None,
    regenerated_artifact_paths: list[str] | None = None,
    partial_result_flags: list[str] | None = None,
    warning_codes: list[str] | None = None,
) -> ArchivistArtifactBundle:
    """Persist final-stage Archivist outputs and mirror the latest copies."""

    codebase_md_path = settings.codebase_md_path(run_dir)
    onboarding_brief_path = settings.onboarding_brief_path(run_dir)
    lineage_graph_path = settings.lineage_graph_path(run_dir)
    semantic_index_dir = settings.semantic_index_dir(run_dir)
    incremental_baseline_path = settings.incremental_baseline_path(run_dir)

    write_markdown(codebase_md_path, codebase_md)
    write_markdown(onboarding_brief_path, onboarding_brief_md)
    write_json(lineage_graph_path, lineage_graph)
    if hasattr(semantic_index_snapshot, "model_dump"):
        semantic_index_dir.mkdir(parents=True, exist_ok=True)
        write_json(semantic_index_dir / "snapshot.json", semantic_index_snapshot)
    write_json(incremental_baseline_path, incremental_baseline)

    mirror_artifact(codebase_md_path, settings.latest_codebase_md_path())
    mirror_artifact(onboarding_brief_path, settings.latest_onboarding_brief_path())
    mirror_artifact(lineage_graph_path, settings.latest_lineage_graph_path())
    mirror_artifact(semantic_index_dir, settings.latest_semantic_index_dir())
    if trace_log_path.exists():
        mirror_artifact(trace_log_path, settings.latest_trace_log_path())

    return ArchivistArtifactBundle(
        run_id=incremental_baseline.run_id,
        analysis_root=str(settings.repo_root).replace("\\", "/"),
        codebase_md_path=str(codebase_md_path),
        onboarding_brief_path=str(onboarding_brief_path),
        lineage_graph_path=str(lineage_graph_path),
        semantic_index_path=str(semantic_index_dir),
        trace_log_path=str(trace_log_path),
        incremental_baseline_path=str(incremental_baseline_path),
        reused_artifact_paths=reused_artifact_paths or [],
        regenerated_artifact_paths=regenerated_artifact_paths or [],
        partial_result_flags=partial_result_flags or [],
        warning_codes=warning_codes or [],
    )
