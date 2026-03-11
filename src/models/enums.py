"""Stable enums shared across Brownfield Cartographer contracts."""

from __future__ import annotations

from enum import StrEnum


class NodeKind(StrEnum):
    MODULE = "module"
    DATASET = "dataset"
    TRANSFORMATION = "transformation"
    FILE = "file"
    SYMBOL = "symbol"


class EdgeKind(StrEnum):
    IMPORTS = "imports"
    DEFINES = "defines"
    CALLS = "calls"
    CONSUMES = "consumes"
    PRODUCES = "produces"
    DEPENDS_ON = "depends_on"
    FLOWS_TO = "flows_to"


class SupportStatus(StrEnum):
    SUPPORTED = "supported"
    PARTIAL = "partial"
    SKIPPED = "skipped"
    UNSUPPORTED = "unsupported"


class AnalysisMethod(StrEnum):
    STATIC_ANALYSIS = "static_analysis"
    GRAPH_INFERENCE = "graph_inference"
    LLM_INFERENCE = "llm_inference"
    HEURISTIC = "heuristic"
    MANUAL = "manual"


class SkipReason(StrEnum):
    ALLOWED = "allowed"
    IGNORED_DIRECTORY = "ignored_directory"
    IGNORED_FILENAME = "ignored_filename"
    SECRET_SENSITIVE = "secret_sensitive"
    BINARY_OR_ARCHIVE = "binary_or_archive"
    MINIFIED_ASSET = "minified_asset"
    OVERSIZED_FILE = "oversized_file"
    UNSUPPORTED_EXTENSION = "unsupported_extension"
    ANALYSIS_ROOT_ESCAPE = "analysis_root_escape"
    TOTAL_BUDGET_EXCEEDED = "total_budget_exceeded"
    UNRESOLVED_REFERENCE = "unresolved_reference"
    MISSING_EVIDENCE = "missing_evidence"


class ConfidenceBand(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class RunStatus(StrEnum):
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
