"""Typed application settings for Brownfield Cartographer."""

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
    model_config = SettingsConfigDict(
        env_prefix="CARTOGRAPHY_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    repo_root: Path = Field(default_factory=lambda: Path(".").resolve())
    artifact_dir: Path = DEFAULT_ARTIFACT_DIR
    max_file_size_bytes: int = 1_000_000
    max_total_bytes_scanned: int = 25_000_000
    supported_extensions: dict[str, dict[str, str]] = Field(default_factory=lambda: DEFAULT_SUPPORTED_EXTENSIONS.copy())
    partially_supported_extensions: set[str] = Field(default_factory=set)
    ignore_dirs: set[str] = Field(default_factory=lambda: set(DEFAULT_IGNORE_DIRS))
    ignore_file_names: set[str] = Field(default_factory=lambda: set(DEFAULT_IGNORE_FILE_NAMES))
    ignore_file_patterns: tuple[str, ...] = DEFAULT_IGNORE_FILE_PATTERNS
    secret_sensitive_patterns: tuple[str, ...] = DEFAULT_SECRET_FILE_PATTERNS
    binary_extensions: set[str] = Field(default_factory=lambda: set(DEFAULT_BINARY_EXTENSIONS))
    concurrency_limit: int = 4
    cache_enabled: bool = True
    git_velocity_lookback_days: int = 30
    high_velocity_core_change_share: float = 0.8
    semantic_git_lookback_days: int = 90
    semantic_module_excerpt_lines: int = 12
    semantic_max_prompt_tokens: int = 14_000
    semantic_max_completion_tokens: int = 900
    semantic_completion_reserve_tokens: int = 160
    semantic_max_total_prompt_tokens: int = 250_000
    semantic_max_total_completion_tokens: int = 60_000
    semantic_max_requests_per_run: int = 500
    semantic_domain_min_clusters: int = 5
    semantic_domain_max_clusters: int = 8
    semantic_provider_enabled: bool = True
    openrouter_api_key: str | None = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_app_name: str = "codebase-cartographer"
    openrouter_referer: str | None = None
    semantic_purpose_model: str = "google/gemini-2.0-flash-001"
    semantic_synthesis_model: str = "openai/gpt-4o-mini"
    semantic_embedding_model: str = "text-embedding-3-small"
    navigator_agent_model: str = "openai/gpt-4o-mini"
    navigator_synthesis_model: str = "openai/gpt-4o-mini"
    navigator_max_tool_rounds: int = 3
    navigator_max_context_tokens: int = 12_000
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
        "semantic_git_lookback_days",
        "semantic_module_excerpt_lines",
        "semantic_max_prompt_tokens",
        "semantic_max_completion_tokens",
        "semantic_completion_reserve_tokens",
        "semantic_max_total_prompt_tokens",
        "semantic_max_total_completion_tokens",
        "semantic_max_requests_per_run",
        "semantic_domain_min_clusters",
        "semantic_domain_max_clusters",
        "navigator_max_tool_rounds",
        "navigator_max_context_tokens",
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
        return self.artifact_dir if self.artifact_dir.is_absolute() else self.repo_root / self.artifact_dir

    def inventory_summary_path(self, run_dir: Path) -> Path:
        return run_dir / "inventory_summary.json"

    def structural_summary_path(self, run_dir: Path) -> Path:
        return run_dir / "structural_summary.json"

    def module_graph_path(self, run_dir: Path) -> Path:
        return run_dir / "module_graph.json"

    def survey_summary_path(self, run_dir: Path) -> Path:
        return run_dir / "survey_summary.json"

    def lineage_graph_path(self, run_dir: Path) -> Path:
        return run_dir / "lineage_graph.json"

    def lineage_summary_path(self, run_dir: Path) -> Path:
        return run_dir / "lineage_summary.json"

    def module_semantics_path(self, run_dir: Path) -> Path:
        return run_dir / "module_semantics.json"

    def documentation_drift_path(self, run_dir: Path) -> Path:
        return run_dir / "documentation_drift.json"

    def domain_map_path(self, run_dir: Path) -> Path:
        return run_dir / "domain_map.json"

    def day_one_answers_path(self, run_dir: Path) -> Path:
        return run_dir / "day_one_answers.json"

    def codebase_md_path(self, run_dir: Path) -> Path:
        return run_dir / "CODEBASE.md"

    def onboarding_brief_path(self, run_dir: Path) -> Path:
        return run_dir / "onboarding_brief.md"

    def semantic_index_dir(self, run_dir: Path) -> Path:
        return run_dir / "semantic_index"

    def trace_log_path(self, run_dir: Path) -> Path:
        return run_dir / "cartography_trace.jsonl"

    def incremental_baseline_path(self, run_dir: Path) -> Path:
        return run_dir / "incremental_baseline.json"

    def latest_codebase_md_path(self) -> Path:
        return self.resolved_artifact_dir() / "CODEBASE.md"

    def latest_onboarding_brief_path(self) -> Path:
        return self.resolved_artifact_dir() / "onboarding_brief.md"

    def latest_lineage_graph_path(self) -> Path:
        return self.resolved_artifact_dir() / "lineage_graph.json"

    def latest_semantic_index_dir(self) -> Path:
        return self.resolved_artifact_dir() / "semantic_index"

    def latest_trace_log_path(self) -> Path:
        return self.resolved_artifact_dir() / "cartography_trace.jsonl"
