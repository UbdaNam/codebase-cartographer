import pytest

from src.models.enums import AnalysisMethod, RunStatus, SkipReason
from src.models.evidence import Citation, EvidenceRecord
from src.models.state import AnalysisState, NavigatorState, NavigatorToolCall, RunContext, SkippedSummary


def test_run_context_accepts_stage0_artifact_root_alias() -> None:
    context = RunContext(
        run_id="run-001",
        repo_root="C:/repo",
        artifact_root="C:/repo/.cartography",
        status=RunStatus.RUNNING,
    )

    payload = context.model_dump(mode="json")

    assert payload["artifact_dir"] == "C:/repo/.cartography"


def test_analysis_state_defaults_and_skipped_summaries() -> None:
    context = RunContext(run_id="run-001", repo_root="C:/repo", artifact_dir=".cartography")
    state = AnalysisState(
        run_context=context,
        stage_name="survey",
        skipped_file_summaries=[
            SkippedSummary(path="secrets/.env", skip_reason=SkipReason.SECRET_SENSITIVE, is_secret_sensitive=True)
        ],
    )

    assert state.partial_results == []
    assert state.skipped_file_summaries[0].skip_reason == SkipReason.SECRET_SENSITIVE


def test_navigator_state_defaults_and_updates() -> None:
    evidence = EvidenceRecord(source_path="src/cli.py", analysis_method=AnalysisMethod.STATIC_ANALYSIS)
    citation = Citation(source_path="src/cli.py", analysis_method=AnalysisMethod.STATIC_ANALYSIS)
    state = NavigatorState(
        incoming_query="How is the CLI wired?",
        artifact_references=[".cartography/runs/run-001/module_graph.json"],
        retrieved_evidence=[evidence],
        tool_history=[NavigatorToolCall(tool_name="graph_lookup", status="completed")],
        citations=[citation],
    )

    assert state.final_answer is None
    assert state.tool_history[0].tool_name == "graph_lookup"


def test_navigator_state_requires_non_blank_query() -> None:
    with pytest.raises(ValueError):
        NavigatorState(incoming_query="   ")
