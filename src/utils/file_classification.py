"""Deterministic language and support-status classification."""

from __future__ import annotations

from pathlib import Path

from src.config import AppSettings
from src.models.manifest import SupportStatus


def classify_path(path: Path, settings: AppSettings) -> tuple[str, SupportStatus, str]:
    """Classify a file path using the supported extension registry."""

    suffix = path.suffix.lower()
    if suffix in settings.supported_extensions:
        entry = settings.supported_extensions[suffix]
        return (
            entry["language"],
            SupportStatus(entry["support_status"]),
            f"extension:{suffix}",
        )
    return ("unknown", SupportStatus.UNSUPPORTED, f"extension:{suffix or '<none>'}")
