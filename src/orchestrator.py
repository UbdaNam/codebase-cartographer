"""Stage 0 orchestration shell."""

from __future__ import annotations

import os
from pathlib import Path

from src.analyzers.repository_manifest import build_repository_manifest
from src.config import AppSettings
from src.models.run_metadata import RunStatus, RunSummary
from src.utils.artifacts import create_run_context, finalize_run, initialize_artifact_dirs, write_json
from src.utils.logging import create_logger, log_event


class Stage0Orchestrator:
    """Coordinate Stage 0 analyze and query flows."""

    def __init__(self, settings: AppSettings):
        self.settings = settings

    def analyze(self, repo: str | Path | None = None) -> RunSummary:
        if repo is not None:
            self.settings.repo_root = Path(repo).resolve()

        directories = initialize_artifact_dirs(self.settings)
        branch = os.getenv("SPECIFY_FEATURE", "local")
        context, run_dir = create_run_context(self.settings, branch=branch)
        logger = create_logger(directories["logs"] / f"{context.run_id}.log", context.run_id)
        log_event(logger, event="run_started", run_id=context.run_id, repo_root=str(self.settings.repo_root))

        manifest = build_repository_manifest(self.settings)
        manifest_path = run_dir / "manifest.json"
        write_json(manifest_path, manifest)

        summary = RunSummary(
            run_id=context.run_id,
            status=RunStatus.COMPLETED,
            message="Stage 0 foundation run completed with manifest-only analysis.",
            manifest_path=str(manifest_path),
        )
        finalize_run(context, run_dir, summary, status=RunStatus.COMPLETED)
        log_event(
            logger,
            event="run_completed",
            run_id=context.run_id,
            manifest_path=str(manifest_path),
            supported_count=manifest.summary.supported_count,
            skipped_count=manifest.summary.skipped_count,
        )
        return summary

    def query(self, question: str) -> str:
        return (
            "Query support is not implemented in Stage 0. "
            f"Received question: {question}"
        )
