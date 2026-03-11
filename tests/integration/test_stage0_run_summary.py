import json
from pathlib import Path

from src.config import AppSettings
from src.orchestrator import Stage0Orchestrator


def test_stage0_run_writes_summary_and_manifest(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("print('ok')", encoding="utf-8")
    settings = AppSettings(repo_root=tmp_path)

    summary = Stage0Orchestrator(settings).analyze(tmp_path)

    summary_path = Path(settings.resolved_artifact_dir()) / "runs" / summary.run_id / "run_summary.json"
    manifest_path = Path(settings.resolved_artifact_dir()) / "runs" / summary.run_id / "manifest.json"

    assert summary_path.exists()
    assert manifest_path.exists()
    assert json.loads(summary_path.read_text(encoding="utf-8"))["status"] == "completed"
