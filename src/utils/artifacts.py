"""Artifact and run-metadata helpers."""

from __future__ import annotations

import json
from datetime import datetime, UTC
from pathlib import Path
from uuid import uuid4

from src.config import AppSettings
from src.models.manifest import RepositoryManifest
from src.models.run_metadata import RunContext, RunStatus, RunSummary
from src.models.structural import AstIndexPayload, StructuralIndexPayload, StructuralSummary


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
