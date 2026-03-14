from src.analyzers.domain_clustering import cluster_profiles
from src.llm.provider import EmbeddingRequest, EmbeddingResult
from src.models.enums import ConfidenceBand
from src.models.semantic import PurposeEvidenceBundle, SemanticModuleProfile


def test_domain_clustering_groups_profiles_with_labels() -> None:
    profiles = [
        SemanticModuleProfile(
            module_id="module-1",
            relative_path="app/ingestion.py",
            language="python",
            purpose_statement="This module handles ingestion work around load_orders. It exists to bring raw inputs into the managed processing flow.",
            purpose_confidence=ConfidenceBand.MEDIUM,
            evidence_bundle=PurposeEvidenceBundle(bundle_id="bundle-1", module_id="module-1", module_path="app/ingestion.py"),
        ),
        SemanticModuleProfile(
            module_id="module-2",
            relative_path="app/serving.py",
            language="python",
            purpose_statement="This module serves metrics through get_metrics_endpoint. It exists to expose processed information to downstream callers.",
            purpose_confidence=ConfidenceBand.MEDIUM,
            evidence_bundle=PurposeEvidenceBundle(bundle_id="bundle-2", module_id="module-2", module_path="app/serving.py"),
        ),
    ]

    domains = cluster_profiles(profiles)

    assert domains
    assert all(domain.domain_id for domain in domains)
    assert any(domain.label == "ingestion" for domain in domains)


class _StubEmbeddingProvider:
    def is_available(self) -> bool:
        return True

    def generate_text(self, request):  # pragma: no cover - not used
        raise AssertionError("generate_text should not be called")

    def embed_texts(self, request: EmbeddingRequest) -> EmbeddingResult:
        vectors = [[float(index), 0.0] for index, _text in enumerate(request.texts, start=1)]
        return EmbeddingResult(vectors=vectors, prompt_tokens=10, model=request.model)


def test_domain_clustering_falls_back_when_embedding_clusters_exceed_bounds() -> None:
    profiles = [
        SemanticModuleProfile(
            module_id=f"module-{index}",
            relative_path=f"app/module_{index}.py",
            language="python",
            purpose_statement=f"This module handles ingestion work around loader_{index}. It exists to bring raw inputs into the managed processing flow.",
            purpose_confidence=ConfidenceBand.MEDIUM,
            evidence_bundle=PurposeEvidenceBundle(bundle_id=f"bundle-{index}", module_id=f"module-{index}", module_path=f"app/module_{index}.py"),
        )
        for index in range(10)
    ]

    domains = cluster_profiles(
        profiles,
        provider=_StubEmbeddingProvider(),
        embedding_model="fake-embedding-model",
        min_clusters=5,
        max_clusters=8,
    )

    assert len(domains) <= 8
    assert any(domain.label == "ingestion" for domain in domains)
