from src.agents import DEFAULT_AGENT_BOUNDARIES
from src.cli import app
from src.orchestrator import CartographyOrchestrator, Stage0Orchestrator


def test_agent_boundaries_are_declared() -> None:
    names = [boundary.name for boundary in DEFAULT_AGENT_BOUNDARIES]

    assert names == ["Surveyor", "Hydrologist", "Semanticist", "Archivist", "Navigator"]


def test_cli_and_orchestrator_boundaries_exist() -> None:
    assert app is not None
    assert callable(CartographyOrchestrator.query)
    assert callable(Stage0Orchestrator.query)
