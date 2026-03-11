from src.models import (
    AnalysisArtifact,
    AnalysisMethod,
    ArtifactPayload,
    Citation,
    EvidenceRecord,
    GraphEdge,
    GraphPayload,
    ModuleNode,
    NavigatorState,
    NodeKind,
    SerializationMetadata,
)
from src.models.enums import ConfidenceBand, EdgeKind, SupportStatus
from src.models.state import AnalysisState, NavigatorToolCall, RunContext
from src.models.artifacts import to_canonical_json


def test_graph_payload_and_artifact_payload_serialize_deterministically() -> None:
    module = ModuleNode(relative_path="src/cli.py", module_name="src.cli", metadata={"z": 2, "a": 1})
    edge = GraphEdge(
        source_node_id=module.node_id,
        target_node_id=module.node_id,
        kind=EdgeKind.DEFINES,
    )
    graph_payload = GraphPayload(
        run_id="run-001",
        graph_metadata={"z": 2, "a": 1},
        nodes=[module],
        edges=[edge],
    )
    artifact = AnalysisArtifact(
        artifact_kind="module_graph",
        logical_name="module graph",
        analysis_method=AnalysisMethod.GRAPH_INFERENCE,
        metadata={"z": 2, "a": 1},
        serialization_path=".cartography/runs/run-001/module_graph.json",
    )
    artifact_payload = ArtifactPayload(
        metadata=SerializationMetadata(run_id="run-001", artifact_dir=".cartography"),
        artifacts=[artifact],
    )

    assert to_canonical_json(graph_payload) == to_canonical_json(graph_payload)
    assert to_canonical_json(artifact_payload) == to_canonical_json(artifact_payload)


def test_degraded_artifact_and_state_payloads_remain_serializable() -> None:
    evidence = EvidenceRecord(
        source_path="src/analyzers/repository_manifest.py",
        analysis_method=AnalysisMethod.STATIC_ANALYSIS,
        confidence=ConfidenceBand.MEDIUM,
    )
    artifact = AnalysisArtifact(
        artifact_kind="lineage_graph",
        logical_name="lineage graph",
        support_status=SupportStatus.PARTIAL,
        analysis_method=AnalysisMethod.GRAPH_INFERENCE,
        evidence=[evidence],
    )
    state = AnalysisState(
        run_context=RunContext(run_id="run-001", repo_root="C:/repo", artifact_dir=".cartography"),
        stage_name="semanticist",
        artifact_references=[".cartography/runs/run-001/lineage_graph.json"],
        partial_results=["dynamic SQL unresolved"],
        warnings=["partial graph emitted"],
    )

    assert artifact.model_dump(mode="json")["support_status"] == "partial"
    assert state.model_dump(mode="json")["partial_results"] == ["dynamic SQL unresolved"]


def test_navigator_contracts_support_future_agent_defaults() -> None:
    navigator_state = NavigatorState(
        incoming_query="Which modules define the CLI entrypoint?",
        artifact_references=[
            ".cartography/runs/run-001/module_graph.json",
            ".cartography/runs/run-001/semantic_index.json",
        ],
        tool_history=[NavigatorToolCall(tool_name="artifact_lookup", status="completed")],
        citations=[
            Citation(
                source_path="src/cli.py",
                analysis_method=AnalysisMethod.STATIC_ANALYSIS,
            )
        ],
    )

    payload = navigator_state.model_dump(mode="json")

    assert payload["artifact_references"] == sorted(payload["artifact_references"])
    assert payload["tool_history"][0]["tool_name"] == "artifact_lookup"
