from pathlib import Path

from langchain_core.messages import AIMessage

from src.agents.navigator import NavigatorAgent
from src.config import AppSettings
from src.models.navigator import NavigatorRequest
from src.orchestrator import CartographyOrchestrator


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


def test_forced_tool_queries_bypass_planner_model(tmp_path: Path) -> None:
    fixture = Path("tests/fixtures/semanticist_repo").resolve()
    settings = AppSettings(
        repo_root=fixture,
        artifact_dir=tmp_path / ".cartography",
        semantic_provider_enabled=False,
    )
    summary = CartographyOrchestrator(settings).analyze(fixture)
    agent = NavigatorAgent(settings)

    response = agent.query(
        NavigatorRequest(
            query_type="explain_module",
            query_text="Explain app/ingestion.py",
            target_identifier="app/ingestion.py",
            run_id=summary.run_id,
        )
    )

    assert response.results
    assert response.used_model_synthesis is False
    assert response.request.query_type == "explain_module"


def test_navigator_exposes_only_the_required_tools(tmp_path: Path) -> None:
    settings = AppSettings(repo_root=tmp_path, artifact_dir=tmp_path / ".cartography", semantic_provider_enabled=False)
    agent = NavigatorAgent(settings)

    assert sorted(tool.name for tool in agent._tools) == [
        "blast_radius",
        "explain_module",
        "find_implementation",
        "trace_lineage",
    ]


def test_tool_round_limit_sets_partial_flag(tmp_path: Path) -> None:
    fixture = Path("tests/fixtures/semanticist_repo").resolve()
    settings = AppSettings(
        repo_root=fixture,
        artifact_dir=tmp_path / ".cartography",
        semantic_provider_enabled=True,
        openrouter_api_key="test-key",
        navigator_max_tool_rounds=1,
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
                        "id": "tool-call-1",
                        "type": "tool_call",
                    }
                ],
            )
        ]
    )
    agent._chat_model = _FakeChatModel(
        (
            '{"summary": "Order ingestion is implemented in the ingestion module.", '
            '"observed_facts": ["The semantic index returned app/ingestion.py."], '
            '"inferred_notes": ["The rest of the pipeline builds on that ingestion path."]}'
        )
    )

    response = agent.query(
        NavigatorRequest(
            query_text="Where is order ingestion implemented?",
            run_id=summary.run_id,
        )
    )

    assert "navigator_tool_round_limit_reached" in response.partial_result_flags
    assert response.results
