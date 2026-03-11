"""Repository input and preparation contracts for Stage 3."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.utils.ids import canonicalize_name, stable_id


class RepositoryInputKind(StrEnum):
    LOCAL_PATH = "local_path"
    GIT_URL = "git_url"


class PreparationStatus(StrEnum):
    READY = "ready"
    FAILED = "failed"


class RepositoryReuseMode(StrEnum):
    DIRECT = "direct"
    FRESH_CLONE = "fresh_clone"
    REUSED_CLONE = "reused_clone"
    REFRESHED_CLONE = "refreshed_clone"


class RepositoryInput(BaseModel):
    """User-supplied repository target before preparation."""

    model_config = ConfigDict(extra="forbid")

    raw_input: str
    input_kind: RepositoryInputKind
    canonical_identity: str | None = None
    requested_ref: str | None = None

    @field_validator("raw_input")
    @classmethod
    def validate_raw_input(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("raw_input must not be empty")
        return cleaned

    @model_validator(mode="after")
    def finalize_identity(self) -> "RepositoryInput":
        if self.canonical_identity is None:
            self.canonical_identity = stable_id(
                "repository",
                self.input_kind.value,
                canonicalize_name(self.raw_input),
                canonicalize_name(self.requested_ref or "-"),
            )
        return self

    @classmethod
    def from_raw(cls, value: str | Path) -> "RepositoryInput":
        raw_value = str(value).strip()
        if not raw_value:
            raise ValueError("repository input must not be empty")

        parsed = urlparse(raw_value)
        if parsed.scheme in {"http", "https", "git", "ssh", "file"} or raw_value.startswith("git@"):
            return cls(raw_input=raw_value, input_kind=RepositoryInputKind.GIT_URL)

        path = Path(raw_value).expanduser()
        if path.exists():
            return cls(raw_input=str(path.resolve()), input_kind=RepositoryInputKind.LOCAL_PATH)

        raise ValueError(f"repository input is not a valid local path or supported Git URL: {raw_value}")


class PreparedRepository(BaseModel):
    """Prepared local repository root for downstream analysis."""

    model_config = ConfigDict(extra="forbid")

    repository_input: RepositoryInput
    local_repo_path: str
    preparation_status: PreparationStatus = PreparationStatus.READY
    reuse_mode: RepositoryReuseMode
    prepared_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    source_url: str | None = None
    source_ref: str | None = None
    warnings: list[str] = Field(default_factory=list)

    @field_validator("local_repo_path")
    @classmethod
    def validate_local_repo_path(cls, value: str) -> str:
        return str(Path(value).resolve()).replace("\\", "/")
