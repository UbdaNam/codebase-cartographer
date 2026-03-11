"""Typed manifest and scan-policy records."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from src.models.enums import SkipReason, SupportStatus


class ScanAction(StrEnum):
    INCLUDE = "include"
    SKIP = "skip"


class ScanPolicyDecision(BaseModel):
    path: str
    action: ScanAction
    reason_code: SkipReason
    matched_rule: str
    is_secret_sensitive: bool = False
    size_bytes: int | None = None


class ManifestRecord(BaseModel):
    relative_path: str
    size_bytes: int
    modified_time: datetime
    digest: str | None = None
    digest_strategy: str = "deferred"
    language: str
    support_status: SupportStatus
    skip_reason: SkipReason | None = None
    classification_source: str


class ManifestSummary(BaseModel):
    total_candidates: int = 0
    supported_count: int = 0
    partial_count: int = 0
    unsupported_count: int = 0
    skipped_count: int = 0
    bytes_considered: int = 0
    bytes_scanned: int = 0


class RepositoryManifest(BaseModel):
    records: list[ManifestRecord] = Field(default_factory=list)
    summary: ManifestSummary = Field(default_factory=ManifestSummary)
