"""Typed application settings for Stage 0."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.constants import (
    DEFAULT_ARTIFACT_DIR,
    DEFAULT_BINARY_EXTENSIONS,
    DEFAULT_CACHE_DIR,
    DEFAULT_IGNORE_DIRS,
    DEFAULT_IGNORE_FILE_NAMES,
    DEFAULT_IGNORE_FILE_PATTERNS,
    DEFAULT_LOGS_DIR,
    DEFAULT_REPOS_DIR,
    DEFAULT_RUNS_DIR,
    DEFAULT_SECRET_FILE_PATTERNS,
    DEFAULT_SUPPORTED_EXTENSIONS,
)


class AppSettings(BaseSettings):
    """Runtime settings with environment override support."""

    model_config = SettingsConfigDict(
        env_prefix="CARTOGRAPHY_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    repo_root: Path = Field(default_factory=lambda: Path(".").resolve())
    artifact_dir: Path = DEFAULT_ARTIFACT_DIR
    max_file_size_bytes: int = 1_000_000
    max_total_bytes_scanned: int = 25_000_000
    supported_extensions: dict[str, dict[str, str]] = Field(
        default_factory=lambda: DEFAULT_SUPPORTED_EXTENSIONS.copy()
    )
    partially_supported_extensions: set[str] = Field(default_factory=set)
    ignore_dirs: set[str] = Field(default_factory=lambda: set(DEFAULT_IGNORE_DIRS))
    ignore_file_names: set[str] = Field(
        default_factory=lambda: set(DEFAULT_IGNORE_FILE_NAMES)
    )
    ignore_file_patterns: tuple[str, ...] = DEFAULT_IGNORE_FILE_PATTERNS
    secret_sensitive_patterns: tuple[str, ...] = DEFAULT_SECRET_FILE_PATTERNS
    binary_extensions: set[str] = Field(
        default_factory=lambda: set(DEFAULT_BINARY_EXTENSIONS)
    )
    concurrency_limit: int = 4
    cache_enabled: bool = True
    git_velocity_lookback_days: int = 30
    high_velocity_core_change_share: float = 0.8
    cache_dir_name: str = DEFAULT_CACHE_DIR
    runs_dir_name: str = DEFAULT_RUNS_DIR
    logs_dir_name: str = DEFAULT_LOGS_DIR
    repos_dir_name: str = DEFAULT_REPOS_DIR

    @field_validator("repo_root", mode="before")
    @classmethod
    def _resolve_repo_root(cls, value: Path | str) -> Path:
        return Path(value).resolve()

    @field_validator("artifact_dir", mode="before")
    @classmethod
    def _resolve_artifact_dir(cls, value: Path | str) -> Path:
        path = Path(value)
        return path if path.is_absolute() else path

    @field_validator(
        "max_file_size_bytes",
        "max_total_bytes_scanned",
        "concurrency_limit",
        "git_velocity_lookback_days",
    )
    @classmethod
    def _ensure_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("must be a positive integer")
        return value

    @field_validator("high_velocity_core_change_share")
    @classmethod
    def _ensure_share(cls, value: float) -> float:
        if value <= 0 or value > 1:
            raise ValueError("must be greater than 0 and less than or equal to 1")
        return value

    def resolved_artifact_dir(self) -> Path:
        """Return the absolute artifact root."""

        if self.artifact_dir.is_absolute():
            return self.artifact_dir
        return self.repo_root / self.artifact_dir

    def inventory_summary_path(self, run_dir: Path) -> Path:
        """Return the inventory summary output path for a run directory."""

        return run_dir / "inventory_summary.json"

    def structural_summary_path(self, run_dir: Path) -> Path:
        """Return the structural summary output path for a run directory."""

        return run_dir / "structural_summary.json"

    def module_graph_path(self, run_dir: Path) -> Path:
        """Return the Surveyor module graph output path for a run directory."""

        return run_dir / "module_graph.json"

    def survey_summary_path(self, run_dir: Path) -> Path:
        """Return the Surveyor summary output path for a run directory."""

        return run_dir / "survey_summary.json"
