from pathlib import Path
import subprocess

from src.models.archivist import IncrementalBaseline
from src.models.run_metadata import RunStatus, RunSummary
from src.utils.incremental import plan_incremental_refresh, write_incremental_baseline


def _git(repo_root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo_root, check=True, capture_output=True, text=True)


def test_incremental_plan_reuses_all_when_commit_is_unchanged(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".gitignore").write_text(".cartography/\n", encoding="utf-8")
    (repo / "app.py").write_text("print('hello')\n", encoding="utf-8")
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "init")

    runs_dir = repo / ".cartography" / "runs"
    run_dir = runs_dir / "run-001"
    run_dir.mkdir(parents=True)
    summary = RunSummary(run_id="run-001", status=RunStatus.COMPLETED, message="done")
    (run_dir / "run_summary.json").write_text(summary.model_dump_json(indent=2), encoding="utf-8")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True).stdout.strip()
    write_incremental_baseline(
        run_dir / "incremental_baseline.json",
        IncrementalBaseline(run_id="run-001", commit_hash=head, source_files=["app.py"]),
    )

    plan = plan_incremental_refresh(repo, runs_dir)

    assert plan.reuse_inventory is True
    assert plan.reuse_structural is True
    assert plan.reuse_surveyor is True
    assert plan.reuse_hydrologist is True
    assert plan.reuse_semanticist is True
    assert plan.reuse_archivist is True


def test_incremental_plan_keeps_upstream_reuse_for_docs_only_change(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".gitignore").write_text(".cartography/\n", encoding="utf-8")
    (repo / "README.md").write_text("hello\n", encoding="utf-8")
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "init")

    runs_dir = repo / ".cartography" / "runs"
    run_dir = runs_dir / "run-001"
    run_dir.mkdir(parents=True)
    summary = RunSummary(run_id="run-001", status=RunStatus.COMPLETED, message="done")
    (run_dir / "run_summary.json").write_text(summary.model_dump_json(indent=2), encoding="utf-8")
    previous_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True).stdout.strip()
    write_incremental_baseline(
        run_dir / "incremental_baseline.json",
        IncrementalBaseline(run_id="run-001", commit_hash=previous_commit, source_files=["README.md"]),
    )

    (repo / "README.md").write_text("hello world\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "docs")

    plan = plan_incremental_refresh(repo, runs_dir)

    assert plan.reuse_inventory is True
    assert plan.reuse_structural is True
    assert plan.reuse_surveyor is True
    assert plan.reuse_hydrologist is True
    assert "incremental_docs_only_refresh" in plan.warning_codes
