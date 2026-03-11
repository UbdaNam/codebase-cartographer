from pathlib import Path

from src.config import AppSettings
from src.orchestrator import Stage0Orchestrator


def test_safe_scan_skips_secret_files_without_persisting_contents(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("SECRET_TOKEN=do-not-store", encoding="utf-8")
    (tmp_path / "app.py").write_text("print('safe')", encoding="utf-8")
    settings = AppSettings(repo_root=tmp_path)

    summary = Stage0Orchestrator(settings).analyze(tmp_path)
    run_dir = Path(settings.resolved_artifact_dir()) / "runs" / summary.run_id
    persisted = (run_dir / "manifest.json").read_text(encoding="utf-8")

    assert "SECRET_TOKEN=do-not-store" not in persisted
    assert ".env" in persisted
