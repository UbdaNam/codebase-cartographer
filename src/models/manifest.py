"""Typed manifest and scan-policy records."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.models.enums import SkipReason, SupportStatus
from src.utils.ids import canonicalize_json_value, normalize_relative_path, stable_id


class ScanAction(StrEnum):
    INCLUDE = "include"
    SKIP = "skip"


class ScanPolicyDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    action: ScanAction
    reason_code: SkipReason
    matched_rule: str
    is_secret_sensitive: bool = False
    size_bytes: int | None = None

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        try:
            return normalize_relative_path(value)
        except ValueError:
            return value.replace("\\", "/")


class ManifestRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    relative_path: str
    file_id: str | None = None
    size_bytes: int
    modified_time: datetime
    extension: str = "<none>"
    digest: str | None = None
    digest_strategy: str = "deferred"
    language: str
    support_status: SupportStatus
    skip_reason: SkipReason | None = None
    is_parse_eligible: bool = False
    classification_source: str
    notes: list[str] = Field(default_factory=list)

    @field_validator("relative_path")
    @classmethod
    def validate_relative_path(cls, value: str) -> str:
        return normalize_relative_path(value)

    @field_validator("extension")
    @classmethod
    def normalize_extension(cls, value: str) -> str:
        return value.lower() or "<none>"

    @model_validator(mode="after")
    def finalize_record(self) -> "ManifestRecord":
        if self.extension == "<none>" and "." in self.relative_path.rsplit("/", maxsplit=1)[-1]:
            suffix = "." + self.relative_path.rsplit(".", maxsplit=1)[-1]
            self.extension = suffix.lower()
        if self.file_id is None:
            self.file_id = stable_id("file", self.relative_path)
        if self.skip_reason is not None:
            self.is_parse_eligible = False
        elif self.support_status == SupportStatus.SUPPORTED:
            self.is_parse_eligible = True
        elif self.support_status == SupportStatus.PARTIAL:
            self.is_parse_eligible = True
        else:
            self.is_parse_eligible = False
        return self


class ManifestSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_candidates: int = 0
    supported_count: int = 0
    partial_count: int = 0
    unsupported_count: int = 0
    skipped_count: int = 0
    bytes_considered: int = 0
    bytes_scanned: int = 0
    parse_eligible_count: int = 0


class RepositoryManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    records: list[ManifestRecord] = Field(default_factory=list)
    summary: ManifestSummary = Field(default_factory=ManifestSummary)

    def model_dump(self, *args, **kwargs):
        payload = super().model_dump(*args, **kwargs)
        return canonicalize_json_value(payload)
