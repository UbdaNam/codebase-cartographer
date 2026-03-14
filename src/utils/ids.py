"""Canonicalization and stable ID helpers for deterministic contracts."""

from __future__ import annotations

from hashlib import sha1
from pathlib import PurePosixPath
from typing import Any

from pydantic import BaseModel

from src.models.enums import EdgeKind, NodeKind


def canonicalize_name(value: str) -> str:
    return " ".join(value.strip().split()).lower()


def normalize_relative_path(path: str) -> str:
    candidate = path.replace("\\", "/").strip()
    pure = PurePosixPath(candidate)
    if pure.is_absolute() or candidate.startswith("../") or "/../" in f"/{candidate}/":
        raise ValueError(f"path must stay relative to the analysis root: {path}")
    normalized = pure.as_posix()
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized or "."


def stable_id(namespace: str, *parts: str) -> str:
    digest = sha1("::".join((namespace, *parts)).encode("utf-8")).hexdigest()[:12]
    return f"{namespace}:{digest}"


def build_node_id(kind: NodeKind | str, *, canonical_name: str, path: str | None = None) -> str:
    name_part = canonicalize_name(canonical_name)
    path_part = normalize_relative_path(path) if path else "-"
    return stable_id("node", str(kind), name_part, path_part)


def build_edge_id(kind: EdgeKind | str, *, source_node_id: str, target_node_id: str) -> str:
    return stable_id("edge", str(kind), source_node_id, target_node_id)


def build_artifact_id(artifact_kind: str, *, logical_name: str | None = None, serialization_path: str | None = None) -> str:
    name_part = canonicalize_name(logical_name or artifact_kind)
    path_part = normalize_relative_path(serialization_path) if serialization_path else "-"
    return stable_id("artifact", canonicalize_name(artifact_kind), name_part, path_part)


def build_module_dependency_key(source_module_id: str, target_display: str) -> str:
    return stable_id("module_dependency", source_module_id, canonicalize_name(target_display))


def build_dataset_id(canonical_name: str) -> str:
    return stable_id("dataset", canonicalize_name(canonical_name))


def build_transformation_id(file_path: str, transformation_name: str) -> str:
    return stable_id("transformation", normalize_relative_path(file_path), canonicalize_name(transformation_name))


def build_lineage_signal_id(source_path: str, raw_identifier: str, signal_source_kind: str, line_start: int | None = None) -> str:
    return stable_id(
        "lineage_signal",
        normalize_relative_path(source_path),
        canonicalize_name(signal_source_kind),
        canonicalize_name(raw_identifier),
        str(line_start or "-"),
    )


def build_semantic_profile_id(module_id: str) -> str:
    return stable_id("semantic_profile", module_id)


def build_drift_id(module_id: str, drift_type: str, documentation_path: str | None = None) -> str:
    return stable_id("documentation_drift", module_id, canonicalize_name(drift_type), normalize_relative_path(documentation_path) if documentation_path else "-")


def build_domain_id(label: str) -> str:
    return stable_id("domain", canonicalize_name(label))


def build_day_one_answer_id(question_id: str) -> str:
    return stable_id("day_one_answer", canonicalize_name(question_id))


def build_evidence_reference_id(source_kind: str, repository_path: str, line_start: int | None = None, line_end: int | None = None) -> str:
    return stable_id(
        "semantic_evidence",
        canonicalize_name(source_kind),
        normalize_relative_path(repository_path),
        str(line_start or "-"),
        str(line_end or "-"),
    )


def canonicalize_json_value(value: Any) -> Any:
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
