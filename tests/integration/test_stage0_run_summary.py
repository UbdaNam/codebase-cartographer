import json
from pathlib import Path

from src.config import AppSettings
from src.orchestrator import CartographyOrchestrator


def test_stage3_run_writes_summary_manifest_inventory_and_structural_outputs(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("print('ok')", encoding="utf-8")
    settings = AppSettings(repo_root=tmp_path)

    summary = CartographyOrchestrator(settings).analyze(tmp_path)

    summary_path = Path(settings.resolved_artifact_dir()) / "runs" / summary.run_id / "run_summary.json"
    manifest_path = Path(settings.resolved_artifact_dir()) / "runs" / summary.run_id / "manifest.json"
    inventory_summary_path = Path(settings.resolved_artifact_dir()) / "runs" / summary.run_id / "inventory_summary.json"
    structural_summary_path = Path(settings.resolved_artifact_dir()) / "runs" / summary.run_id / "structural_summary.json"
    structural_index_path = Path(settings.resolved_artifact_dir()) / "runs" / summary.run_id / "structural_index.json"
    ast_index_path = Path(settings.resolved_artifact_dir()) / "runs" / summary.run_id / "ast_index.json"

    assert summary_path.exists()
    assert manifest_path.exists()
    assert inventory_summary_path.exists()
    assert structural_summary_path.exists()
    assert structural_index_path.exists()
    assert ast_index_path.exists()
    assert json.loads(summary_path.read_text(encoding="utf-8"))["status"] == "completed"
    assert summary.inventory_stats["supported_count"] == 1
    assert summary.structural_stats["parsed_files"] >= 1
