from pathlib import Path

from src.config import AppSettings
from src.orchestrator import CartographyOrchestrator


def test_orchestrator_runs_semanticist_after_hydrologist() -> None:
    fixture = Path("tests/fixtures/semanticist_repo").resolve()
    settings = AppSettings(repo_root=fixture, semantic_provider_enabled=False)

    summary = CartographyOrchestrator(settings).analyze(fixture)

    assert summary.lineage_graph_path
    assert summary.module_semantics_path
    assert summary.day_one_answers_path
