"""Canonicalization and stable ID helpers for deterministic contracts."""

from __future__ import annotations

from hashlib import sha1
from pathlib import PurePosixPath
from typing import Any

from pydantic import BaseModel

from src.models.enums import EdgeKind, NodeKind


def canonicalize_name(value: str) -> str:
    """Normalize names used as deterministic identity inputs."""

    return " ".join(value.strip().split()).lower()


def normalize_relative_path(path: str) -> str:
    """Normalize an analysis-root-relative path to POSIX form."""

    candidate = path.replace("\\", "/").strip()
    pure = PurePosixPath(candidate)
    if pure.is_absolute() or candidate.startswith("../") or "/../" in f"/{candidate}/":
        msg = f"path must stay relative to the analysis root: {path}"
        raise ValueError(msg)
    normalized = pure.as_posix()
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized or "."


def stable_id(namespace: str, *parts: str) -> str:
    """Build a short deterministic identifier from canonical inputs."""

    digest = sha1("::".join((namespace, *parts)).encode("utf-8")).hexdigest()[:12]
    return f"{namespace}:{digest}"


def build_node_id(kind: NodeKind | str, *, canonical_name: str, path: str | None = None) -> str:
    """Build a deterministic node ID from canonical graph fields."""

    name_part = canonicalize_name(canonical_name)
    path_part = normalize_relative_path(path) if path else "-"
    return stable_id("node", str(kind), name_part, path_part)


def build_edge_id(kind: EdgeKind | str, *, source_node_id: str, target_node_id: str) -> str:
    """Build a deterministic edge ID from source, target, and edge kind."""

    return stable_id("edge", str(kind), source_node_id, target_node_id)


def build_artifact_id(
    artifact_kind: str,
    *,
    logical_name: str | None = None,
    serialization_path: str | None = None,
) -> str:
    """Build a deterministic artifact ID from canonical artifact fields."""

    name_part = canonicalize_name(logical_name or artifact_kind)
    path_part = normalize_relative_path(serialization_path) if serialization_path else "-"
    return stable_id("artifact", canonicalize_name(artifact_kind), name_part, path_part)


def canonicalize_json_value(value: Any) -> Any:
    """Recursively normalize payload values for deterministic JSON output."""

    if isinstance(value, BaseModel):
        return canonicalize_json_value(value.model_dump(mode="json"))
    if isinstance(value, dict):
        return {key: canonicalize_json_value(value[key]) for key in sorted(value)}
    if isinstance(value, set):
        return [canonicalize_json_value(item) for item in sorted(value, key=repr)]
    if isinstance(value, tuple):
        return [canonicalize_json_value(item) for item in value]
    if isinstance(value, list):
        return [canonicalize_json_value(item) for item in value]
    return value
