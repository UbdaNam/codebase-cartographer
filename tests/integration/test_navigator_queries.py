from pathlib import Path

from langchain_core.messages import AIMessage

from src.agents.navigator import NavigatorAgent
from src.config import AppSettings
from src.models.navigator import NavigatorRequest
from src.orchestrator import CartographyOrchestrator


def test_navigator_returns_citations_for_explain_module(tmp_path: Path) -> None:
    fixture = Path("tests/fixtures/semanticist_repo").resolve()
    settings = AppSettings(
        repo_root=fixture,
        artifact_dir=tmp_path / ".cartography",
        semantic_provider_enabled=False,
    )
    summary = CartographyOrchestrator(settings).analyze(fixture)

    response = NavigatorAgent(settings).query(
        NavigatorRequest(
            query_type="explain_module",
            query_text="Explain app/ingestion.py",
            target_identifier="app/ingestion.py",
            run_id=summary.run_id,
        )
    )

    assert response.results
    citation = response.results[0].citations[0]
    assert citation.source_file
    assert citation.analysis_method
    assert citation.trust_label


def test_navigator_trace_lineage_returns_graph_based_answer(tmp_path: Path) -> None:
    fixture = Path("tests/fixtures/semanticist_repo").resolve()
    settings = AppSettings(
        repo_root=fixture,
        artifact_dir=tmp_path / ".cartography",
        semantic_provider_enabled=False,
    )
    summary = CartographyOrchestrator(settings).analyze(fixture)

    response = NavigatorAgent(settings).query(
        NavigatorRequest(
            query_type="trace_lineage",
            query_text="Trace lineage for order_metrics.parquet",
            target_identifier="order_metrics.parquet",
            direction="both",
            run_id=summary.run_id,
        )
    )

    assert response.results
    assert "lineage" in response.results[0].inferred_notes[0].lower()


def test_navigator_provider_unavailable_repo_summary_uses_artifact_fallback(tmp_path: Path) -> None:
    fixture = Path("tests/fixtures/semanticist_repo").resolve()
    settings = AppSettings(
        repo_root=fixture,
        artifact_dir=tmp_path / ".cartography",
        semantic_provider_enabled=False,
    )
    summary = CartographyOrchestrator(settings).analyze(fixture)

    response = NavigatorAgent(settings).query(
        NavigatorRequest(
            query_text="what is this codebase about?",
            run_id=summary.run_id,
        )
    )

    assert response.results
    assert response.results[0].title == "Repository overview"
    assert response.results[0].citations
    assert "navigator_model_unavailable" in response.partial_result_flags


class _FakePlannerModel:
    def __init__(self, responses: list[AIMessage]):
        self._responses = list(responses)

    def invoke(self, _messages):
        if not self._responses:
            raise AssertionError("planner invoked more times than expected")
        return self._responses.pop(0)


class _FakeChatModel:
    def __init__(self, response_text: str):
        self.response_text = response_text

    def invoke(self, _messages):
        return AIMessage(content=self.response_text)


def test_navigator_answers_repo_summary_query_from_repo_context(tmp_path: Path) -> None:
    fixture = Path("tests/fixtures/semanticist_repo").resolve()
    settings = AppSettings(
        repo_root=fixture,
        artifact_dir=tmp_path / ".cartography",
        semantic_provider_enabled=True,
        openrouter_api_key="test-key",
    )
    summary = CartographyOrchestrator(settings).analyze(fixture)
    agent = NavigatorAgent(settings)
    agent._planner_model = _FakePlannerModel(
        [
            AIMessage(
                content=(
                    "This repository ingests order data, transforms it into warehouse metrics, "
                    "and captures enough architecture context for onboarding."
                )
            )
        ]
    )
    agent._chat_model = _FakeChatModel(
        (
            '{"summary": "This repository ingests raw order data and turns it into curated warehouse outputs.", '
            '"observed_facts": ["Surveyor and Hydrologist artifacts describe ingestion and transformation paths."], '
            '"inferred_notes": ["The repository centers on data processing and onboarding context generation."]}'
        )
    )

    response = agent.query(
        NavigatorRequest(
            query_text="what is this codebase about?",
            run_id=summary.run_id,
        )
    )

    assert response.summary.lower().startswith("this repository ingests raw order data")
    assert response.results
    assert response.results[0].title == "Repository overview"
    assert response.results[0].citations
    assert all(citation.source_file not in {"", "."} for citation in response.results[0].citations)
    assert response.results[0].observed_facts
    assert response.results[0].inferred_notes
    assert response.used_model_synthesis is True


def test_navigator_records_planner_and_tool_trace_events(tmp_path: Path) -> None:
    fixture = Path("tests/fixtures/semanticist_repo").resolve()
    settings = AppSettings(
        repo_root=fixture,
        artifact_dir=tmp_path / ".cartography",
        semantic_provider_enabled=True,
        openrouter_api_key="test-key",
        navigator_max_tool_rounds=2,
    )
    summary = CartographyOrchestrator(settings).analyze(fixture)
    agent = NavigatorAgent(settings)
    agent._planner_model = _FakePlannerModel(
        [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "find_implementation",
                        "args": {"concept": "order ingestion"},
                        "id": "call-find-implementation",
                        "type": "tool_call",
                    }
                ],
            ),
            AIMessage(content="Order ingestion is implemented in the ingestion module and then consumed by transforms."),
        ]
    )
    agent._chat_model = _FakeChatModel(
        (
            '{"summary": "Order ingestion is implemented in the ingestion module and consumed by transforms.", '
            '"observed_facts": ["The semantic index points to app/ingestion.py."], '
            '"inferred_notes": ["Transforms build curated metrics on top of that ingestion step."]}'
        )
    )

    response = agent.query(
        NavigatorRequest(
            query_text="Where is order ingestion implemented?",
            run_id=summary.run_id,
        )
    )

    assert response.summary.lower().startswith("order ingestion is implemented")
    assert response.results
    trace_log = (tmp_path / ".cartography" / "runs" / summary.run_id / "cartography_trace.jsonl").read_text(encoding="utf-8")
    assert "planner_decision" in trace_log
    assert "tool_find_implementation" in trace_log
    assert "synthesize_response" in trace_log
