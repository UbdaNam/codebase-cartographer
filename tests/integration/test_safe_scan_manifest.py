from pathlib import Path

from src.config import AppSettings
from src.orchestrator import CartographyOrchestrator


def test_safe_scan_skips_secret_files_without_persisting_contents(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("SECRET_TOKEN=do-not-store", encoding="utf-8")
    (tmp_path / "app.py").write_text("print('safe')", encoding="utf-8")
    settings = AppSettings(repo_root=tmp_path)

    summary = CartographyOrchestrator(settings).analyze(tmp_path)
    run_dir = Path(settings.resolved_artifact_dir()) / "runs" / summary.run_id
    persisted = (run_dir / "manifest.json").read_text(encoding="utf-8")

    assert "SECRET_TOKEN=do-not-store" not in persisted
    assert ".env" in persisted


def test_inventory_artifacts_include_manifest_and_summary(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("print('ok')", encoding="utf-8")
    (tmp_path / "package.json").write_text('{"name":"demo"}', encoding="utf-8")
    settings = AppSettings(repo_root=tmp_path)

    summary = CartographyOrchestrator(settings).analyze(tmp_path)
    run_dir = Path(settings.resolved_artifact_dir()) / "runs" / summary.run_id
    manifest_path = run_dir / "manifest.json"
    inventory_summary_path = run_dir / "inventory_summary.json"

    assert manifest_path.exists()
    assert inventory_summary_path.exists()
    assert str(inventory_summary_path).replace("\\", "/") == summary.inventory_summary_path
