"""Filesystem-backed semantic index for Navigator retrieval."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

from src.llm.provider import EmbeddingRequest, LLMProvider, ProviderError
from src.models.archivist import SemanticIndexEntry, SemanticIndexSnapshot
from src.models.semantic import SemanticModuleProfile

TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9_]{2,}")


def build_semantic_index(
    profiles: list[SemanticModuleProfile],
    *,
    run_id: str,
    index_dir: Path,
    commit_hash: str | None,
    provider: LLMProvider | None,
    embedding_model: str,
) -> SemanticIndexSnapshot:
    """Build and persist a semantic index snapshot."""

    index_dir.mkdir(parents=True, exist_ok=True)
    entries = [
        SemanticIndexEntry(
            module_id=profile.module_id,
            module_path=profile.relative_path,
            purpose_statement=profile.purpose_statement,
            domain_cluster=profile.domain_label,
            retrieval_tokens=tokenize(f"{profile.relative_path} {profile.domain_label or ''} {profile.purpose_statement}"),
            evidence_references=profile.evidence_references[:6],
        )
        for profile in sorted(profiles, key=lambda item: item.relative_path)
    ]
    used_fallback_indexing = True
    warning_codes: list[str] = []
    if provider is not None and provider.is_available() and entries:
        try:
            result = provider.embed_texts(
                EmbeddingRequest(
                    texts=[entry.purpose_statement for entry in entries],
                    model=embedding_model,
                )
            )
            for entry, vector in zip(entries, result.vectors, strict=False):
                entry.embedding_vector = vector
            used_fallback_indexing = False
        except ProviderError as exc:
            warning_codes.append(f"semantic_index_embedding_fallback:{type(exc).__name__}")
            detail = str(exc).strip()
            if detail:
                warning_codes.append(f"semantic_index_embedding_detail:{detail[:160]}")
    snapshot = SemanticIndexSnapshot(
        run_id=run_id,
        commit_hash=commit_hash,
        entry_count=len(entries),
        embedding_model=embedding_model if not used_fallback_indexing else None,
        used_fallback_indexing=used_fallback_indexing,
        source_module_ids=[entry.module_id for entry in entries],
        warning_codes=warning_codes,
        entries=entries,
    )
    (index_dir / "snapshot.json").write_text(json.dumps(snapshot.model_dump(mode="json"), indent=2, sort_keys=True), encoding="utf-8")
    return snapshot


def load_semantic_index(index_dir: Path) -> SemanticIndexSnapshot:
    """Load a semantic index snapshot from disk."""

    return SemanticIndexSnapshot.model_validate_json((index_dir / "snapshot.json").read_text(encoding="utf-8"))


def search_semantic_index(
    snapshot: SemanticIndexSnapshot,
    query: str,
    *,
    max_results: int,
    query_vector: list[float] | None = None,
) -> list[SemanticIndexEntry]:
    """Retrieve semantically relevant modules from the persisted index."""

    tokens = tokenize(query)
    scored: list[tuple[float, SemanticIndexEntry]] = []
    for entry in snapshot.entries:
        lexical = lexical_score(tokens, entry.retrieval_tokens)
        semantic = cosine_similarity(query_vector, entry.embedding_vector) if query_vector and entry.embedding_vector else 0.0
        score = hybrid_score(lexical, semantic)
        score += evidence_bonus(entry)
        score -= container_penalty(entry)
        if score <= 0 and entry.embedding_vector:
            score = vectorless_keyword_hint(query, entry)
        if score <= 0:
            continue
        scored.append((score, entry))
    ordered = sorted(scored, key=lambda item: (-item[0], item[1].module_path, item[1].module_id))
    return [entry for _, entry in ordered[:max_results]]


def tokenize(text: str) -> list[str]:
    """Tokenize a retrieval unit deterministically."""

    return sorted(dict.fromkeys(match.group(0).lower() for match in TOKEN_PATTERN.finditer(text)))


def lexical_score(query_tokens: list[str], candidate_tokens: list[str]) -> float:
    """Simple deterministic lexical score."""

    if not query_tokens or not candidate_tokens:
        return 0.0
    overlap = len(set(query_tokens).intersection(candidate_tokens))
    return overlap / math.sqrt(len(set(query_tokens)) * len(set(candidate_tokens)))


def vectorless_keyword_hint(query: str, entry: SemanticIndexEntry) -> float:
    """Fallback nudge when embeddings exist but the lexical score is zero."""

    lowered = query.lower()
    if entry.domain_cluster and entry.domain_cluster.lower() in lowered:
        return 0.25
    if entry.module_path.lower() in lowered:
        return 1.0
    return 0.0


def cosine_similarity(left: list[float] | None, right: list[float] | None) -> float:
    """Compute cosine similarity for two embedding vectors."""

    if not left or not right or len(left) != len(right):
        return 0.0
    numerator = sum(a * b for a, b in zip(left, right, strict=False))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm <= 0 or right_norm <= 0:
        return 0.0
    return numerator / (left_norm * right_norm)


def hybrid_score(lexical: float, semantic: float) -> float:
    """Combine lexical and embedding similarity deterministically."""

    if semantic > 0:
        return (lexical * 0.65) + (semantic * 0.35)
    return lexical


def evidence_bonus(entry: SemanticIndexEntry) -> float:
    """Nudge evidence-backed entries above otherwise-similar empty entries."""

    return 0.1 if entry.evidence_references else 0.0


def container_penalty(entry: SemanticIndexEntry) -> float:
    """Penalize package container modules for concept-style implementation lookups."""

    return 0.35 if entry.module_path.endswith("/__init__.py") else 0.0
