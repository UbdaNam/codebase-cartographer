from src.models.enums import AnalysisMethod, ConfidenceBand
from src.models.evidence import EvidenceRecord
from src.models.graph import (
    DeadCodeCandidate,
    GraphPayload,
    ModuleNode,
    SurveyHub,
    SurveySummaryPayload,
    VelocityRecord,
)


def test_survey_summary_payload_serializes_deterministically() -> None:
    summary = SurveySummaryPayload(
        run_id="run-001",
        analysis_root="C:/repo",
        module_count=2,
        import_edge_count=1,
        circular_dependency_group_count=0,
        high_velocity_file_count=1,
        high_velocity_core_count=1,
        dead_code_candidate_count=1,
        top_hubs=[
            SurveyHub(module_id="b", relative_path="src/b.py", score=0.2),
            SurveyHub(module_id="a", relative_path="src/a.py", score=0.9),
        ],
        high_velocity_files=[
            VelocityRecord(module_id="b", relative_path="src/b.py", lookback_days=30, change_count=1),
            VelocityRecord(module_id="a", relative_path="src/a.py", lookback_days=30, change_count=3, is_high_velocity_core=True),
        ],
        dead_code_candidates=[
            DeadCodeCandidate(
                module_id="b",
                relative_path="src/b.py",
                reason_codes=["isolated_module", "low_recent_change_activity"],
                confidence=ConfidenceBand.LOW,
                evidence=[
                    EvidenceRecord(
                        source_path="src/b.py",
                        analysis_method=AnalysisMethod.HEURISTIC,
                        content_redacted=True,
                    )
                ],
            )
        ],
        warnings=["b", "a"],
        partial_result_flags=["x", "a"],
        stats={"b": 2, "a": 1},
    ).model_dump(mode="json")

    assert [item["module_id"] for item in summary["top_hubs"]] == ["a", "b"]
    assert [item["relative_path"] for item in summary["high_velocity_files"]] == ["src/a.py", "src/b.py"]
    assert summary["warnings"] == ["a", "b"]
    assert summary["partial_result_flags"] == ["a", "x"]
    assert summary["stats"] == {"a": 1, "b": 2}


def test_graph_payload_can_carry_surveyor_metadata() -> None:
    module = ModuleNode(relative_path="src/app.py", module_name="src.app", import_targets=["src.helper"])
    payload = GraphPayload(
        run_id="run-001",
        graph_metadata={"top_hubs": [{"module_id": module.node_id}]},
        nodes=[module],
        edges=[],
    ).model_dump(mode="json")

    assert payload["nodes"][0]["relative_path"] == "src/app.py"
    assert payload["graph_metadata"]["top_hubs"][0]["module_id"] == module.node_id
