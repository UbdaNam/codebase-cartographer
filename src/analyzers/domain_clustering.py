"""Domain clustering for Semanticist."""

from __future__ import annotations

from collections import defaultdict
from math import sqrt

from src.llm.provider import EmbeddingRequest, LLMProvider, ProviderError
from src.models.enums import ConfidenceBand
from src.models.semantic import DomainAssignment, DomainCluster, SemanticModuleProfile

DOMAIN_KEYWORDS: dict[str, tuple[str, ...]] = {
    "ingestion": ("ingest", "load", "extract", "source", "input"),
    "transformation": ("transform", "build", "aggregate", "dataset", "output"),
    "serving": ("serve", "api", "endpoint", "response", "publish"),
    "monitoring": ("monitor", "alert", "health", "metric", "observe"),
    "orchestration": ("dag", "schedule", "orchestr", "job", "workflow", "cli"),
    "shared utilities": ("util", "helper", "shared", "common", "base"),
}


def cluster_profiles(
    profiles: list[SemanticModuleProfile],
    *,
    provider: LLMProvider | None = None,
    embedding_model: str | None = None,
    min_clusters: int = 5,
    max_clusters: int = 8,
) -> list[DomainCluster]:
    if not profiles:
        return []
    if provider and embedding_model and provider.is_available():
        try:
            clustered = _merge_clusters_by_label(_cluster_with_embeddings(profiles, provider, embedding_model))
            if len(clustered) <= max_clusters:
                return clustered
        except ProviderError:
            pass
    return _cluster_with_keywords(profiles)


def infer_domain_label(profile: SemanticModuleProfile) -> str:
    haystack = " ".join(
        [
            profile.relative_path.lower(),
            profile.purpose_statement.lower(),
            profile.domain_label.lower() if profile.domain_label else "",
        ]
    )
    scores = {
        label: sum(1 for keyword in keywords if keyword in haystack)
        for label, keywords in DOMAIN_KEYWORDS.items()
    }
    best_label, best_score = max(scores.items(), key=lambda item: (item[1], item[0]))
    return best_label if best_score > 0 else "shared utilities"


def _cluster_with_keywords(profiles: list[SemanticModuleProfile]) -> list[DomainCluster]:
    buckets: dict[str, list[SemanticModuleProfile]] = defaultdict(list)
    for profile in profiles:
        buckets[infer_domain_label(profile)].append(profile)
    clusters: list[DomainCluster] = []
    for label, bucket in sorted(buckets.items()):
        cluster = DomainCluster(
            label=label,
            summary=f"This domain groups {len(bucket)} modules centered on {label} responsibilities.",
            confidence=ConfidenceBand.MEDIUM,
            module_ids=[profile.module_id for profile in bucket],
            primary_signals=[label, "keyword_fallback"],
            assignments=[],
        )
        assignments = [
            DomainAssignment(
                module_id=profile.module_id,
                domain_id=cluster.domain_id,
                assignment_confidence=ConfidenceBand.MEDIUM,
                assignment_signals=[label, profile.relative_path],
            )
            for profile in sorted(bucket, key=lambda item: item.relative_path)
        ]
        clusters.append(cluster.model_copy(update={"assignments": assignments}))
    return clusters


def _cluster_with_embeddings(profiles: list[SemanticModuleProfile], provider: LLMProvider, embedding_model: str) -> list[DomainCluster]:
    texts = [f"{profile.relative_path}\n{profile.purpose_statement}" for profile in profiles]
    result = provider.embed_texts(EmbeddingRequest(texts=texts, model=embedding_model))
    if len(result.vectors) != len(profiles):
        return _cluster_with_keywords(profiles)
    indexed_vectors = list(enumerate(result.vectors))
    seeds: list[tuple[str, list[float], list[int]]] = []
    for profile_index, vector in indexed_vectors:
        assigned = False
        for index, (label, centroid, members) in enumerate(seeds):
            if _cosine_similarity(vector, centroid) >= 0.84:
                updated_members = members + [profile_index]
                updated_centroid = _centroid([result.vectors[item] for item in updated_members], len(vector))
                seeds[index] = (label, updated_centroid, updated_members)
                assigned = True
                break
        if not assigned:
            seeds.append((infer_domain_label(profiles[profile_index]), vector, [profile_index]))
    clusters: list[DomainCluster] = []
    for label, _, member_indexes in sorted(seeds, key=lambda item: (item[0], len(item[2]) * -1)):
        members = [profiles[index] for index in member_indexes]
        cluster = DomainCluster(
            label=label,
            summary=f"This domain groups {len(members)} modules centered on {label} responsibilities.",
            confidence=ConfidenceBand.HIGH,
            module_ids=[member.module_id for member in members],
            primary_signals=[label, "embedding_cluster"],
            assignments=[],
        )
        assignments = [
            DomainAssignment(
                module_id=member.module_id,
                domain_id=cluster.domain_id,
                assignment_confidence=ConfidenceBand.HIGH,
                assignment_signals=[label, "embedding_cluster"],
            )
            for member in sorted(members, key=lambda item: item.relative_path)
        ]
        clusters.append(cluster.model_copy(update={"assignments": assignments}))
    return clusters


def _merge_clusters_by_label(clusters: list[DomainCluster]) -> list[DomainCluster]:
    grouped: dict[str, list[DomainCluster]] = defaultdict(list)
    for cluster in clusters:
        grouped[cluster.label].append(cluster)
    merged: list[DomainCluster] = []
    for label, items in sorted(grouped.items()):
        module_ids = sorted({module_id for item in items for module_id in item.module_ids})
        primary_signals = sorted({signal for item in items for signal in item.primary_signals})
        assignments = [
            DomainAssignment(
                module_id=module_id,
                domain_id="",
                assignment_confidence=ConfidenceBand.HIGH if any(
                    assignment.assignment_confidence == ConfidenceBand.HIGH
                    for item in items
                    for assignment in item.assignments
                    if assignment.module_id == module_id
                ) else ConfidenceBand.MEDIUM,
                assignment_signals=primary_signals,
            )
            for module_id in module_ids
        ]
        merged_cluster = DomainCluster(
            label=label,
            summary=f"This domain groups {len(module_ids)} modules centered on {label} responsibilities.",
            confidence=ConfidenceBand.HIGH,
            module_ids=module_ids,
            primary_signals=primary_signals,
            assignments=[],
        )
        merged.append(
            merged_cluster.model_copy(
                update={
                    "assignments": [
                        assignment.model_copy(update={"domain_id": merged_cluster.domain_id})
                        for assignment in assignments
                    ]
                }
            )
        )
    return merged


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = sqrt(sum(item * item for item in left))
    right_norm = sqrt(sum(item * item for item in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


def _centroid(vectors: list[list[float]], width: int) -> list[float]:
    if not vectors:
        return [0.0] * width
    return [sum(vector[index] for vector in vectors) / len(vectors) for index in range(width)]
