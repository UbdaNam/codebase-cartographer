import json
from pathlib import Path

from src.config import AppSettings
from src.orchestrator import CartographyOrchestrator


def test_semanticist_detects_documentation_drift() -> None:
    fixture = Path("tests/fixtures/semanticist_partial_repo").resolve()
    settings = AppSettings(repo_root=fixture, semantic_provider_enabled=False)

    summary = CartographyOrchestrator(settings).analyze(fixture)
    run_dir = Path(settings.resolved_artifact_dir()) / "runs" / summary.run_id
    payload = json.loads((run_dir / "documentation_drift.json").read_text(encoding="utf-8"))

    assert payload["drift_records"]
    assert payload["drift_records"][0]["drift_type"] in {"contradiction", "omission", "outdated"}
