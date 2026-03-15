from pathlib import Path
import subprocess

from src.config import AppSettings
from src.orchestrator import CartographyOrchestrator


def _git(repo_root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo_root, check=True, capture_output=True, text=True)


def test_incremental_pipeline_reuses_artifacts_when_commit_is_unchanged(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".gitignore").write_text(".cartography/\n", encoding="utf-8")
    (repo / "app.py").write_text(
        "import pandas as pd\n\n\ndef run():\n    return pd.read_csv('orders.csv')\n",
        encoding="utf-8",
    )
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "init")

    settings = AppSettings(repo_root=repo, semantic_provider_enabled=False)
    first = CartographyOrchestrator(settings).analyze(repo)
    second = CartographyOrchestrator(settings).analyze(repo)

    assert first.codebase_md_path
    assert second.codebase_md_path
    assert second.archivist_stats["reused_artifact_count"] > 0
