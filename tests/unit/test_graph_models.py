from src.models.artifacts import AnalysisArtifact
from src.models.enums import AnalysisMethod, EdgeKind, NodeKind, SkipReason, SupportStatus
from src.models.evidence import EvidenceRecord
from src.models.graph import DatasetNode, GraphEdge, GraphPayload, ModuleNode, TransformationNode


def test_graph_models_generate_deterministic_ids() -> None:
    module = ModuleNode(relative_path="src/cli.py", module_name="src.cli")
    dataset = DatasetNode(dataset_name="warehouse.orders", namespace="analytics")
    edge = GraphEdge(
        source_node_id=module.node_id,
        target_node_id=dataset.node_id,
        kind=EdgeKind.CONSUMES,
    )

    assert module.node_id == ModuleNode(relative_path="src/cli.py", module_name="src.cli").node_id
    assert dataset.kind == NodeKind.DATASET
    assert edge.edge_id == GraphEdge(
        source_node_id=module.node_id,
        target_node_id=dataset.node_id,
        kind=EdgeKind.CONSUMES,
    ).edge_id


def test_graph_payload_serializes_nodes_and_edges_in_stable_order() -> None:
    module = ModuleNode(relative_path="src/orchestrator.py", module_name="src.orchestrator")
    transform = TransformationNode(transformation_name="build_manifest", operation_type="inventory")
    edge = GraphEdge(
        source_node_id=module.node_id,
        target_node_id=transform.node_id,
        kind=EdgeKind.DEFINES,
    )

    payload = GraphPayload(
        run_id="run-001",
        graph_metadata={"b": 2, "a": 1},
        nodes=[transform, module],
        edges=[edge],
    ).model_dump(mode="json")

    assert payload["graph_metadata"] == {"a": 1, "b": 2}
    assert [node["node_id"] for node in payload["nodes"]] == sorted(node["node_id"] for node in payload["nodes"])


def test_partial_and_skipped_contracts_are_supported() -> None:
    evidence = EvidenceRecord(
        source_path="src/analyzers/repository_manifest.py",
        line_start=10,
        line_end=20,
        analysis_method=AnalysisMethod.STATIC_ANALYSIS,
    )
    partial_node = ModuleNode(
        relative_path="src/analyzers/repository_manifest.py",
        module_name="src.analyzers.repository_manifest",
        support_status=SupportStatus.PARTIAL,
        evidence=[evidence],
    )
    skipped_artifact = AnalysisArtifact(
        artifact_kind="semantic_index",
        logical_name="semantic index",
        support_status=SupportStatus.SKIPPED,
        skip_reason=SkipReason.SECRET_SENSITIVE,
    )

    assert partial_node.support_status == SupportStatus.PARTIAL
    assert skipped_artifact.skip_reason == SkipReason.SECRET_SENSITIVE
