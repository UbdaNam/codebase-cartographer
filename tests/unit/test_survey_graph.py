from pathlib import Path

from src.graph.survey import (
    build_import_edges,
    build_import_graph,
    build_module_node,
    compute_high_velocity_core,
    compute_pagerank,
    compute_strongly_connected_components,
    relative_path_to_module_name,
)
from src.models.enums import AnalysisMethod, SupportStatus
from src.models.evidence import EvidenceRecord
from src.models.structural import ParseStatus, StructuralFileResult, StructuralRecord, StructuralSymbolKind


def _file_result(path: str, records: list[StructuralRecord]) -> StructuralFileResult:
    return StructuralFileResult(
        manifest_file_id=path,
        file_path=path,
        language="python",
        support_status=SupportStatus.SUPPORTED,
        parse_status=ParseStatus.PARSED,
        records=records,
    )


def test_relative_path_to_module_name_normalizes_init_files() -> None:
    assert relative_path_to_module_name("pkg/__init__.py") == "pkg"
    assert relative_path_to_module_name("src/app.py") == "src.app"


def test_build_import_edges_and_analytics_are_deterministic(tmp_path: Path) -> None:
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "pkg" / "a.py").write_text("from pkg import b\n", encoding="utf-8")
    (tmp_path / "pkg" / "b.py").write_text("from pkg import a\n", encoding="utf-8")

    import_a = StructuralRecord(
        file_path="pkg/a.py",
        language="python",
        symbol_kind=StructuralSymbolKind.IMPORT,
        analysis_method=AnalysisMethod.STATIC_ANALYSIS,
        evidence=[EvidenceRecord(source_path="pkg/a.py", line_start=1, line_end=1, analysis_method=AnalysisMethod.STATIC_ANALYSIS)],
    )
    import_b = StructuralRecord(
        file_path="pkg/b.py",
        language="python",
        symbol_kind=StructuralSymbolKind.IMPORT,
        analysis_method=AnalysisMethod.STATIC_ANALYSIS,
        evidence=[EvidenceRecord(source_path="pkg/b.py", line_start=1, line_end=1, analysis_method=AnalysisMethod.STATIC_ANALYSIS)],
    )
    results = [_file_result("pkg/a.py", [import_a]), _file_result("pkg/b.py", [import_b])]
    nodes = [build_module_node(result) for result in results]
    edges, unresolved, _ = build_import_edges(tmp_path, nodes, results)
    graph = build_import_graph(nodes, edges)
    hubs = compute_pagerank(graph, {node.node_id: node for node in nodes})
    cycles = compute_strongly_connected_components(graph, {node.node_id: node for node in nodes})

    assert len(edges) == 2
    assert unresolved == []
    assert len(hubs) == 2
    assert len(cycles) == 1
    assert cycles[0].relative_paths == ["pkg/a.py", "pkg/b.py"]


def test_compute_high_velocity_core_selects_minimal_sorted_prefix() -> None:
    core = compute_high_velocity_core(
        {"a.py": 8, "b.py": 1, "c.py": 1},
        lookback_days=30,
        change_share_threshold=0.8,
        module_id_by_path={"a.py": "node:a", "b.py": "node:b", "c.py": "node:c"},
    )

    assert [record.relative_path for record in core] == ["a.py"]
