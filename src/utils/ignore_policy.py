"""Centralized safe-scanning policy."""

from __future__ import annotations

from fnmatch import fnmatch
from pathlib import Path

from src.config import AppSettings
from src.constants import MINIFIED_SUFFIXES
from src.models.manifest import ScanAction, ScanPolicyDecision, SkipReason


LOCKFILE_SUFFIXES = (".lock",)


def _is_within_root(path: Path, repo_root: Path) -> bool:
    try:
        path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return False
    return True


def should_skip_path(path: Path, repo_root: Path, settings: AppSettings) -> ScanPolicyDecision:
    """Return a structured policy decision for a candidate path."""

    normalized = path.resolve()
    try:
        relative_label = str(normalized.relative_to(repo_root.resolve()))
    except ValueError:
        relative_label = str(normalized)

    if not _is_within_root(normalized, repo_root):
        return ScanPolicyDecision(
            path=relative_label,
            action=ScanAction.SKIP,
            reason_code=SkipReason.ANALYSIS_ROOT_ESCAPE,
            matched_rule="analysis_root",
        )

    if any(part in settings.ignore_dirs for part in path.parts):
        return ScanPolicyDecision(
            path=relative_label,
            action=ScanAction.SKIP,
            reason_code=SkipReason.IGNORED_DIRECTORY,
            matched_rule="ignore_dirs",
        )

    if path.name in settings.ignore_file_names:
        return ScanPolicyDecision(
            path=relative_label,
            action=ScanAction.SKIP,
            reason_code=SkipReason.IGNORED_FILENAME,
            matched_rule=path.name,
        )

    if any(fnmatch(path.name, pattern) for pattern in settings.ignore_file_patterns):
        return ScanPolicyDecision(
            path=relative_label,
            action=ScanAction.SKIP,
            reason_code=SkipReason.IGNORED_FILENAME,
            matched_rule="ignore_file_patterns",
        )

    if any(fnmatch(path.name, pattern) for pattern in settings.secret_sensitive_patterns):
        return ScanPolicyDecision(
            path=relative_label,
            action=ScanAction.SKIP,
            reason_code=SkipReason.SECRET_SENSITIVE,
            matched_rule="secret_sensitive_patterns",
            is_secret_sensitive=True,
        )

    if path.suffix.lower() in LOCKFILE_SUFFIXES:
        return ScanPolicyDecision(
            path=relative_label,
            action=ScanAction.SKIP,
            reason_code=SkipReason.IGNORED_FILENAME,
            matched_rule="lockfile_suffix",
        )

    if path.suffix.lower() in settings.binary_extensions:
        return ScanPolicyDecision(
            path=relative_label,
            action=ScanAction.SKIP,
            reason_code=SkipReason.BINARY_OR_ARCHIVE,
            matched_rule=path.suffix.lower(),
        )

    if any(path.name.endswith(suffix) for suffix in MINIFIED_SUFFIXES):
        return ScanPolicyDecision(
            path=relative_label,
            action=ScanAction.SKIP,
            reason_code=SkipReason.MINIFIED_ASSET,
            matched_rule="minified_suffix",
        )

    size_bytes = path.stat().st_size
    if size_bytes > settings.max_file_size_bytes:
        return ScanPolicyDecision(
            path=relative_label,
            action=ScanAction.SKIP,
            reason_code=SkipReason.OVERSIZED_FILE,
            matched_rule="max_file_size_bytes",
            size_bytes=size_bytes,
        )

    return ScanPolicyDecision(
        path=relative_label,
        action=ScanAction.INCLUDE,
        reason_code=SkipReason.ALLOWED,
        matched_rule="allowed",
        size_bytes=size_bytes,
    )
