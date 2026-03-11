from pathlib import Path

import pytest

from src.config import AppSettings


def test_settings_resolve_repo_root(tmp_path: Path) -> None:
    settings = AppSettings(repo_root=tmp_path, artifact_dir=".cartography")

    assert settings.repo_root == tmp_path.resolve()
    assert settings.resolved_artifact_dir() == tmp_path / ".cartography"
    assert ".py" in settings.supported_extensions


def test_settings_validate_positive_numbers(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        AppSettings(repo_root=tmp_path, max_file_size_bytes=0)
