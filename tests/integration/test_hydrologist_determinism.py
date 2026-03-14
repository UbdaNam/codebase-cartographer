from pathlib import Path

from src.config import AppSettings
from src.orchestrator import CartographyOrchestrator


def test_orchestrator_summary_includes_lineage_outputs() -> None:
    repo_root = Path('tests/fixtures/hydrologist_sql_repo').resolve()
    summary = CartographyOrchestrator(AppSettings(repo_root=repo_root, semantic_provider_enabled=False)).analyze(repo_root)
    assert summary.lineage_graph_path
    assert summary.lineage_summary_path
    assert summary.lineage_stats['dataset_count'] >= 1
