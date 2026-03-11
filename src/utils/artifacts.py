"""Artifact and run-metadata helpers."""

from __future__ import annotations

import json
from datetime import datetime, UTC
from pathlib import Path
from uuid import uuid4

from src.config import AppSettings
from src.models.run_metadata import RunContext, RunStatus, RunSummary


def initialize_artifact_dirs(settings: AppSettings) -> dict[str, Path]:
    """Create and return deterministic artifact directories."""

    root = settings.resolved_artifact_dir()
    runs = root / settings.runs_dir_name
    cache = root / settings.cache_dir_name
    logs = root / settings.logs_dir_name
    for directory in (root, runs, cache, logs):
        directory.mkdir(parents=True, exist_ok=True)
    return {"root": root, "runs": runs, "cache": cache, "logs": logs}


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
