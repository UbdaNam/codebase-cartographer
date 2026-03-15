from pathlib import Path

from src.agents.navigator import NavigatorAgent
from src.config import AppSettings
from src.models.enums import AnalysisMethod, ConfidenceBand
from src.models.navigator import NavigatorAnswerItem, NavigatorCitation, NavigatorRequest


def test_attach_citations_does_not_backfill_unrelated_item_citations(tmp_path: Path) -> None:
    settings = AppSettings(repo_root=tmp_path, artifact_dir=tmp_path / ".cartography", semantic_provider_enabled=False)
    agent = NavigatorAgent(settings)
    state = {
        "request": NavigatorRequest(query_type="find_implementation", query_text="find ingestion"),
        "response_draft": [
            NavigatorAnswerItem(
                title="app/ingestion.py",
                answer_text="Loads raw orders.",
                confidence=ConfidenceBand.MEDIUM,
                citations=[
                    NavigatorCitation(
                        source_file="app/ingestion.py",
                        line_start=1,
                        line_end=4,
                        analysis_method=AnalysisMethod.STATIC_ANALYSIS,
                        trust_label="static_analysis",
                    )
                ],
            ),
            NavigatorAnswerItem(
                title="app/unknown.py",
                answer_text="No direct evidence.",
                confidence=ConfidenceBand.LOW,
                citations=[],
            ),
        ],
        "partial_result_flags": [],
        "trace_event_ids": [],
        "evidence_references": [],
        "retrieved_context": {},
    }

    result = agent.attach_citations_and_trust_metadata(state)

    assert len(result["response_draft"][0].citations) == 1
    assert result["response_draft"][1].citations == []
    assert "navigator_missing_citations" in result["response_draft"][1].warning_codes
    assert "navigator_missing_citations" in result["partial_result_flags"]
