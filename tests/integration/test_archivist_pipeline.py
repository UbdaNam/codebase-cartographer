from pathlib import Path

from src.config import AppSettings
from src.orchestrator import CartographyOrchestrator


def test_full_pipeline_writes_archivist_outputs(tmp_path: Path) -> None:
    fixture = Path("tests/fixtures/semanticist_repo").resolve()
    settings = AppSettings(
        repo_root=fixture,
        artifact_dir=tmp_path / ".cartography",
        semantic_provider_enabled=False,
    )

    summary = CartographyOrchestrator(settings).analyze(fixture)

    codebase = Path(summary.codebase_md_path or "").read_text(encoding="utf-8")
    onboarding = Path(summary.onboarding_brief_path or "").read_text(encoding="utf-8")
    trace = Path(summary.trace_log_path or "").read_text(encoding="utf-8")

    assert "## Architecture Overview" in codebase
    assert "## Module Purpose Index" in codebase
    assert "Observed facts:" in onboarding
    assert "Inferred conclusions:" in onboarding
    assert trace.strip()
    assert Path(summary.semantic_index_path or "").joinpath("snapshot.json").exists()
