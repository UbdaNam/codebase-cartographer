from pathlib import Path

from src.analyzers.day_one_synthesis import DAY_ONE_QUESTIONS, synthesize_day_one_answers
from src.config import AppSettings
from src.llm.budget import ContextWindowBudget
from src.llm.provider import ChatRequest, ChatResult
from src.models.enums import AnalysisMethod, ConfidenceBand, SupportStatus
from src.models.graph import DatasetNode, GraphEdge, GraphPayload, ModuleNode, TransformationNode
from src.models.semantic import DomainCluster, EvidenceReference, PurposeEvidenceBundle, SemanticModuleProfile


class _StubProvider:
    def __init__(self, response_text: str):
        self.response_text = response_text

    def is_available(self) -> bool:
        return True

    def generate_text(self, request: ChatRequest) -> ChatResult:
        return ChatResult(
            text=self.response_text,
            prompt_tokens=120,
            completion_tokens=80,
            model=request.model,
        )

    def embed_texts(self, request):  # pragma: no cover - not used
        raise AssertionError("embed_texts should not be called")


def test_day_one_synthesis_uses_provider_response_with_line_citations(tmp_path: Path) -> None:
    evidence_ref = EvidenceReference(
        source_kind="code_excerpt",
        repository_path="app/ingest.py",
        line_start=10,
        line_end=18,
        quoted_text="def load_orders(): ...",
        observed_or_inferred="observed",
        analysis_method=AnalysisMethod.STATIC_ANALYSIS,
        confidence=ConfidenceBand.MEDIUM,
    )
    profile = SemanticModuleProfile(
        module_id="node:ingest",
        relative_path="app/ingest.py",
        language="python",
        purpose_statement="This module ingests order data and prepares warehouse-ready records.",
        purpose_confidence=ConfidenceBand.MEDIUM,
        evidence_references=[evidence_ref],
        source_excerpt_refs=[evidence_ref],
        evidence_bundle=PurposeEvidenceBundle(
            bundle_id="bundle-1",
            module_id="node:ingest",
            module_path="app/ingest.py",
        ),
    )
    serve_ref = EvidenceReference(
        source_kind="code_excerpt",
        repository_path="app/serve.py",
        line_start=5,
        line_end=14,
        quoted_text="def publish_metrics(): ...",
        observed_or_inferred="observed",
        analysis_method=AnalysisMethod.STATIC_ANALYSIS,
        confidence=ConfidenceBand.MEDIUM,
    )
    serve_profile = SemanticModuleProfile(
        module_id="node:serve",
        relative_path="app/serve.py",
        language="python",
        purpose_statement="This module serves processed metrics to downstream readers.",
        purpose_confidence=ConfidenceBand.MEDIUM,
        evidence_references=[serve_ref],
        source_excerpt_refs=[serve_ref],
        evidence_bundle=PurposeEvidenceBundle(
            bundle_id="bundle-2",
            module_id="node:serve",
            module_path="app/serve.py",
        ),
    )
    module_graph = GraphPayload(
        run_id="run-1",
        nodes=[
            ModuleNode(
                node_id="node:ingest",
                relative_path="app/ingest.py",
                module_name="app.ingest",
                language_or_dialect="python",
                support_status=SupportStatus.SUPPORTED,
                confidence=ConfidenceBand.HIGH,
                pagerank_score=0.9,
                change_velocity_recent=3,
                evidence=[],
            ),
            ModuleNode(
                node_id="node:serve",
                relative_path="app/serve.py",
                module_name="app.serve",
                language_or_dialect="python",
                support_status=SupportStatus.SUPPORTED,
                confidence=ConfidenceBand.HIGH,
                pagerank_score=0.6,
                change_velocity_recent=1,
                evidence=[],
            ),
        ],
        edges=[
            GraphEdge(
                source_node_id="node:ingest",
                target_node_id="node:serve",
                kind="imports",
            )
        ],
    )
    raw_dataset = DatasetNode(dataset_name="raw.orders", canonical_name="raw.orders")
    output_dataset = DatasetNode(dataset_name="warehouse.metrics", canonical_name="warehouse.metrics")
    transformation = TransformationNode(
        node_id="transform:ingest",
        transformation_name="app.ingest.load_orders",
        module_or_file_id="node:ingest",
        path="app/ingest.py",
    )
    lineage_graph = GraphPayload(
        run_id="run-1",
        nodes=[raw_dataset, output_dataset, transformation],
        edges=[
            GraphEdge(source_node_id=raw_dataset.node_id, target_node_id=transformation.node_id, kind="consumes"),
            GraphEdge(source_node_id=transformation.node_id, target_node_id=output_dataset.node_id, kind="produces"),
        ],
    )
    domains = [
        DomainCluster(
            label="ingestion",
            summary="Ingestion modules move data from raw inputs into managed flows.",
            confidence=ConfidenceBand.MEDIUM,
            module_ids=["node:ingest"],
        )
    ]
    response_text = (
        '{'
        '"answers": ['
        + ",".join(
            [
                (
                    '{"question_id":"%s","observation":"Observed evidence in app/ingest.py.","inference":"This supports the requested answer.","confidence":"high","evidence_ids":["%s"]}'
                    % (question_id, evidence_ref.reference_id)
                )
                for question_id, _ in DAY_ONE_QUESTIONS
            ]
        )
        + "]}"
    )

    answers, warnings, is_partial = synthesize_day_one_answers(
        prepared_repo_root=Path(tmp_path),
        settings=AppSettings(repo_root=tmp_path, semantic_provider_enabled=False),
        module_graph=module_graph,
        lineage_graph=lineage_graph,
        profiles=[profile, serve_profile],
        domains=domains,
        provider=_StubProvider(response_text),
        budget=ContextWindowBudget(max_prompt_tokens=50_000, max_completion_tokens=5_000, max_requests=5),
    )

    assert not warnings
    assert is_partial is False
    assert len(answers) == 5
    assert all(answer.evidence_references for answer in answers)
    assert all(answer.evidence_references[0].repository_path == "app/ingest.py" for answer in answers)
    assert all(answer.evidence_references[0].line_start == 10 for answer in answers)
    assert answers[0].answer_text
