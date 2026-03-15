from pathlib import Path

from src.config import AppSettings
from src.orchestrator import CartographyOrchestrator


def test_run_summary_exposes_semanticist_paths(tmp_path: Path) -> None:
    fixture = Path("tests/fixtures/semanticist_repo").resolve()
    settings = AppSettings(repo_root=fixture, semantic_provider_enabled=False)

    summary = CartographyOrchestrator(settings).analyze(fixture)

    assert summary.module_semantics_path
    assert summary.documentation_drift_path
    assert summary.domain_map_path
    assert summary.day_one_answers_path
    assert summary.codebase_md_path
    assert summary.onboarding_brief_path
    assert summary.trace_log_path
    assert "analyzed_module_count" in summary.semantic_stats
    assert "semantic_index_entry_count" in summary.archivist_stats
