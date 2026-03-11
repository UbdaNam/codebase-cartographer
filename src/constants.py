"""Shared constants for Stage 0 scanning and artifact behavior."""

from __future__ import annotations

from pathlib import Path

SUPPORTED = "supported"
PARTIAL = "partial"
SKIPPED = "skipped"
UNSUPPORTED = "unsupported"

DEFAULT_ARTIFACT_DIR = Path(".cartography")
DEFAULT_RUNS_DIR = "runs"
DEFAULT_CACHE_DIR = "cache"
DEFAULT_LOGS_DIR = "logs"

DEFAULT_IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "coverage",
}

DEFAULT_IGNORE_FILE_NAMES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "uv.lock",
    ".terraform.lock.hcl",
}

DEFAULT_SECRET_FILE_PATTERNS = (
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "*.crt",
)

DEFAULT_BINARY_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".webp",
    ".ico",
    ".pdf",
    ".zip",
    ".gz",
    ".tar",
    ".7z",
    ".rar",
    ".mp3",
    ".mp4",
    ".mov",
    ".avi",
    ".dll",
    ".so",
    ".dylib",
    ".exe",
    ".bin",
}

DEFAULT_SUPPORTED_EXTENSIONS = {
    ".py": {"language": "python", "support_status": SUPPORTED},
    ".sql": {"language": "sql", "support_status": SUPPORTED},
    ".yaml": {"language": "yaml", "support_status": SUPPORTED},
    ".yml": {"language": "yaml", "support_status": SUPPORTED},
    ".js": {"language": "javascript", "support_status": SUPPORTED},
    ".ts": {"language": "typescript", "support_status": SUPPORTED},
    ".json": {"language": "json", "support_status": SUPPORTED},
    ".ipynb": {"language": "notebook", "support_status": PARTIAL},
}

MINIFIED_SUFFIXES = (".min.js", ".min.css")
