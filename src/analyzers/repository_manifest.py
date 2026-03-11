"""Single-pass deterministic repository manifest builder."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from src.config import AppSettings
from src.models.manifest import (
    ManifestRecord,
    ManifestSummary,
    RepositoryManifest,
    ScanAction,
    SkipReason,
    SupportStatus,
)
from src.utils.file_classification import classify_path
from src.utils.ignore_policy import should_skip_path


def build_repository_manifest(settings: AppSettings) -> RepositoryManifest:
    """Walk the repository once and build a deterministic manifest."""

    records: list[ManifestRecord] = []
    summary = ManifestSummary()
    repo_root = settings.repo_root
    bytes_scanned = 0

    for current_root, dirs, files in os_walk_sorted(repo_root):
        current_path = Path(current_root)
        dirs[:] = [
            name
            for name in dirs
            if should_skip_path(current_path / name, repo_root, settings).action
            != ScanAction.SKIP
        ]
        for file_name in files:
            path = current_path / file_name
            decision = should_skip_path(path, repo_root, settings)
            summary.total_candidates += 1
            size = path.stat().st_size
            summary.bytes_considered += size

            if bytes_scanned + size > settings.max_total_bytes_scanned:
                decision = decision.model_copy(
                    update={
                        "action": ScanAction.SKIP,
                        "reason_code": SkipReason.TOTAL_BUDGET_EXCEEDED,
                        "matched_rule": "max_total_bytes_scanned",
                        "size_bytes": size,
                    }
                )

            language, support_status, source, is_parse_eligible, notes = classify_path(path, settings)
            if decision.action == ScanAction.SKIP:
                support_status = SupportStatus.SKIPPED
                is_parse_eligible = False
                notes = [*notes, f"skipped:{decision.reason_code.value}"]
            elif is_parse_eligible:
                bytes_scanned += size

            record = ManifestRecord(
                relative_path=str(path.relative_to(repo_root)).replace("\\", "/"),
                size_bytes=size,
                modified_time=datetime.fromtimestamp(path.stat().st_mtime, UTC),
                extension=path.suffix.lower() or "<none>",
                language=language,
                support_status=support_status,
                skip_reason=decision.reason_code if decision.action == ScanAction.SKIP else None,
                is_parse_eligible=is_parse_eligible,
                classification_source=source,
                notes=notes,
            )
            records.append(record)

    records.sort(key=lambda item: item.relative_path)
    for record in records:
        if record.support_status == SupportStatus.SUPPORTED:
            summary.supported_count += 1
        elif record.support_status == SupportStatus.PARTIAL:
            summary.partial_count += 1
        elif record.support_status == SupportStatus.UNSUPPORTED:
            summary.unsupported_count += 1
        elif record.support_status == SupportStatus.SKIPPED:
            summary.skipped_count += 1
        if record.is_parse_eligible:
            summary.parse_eligible_count += 1
    summary.bytes_scanned = bytes_scanned
    return RepositoryManifest(records=records, summary=summary)


def os_walk_sorted(root: Path):
    """Yield sorted os.walk results."""

    import os

    for current_root, dirs, files in os.walk(root):
        dirs.sort()
        files.sort()
        yield current_root, dirs, files
