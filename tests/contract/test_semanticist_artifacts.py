import json
from pathlib import Path

from src.config import AppSettings
from src.orchestrator import CartographyOrchestrator


def test_semanticist_artifacts_are_written_and_shaped(tmp_path: Path) -> None:
    fixture = Path("tests/fixtures/semanticist_repo").resolve()
    settings = AppSettings(repo_root=fixture, semantic_provider_enabled=False)

    summary = CartographyOrchestrator(settings).analyze(fixture)
    run_dir = Path(settings.resolved_artifact_dir()) / "runs" / summary.run_id
    module_semantics_path = run_dir / "module_semantics.json"
    documentation_drift_path = run_dir / "documentation_drift.json"
    domain_map_path = run_dir / "domain_map.json"
    day_one_answers_path = run_dir / "day_one_answers.json"

    assert module_semantics_path.exists()
    assert documentation_drift_path.exists()
    assert domain_map_path.exists()
    assert day_one_answers_path.exists()

    module_payload = json.loads(module_semantics_path.read_text(encoding="utf-8"))
    answer_payload = json.loads(day_one_answers_path.read_text(encoding="utf-8"))

    assert "profiles" in module_payload
    assert "answers" in answer_payload
    assert len(answer_payload["answers"]) == 5
