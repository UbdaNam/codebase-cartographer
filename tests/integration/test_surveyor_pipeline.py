import json
import shutil
import subprocess
from pathlib import Path

import pytest

from src.config import AppSettings
from src.orchestrator import CartographyOrchestrator


def _copy_fixture(src: Path, dest: Path) -> Path:
    shutil.copytree(src, dest)
    shutil.rmtree(dest / ".cartography", ignore_errors=True)
    return dest


def test_surveyor_pipeline_writes_module_graph_and_summary(tmp_path: Path) -> None:
    repo_root = _copy_fixture(Path("tests/fixtures/surveyor_repo"), tmp_path / "surveyor_repo")
    settings = AppSettings(repo_root=repo_root, semantic_provider_enabled=False)

    summary = CartographyOrchestrator(settings).analyze(repo_root)
    run_dir = Path(settings.resolved_artifact_dir()) / "runs" / summary.run_id

    module_graph_path = run_dir / "module_graph.json"
    survey_summary_path = run_dir / "survey_summary.json"

    assert module_graph_path.exists()
    assert survey_summary_path.exists()

    graph_payload = json.loads(module_graph_path.read_text(encoding="utf-8"))
    summary_payload = json.loads(survey_summary_path.read_text(encoding="utf-8"))

    assert summary_payload["module_count"] >= 4
    assert summary_payload["import_edge_count"] >= 3
    assert graph_payload["graph_metadata"]["module_count"] == summary_payload["module_count"]


def test_surveyor_pipeline_degrades_gracefully_without_git_history(tmp_path: Path) -> None:
    repo_root = _copy_fixture(Path("tests/fixtures/surveyor_repo"), tmp_path / "surveyor_repo")
    settings = AppSettings(repo_root=repo_root, semantic_provider_enabled=False)

    summary = CartographyOrchestrator(settings).analyze(repo_root)
    run_dir = Path(settings.resolved_artifact_dir()) / "runs" / summary.run_id
    survey_summary = json.loads((run_dir / "survey_summary.json").read_text(encoding="utf-8"))

    joined = " ".join(survey_summary["partial_result_flags"] + survey_summary["warnings"])
    assert "git_velocity_unavailable" in joined


@pytest.mark.skipif(shutil.which("git") is None, reason="git is required for velocity integration coverage")
def test_surveyor_pipeline_collects_git_velocity_for_recent_repo(tmp_path: Path) -> None:
    repo_root = _copy_fixture(Path("tests/fixtures/surveyor_repo"), tmp_path / "git_surveyor_repo")
    subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_root, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_root, check=True, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=repo_root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo_root, check=True, capture_output=True)
    (repo_root / "pkg" / "main.py").write_text(
        "from pkg import helper\nfrom pkg import cycle_a\n\ndef public_api():\n    return helper.run()\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "."], cwd=repo_root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "update"], cwd=repo_root, check=True, capture_output=True)

    settings = AppSettings(repo_root=repo_root, semantic_provider_enabled=False)
    summary = CartographyOrchestrator(settings).analyze(repo_root)
    run_dir = Path(settings.resolved_artifact_dir()) / "runs" / summary.run_id
    survey_summary = json.loads((run_dir / "survey_summary.json").read_text(encoding="utf-8"))

    assert survey_summary["high_velocity_file_count"] >= 1
    assert any(item["relative_path"] == "pkg/main.py" for item in survey_summary["high_velocity_files"])
