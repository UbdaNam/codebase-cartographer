import json
from pathlib import Path

from src.config import AppSettings
from src.orchestrator import CartographyOrchestrator


def test_structural_pipeline_writes_deterministic_artifacts_for_polyglot_repo() -> None:
    repo_root = Path("tests/fixtures/structural_polyglot_repo").resolve()
    settings = AppSettings(repo_root=repo_root)

    summary = CartographyOrchestrator(settings).analyze(repo_root)
    run_dir = Path(settings.resolved_artifact_dir()) / "runs" / summary.run_id

    structural_index_path = run_dir / "structural_index.json"
    ast_index_path = run_dir / "ast_index.json"
    structural_summary_path = run_dir / "structural_summary.json"

    assert structural_index_path.exists()
    assert ast_index_path.exists()
    assert structural_summary_path.exists()
    assert json.loads(structural_summary_path.read_text(encoding="utf-8"))["record_count"] > 0


def test_structural_pipeline_reports_partial_and_unsupported_results() -> None:
    repo_root = Path("tests/fixtures/structural_malformed_repo").resolve()
    settings = AppSettings(repo_root=repo_root)

    summary = CartographyOrchestrator(settings).analyze(repo_root)
    run_dir = Path(settings.resolved_artifact_dir()) / "runs" / summary.run_id
    structural_index = json.loads((run_dir / "structural_index.json").read_text(encoding="utf-8"))
    by_path = {entry["file_path"]: entry for entry in structural_index["file_results"]}

    assert by_path["broken.py"]["parse_status"] == "partial"
    assert by_path["notes.ipynb"]["parse_status"] == "partial"
    assert by_path["docs/readme.txt"]["parse_status"] == "unsupported"
