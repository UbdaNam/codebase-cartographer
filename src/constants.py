"""Shared constants for scanning, routing, and artifact behavior."""

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
DEFAULT_REPOS_DIR = "repos"

DEFAULT_IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "coverage",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    ".cache",
}

DEFAULT_IGNORE_FILE_NAMES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "uv.lock",
    ".terraform.lock.hcl",
    "Cargo.lock",
    "composer.lock",
    "Gemfile.lock",
    "Pipfile.lock",
}

DEFAULT_IGNORE_FILE_PATTERNS = (
    ".python-version",
    ".tool-versions",
)

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
    ".parquet",
    ".avro",
    ".orc",
    ".zip",
    ".gz",
    ".tar",
    ".tgz",
    ".7z",
    ".rar",
    ".jar",
    ".war",
    ".class",
    ".mp3",
    ".mp4",
    ".mov",
    ".avi",
    ".wav",
    ".ogg",
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
    ".mjs": {"language": "javascript", "support_status": SUPPORTED},
    ".cjs": {"language": "javascript", "support_status": SUPPORTED},
    ".ts": {"language": "typescript", "support_status": SUPPORTED},
    ".tsx": {"language": "typescript", "support_status": PARTIAL},
    ".json": {"language": "json", "support_status": SUPPORTED},
    ".ipynb": {"language": "notebook", "support_status": PARTIAL},
    ".sh": {"language": "shell", "support_status": PARTIAL},
}

MINIFIED_SUFFIXES = (".min.js", ".min.css")

SUPPORTED_FOR_PARSING = {SUPPORTED}
PARTIALLY_SUPPORTED_FOR_PARSING = {PARTIAL}
