import json
from pathlib import Path

from src.config import AppSettings
from src.orchestrator import CartographyOrchestrator


def test_semanticist_pipeline_generates_semantic_outputs() -> None:
    fixture = Path("tests/fixtures/semanticist_repo").resolve()
    settings = AppSettings(repo_root=fixture, semantic_provider_enabled=False)

    summary = CartographyOrchestrator(settings).analyze(fixture)
    run_dir = Path(settings.resolved_artifact_dir()) / "runs" / summary.run_id
    payload = json.loads((run_dir / "module_semantics.json").read_text(encoding="utf-8"))
    domains = json.loads((run_dir / "domain_map.json").read_text(encoding="utf-8"))

    assert payload["profiles"]
    assert all(profile["purpose_statement"] for profile in payload["profiles"])
    assert domains["domains"]
