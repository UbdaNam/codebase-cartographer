"""Deterministic language, support-status, and parse-eligibility classification."""

from __future__ import annotations

from pathlib import Path

from src.config import AppSettings
from src.models.enums import SkipReason, SupportStatus
from src.utils.ids import normalize_relative_path


def classify_path(path: Path, settings: AppSettings) -> tuple[str, SupportStatus, str, bool, list[str]]:
    """Classify a file path using the supported extension registry."""

    suffix = path.suffix.lower()
    notes: list[str] = []
    try:
        normalized_path = normalize_relative_path(str(path))
    except ValueError:
        normalized_path = str(path).replace("\\", "/")

    if path.name == "package.json":
        return ("json", SupportStatus.PARTIAL, "filename:package.json", True, ["package metadata file"])
    if suffix == ".json" and any(part in {"config", "configs"} for part in path.parts):
        notes.append("config directory JSON")

    if suffix in settings.supported_extensions:
        entry = settings.supported_extensions[suffix]
        support_status = SupportStatus(entry["support_status"])
        return (
            entry["language"],
            support_status,
            f"extension:{suffix}",
            support_status in {SupportStatus.SUPPORTED, SupportStatus.PARTIAL},
            notes,
        )
    if normalized_path.endswith(".lock"):
        return ("lockfile", SupportStatus.SKIPPED, f"extension:{suffix or '.lock'}", False, ["lockfile excluded"])
    return ("unknown", SupportStatus.UNSUPPORTED, f"extension:{suffix or '<none>'}", False, ["unsupported extension"])
