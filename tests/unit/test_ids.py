import pytest

from src.models.enums import EdgeKind, NodeKind
from src.utils.ids import build_artifact_id, build_edge_id, build_node_id, normalize_relative_path


def test_normalize_relative_path_rejects_analysis_root_escape() -> None:
    with pytest.raises(ValueError):
        normalize_relative_path("../secrets.env")


def test_node_and_edge_ids_are_deterministic() -> None:
    node_id = build_node_id(NodeKind.MODULE, canonical_name="src.cli", path="src/cli.py")
    repeat_node_id = build_node_id(NodeKind.MODULE, canonical_name="src.cli", path="src/cli.py")
    edge_id = build_edge_id(EdgeKind.IMPORTS, source_node_id=node_id, target_node_id="node:123")
    repeat_edge_id = build_edge_id(EdgeKind.IMPORTS, source_node_id=node_id, target_node_id="node:123")

    assert node_id == repeat_node_id
    assert edge_id == repeat_edge_id
    assert node_id.startswith("node:")
    assert edge_id.startswith("edge:")


def test_artifact_id_uses_logical_name_and_path() -> None:
    artifact_id = build_artifact_id(
        "graph_payload",
        logical_name="module graph",
        serialization_path=".cartography/runs/demo/module_graph.json",
    )

    assert artifact_id.startswith("artifact:")
