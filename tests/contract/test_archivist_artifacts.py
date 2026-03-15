from pathlib import Path

from src.config import AppSettings
from src.orchestrator import CartographyOrchestrator


def test_archivist_artifacts_are_written(tmp_path: Path) -> None:
    fixture = Path("tests/fixtures/semanticist_repo").resolve()
    settings = AppSettings(
        repo_root=fixture,
        artifact_dir=tmp_path / ".cartography",
        semantic_provider_enabled=False,
    )

    summary = CartographyOrchestrator(settings).analyze(fixture)

    assert Path(summary.codebase_md_path or "").exists()
    assert Path(summary.onboarding_brief_path or "").exists()
    assert Path(summary.semantic_index_path or "").is_dir()
    assert Path(summary.trace_log_path or "").exists()
