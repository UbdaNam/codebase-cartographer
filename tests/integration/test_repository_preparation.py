import subprocess
from pathlib import Path

from src.config import AppSettings
from src.models.repository_input import RepositoryReuseMode
from src.utils.repository_preparation import prepare_repository


def _init_git_repo(path: Path) -> Path:
    subprocess.run(["git", "init", str(path)], check=True, capture_output=True, text=True)
    (path / "app.py").write_text("print('hello')\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(path), "add", "."], check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "-C", str(path), "-c", "user.email=test@example.com", "-c", "user.name=Test User", "commit", "-m", "init"],
        check=True,
        capture_output=True,
        text=True,
    )
    return path


def test_prepare_repository_returns_direct_local_repo(tmp_path: Path) -> None:
    local_repo = tmp_path / "local"
    local_repo.mkdir()
    settings = AppSettings(repo_root=tmp_path)

    prepared = prepare_repository(local_repo, settings)

    assert prepared.reuse_mode == RepositoryReuseMode.DIRECT
    assert prepared.local_repo_path.replace("\\", "/") == str(local_repo.resolve()).replace("\\", "/")


def test_prepare_repository_clones_and_reuses_file_url_repo(tmp_path: Path) -> None:
    origin_repo = _init_git_repo(tmp_path / "origin")
    settings = AppSettings(repo_root=tmp_path)
    repo_url = origin_repo.resolve().as_uri()

    first = prepare_repository(repo_url, settings)
    second = prepare_repository(repo_url, settings)

    assert first.reuse_mode == RepositoryReuseMode.FRESH_CLONE
    assert second.reuse_mode == RepositoryReuseMode.REUSED_CLONE
    assert first.local_repo_path == second.local_repo_path
    assert Path(first.local_repo_path).exists()
