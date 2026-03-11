import subprocess
from pathlib import Path

from typer.testing import CliRunner

from src.cli import app

runner = CliRunner()


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


def test_cli_analyze_accepts_local_path(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("print('ok')\n", encoding="utf-8")

    result = runner.invoke(app, ["analyze", "--repo", str(tmp_path)])

    assert result.exit_code == 0
    assert '"prepared_repo_path"' in result.stdout


def test_cli_analyze_accepts_git_url(tmp_path: Path) -> None:
    repo = _init_git_repo(tmp_path / "origin")

    result = runner.invoke(app, ["analyze", "--repo", repo.resolve().as_uri()])

    assert result.exit_code == 0
    assert '"prepared_repo_path"' in result.stdout
