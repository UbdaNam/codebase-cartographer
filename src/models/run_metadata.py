"""Typed run context and summary records."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class RunStatus(StrEnum):
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"


class RunContext(BaseModel):
    run_id: str
    started_at: datetime
    finished_at: datetime | None = None
    branch: str
    repo_root: str
    artifact_root: str
    status: RunStatus
    summary_path: str


class RunSummary(BaseModel):
    run_id: str
    status: RunStatus
    message: str
    manifest_path: str | None = None
