"""Repository inventory orchestration shell."""

from __future__ import annotations

import os
from pathlib import Path

from src.analyzers.repository_manifest import build_repository_manifest
from src.config import AppSettings
from src.models.run_metadata import RunStatus, RunSummary
from src.utils.artifacts import (
    create_run_context,
    finalize_run,
    initialize_artifact_dirs,
    write_inventory_artifacts,
)
from src.utils.logging import create_logger, log_event


class CartographyOrchestrator:
    """Coordinate Stage 2 inventory analyze and the placeholder query flow."""

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
        manifest_path, summary_path = write_inventory_artifacts(run_dir, manifest, self.settings)

        summary = RunSummary(
            run_id=context.run_id,
            status=RunStatus.COMPLETED,
            message="Stage 2 repository inventory completed with deterministic manifest output.",
            manifest_path=str(manifest_path),
            inventory_summary_path=str(summary_path),
            artifact_paths=[str(manifest_path), str(summary_path)],
            warnings=[
                f"skipped:{manifest.summary.skipped_count}",
                f"unsupported:{manifest.summary.unsupported_count}",
                f"partial:{manifest.summary.partial_count}",
            ],
            inventory_stats={
                "total_candidates": manifest.summary.total_candidates,
                "supported_count": manifest.summary.supported_count,
                "partial_count": manifest.summary.partial_count,
                "unsupported_count": manifest.summary.unsupported_count,
                "skipped_count": manifest.summary.skipped_count,
                "parse_eligible_count": manifest.summary.parse_eligible_count,
                "bytes_considered": manifest.summary.bytes_considered,
                "bytes_scanned": manifest.summary.bytes_scanned,
            },
        )
        context.generated_artifact_paths = [str(manifest_path), str(summary_path)]
        finalize_run(context, run_dir, summary, status=RunStatus.COMPLETED)
        log_event(
            logger,
            event="run_completed",
            run_id=context.run_id,
            manifest_path=str(manifest_path),
            summary_path=str(summary_path),
            supported_count=manifest.summary.supported_count,
            partial_count=manifest.summary.partial_count,
            skipped_count=manifest.summary.skipped_count,
            unsupported_count=manifest.summary.unsupported_count,
            parse_eligible_count=manifest.summary.parse_eligible_count,
        )
        return summary

    def query(self, question: str) -> str:
        return (
            "Query support is not implemented in Stage 2. "
            f"Received question: {question}"
        )


Stage0Orchestrator = CartographyOrchestrator
