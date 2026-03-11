import subprocess
from pathlib import Path

from src.graph.survey import extract_git_velocity


def test_extract_git_velocity_parses_name_only_output(monkeypatch, tmp_path: Path) -> None:
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout="pkg/a.py\npkg/b.py\n\npkg/a.py\n",
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    counts, warnings = extract_git_velocity(tmp_path, days=30)

    assert warnings == []
    assert counts == {"pkg/a.py": 2, "pkg/b.py": 1}


def test_extract_git_velocity_returns_warning_when_git_unavailable(monkeypatch, tmp_path: Path) -> None:
    def fake_run(*args, **kwargs):
        raise OSError("git missing")

    monkeypatch.setattr(subprocess, "run", fake_run)

    counts, warnings = extract_git_velocity(tmp_path, days=30)

    assert counts == {}
    assert warnings == ["git_velocity_unavailable:OSError"]
