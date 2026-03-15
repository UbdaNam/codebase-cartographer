from pathlib import Path

import pytest

from src.config import AppSettings


def test_settings_resolve_repo_root(tmp_path: Path) -> None:
    settings = AppSettings(repo_root=tmp_path, artifact_dir=".cartography")

    assert settings.repo_root == tmp_path.resolve()
    assert settings.resolved_artifact_dir() == tmp_path / ".cartography"
    assert ".py" in settings.supported_extensions
    assert settings.semantic_max_total_completion_tokens > settings.semantic_max_completion_tokens


def test_settings_validate_positive_numbers(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        AppSettings(repo_root=tmp_path, max_file_size_bytes=0)


def test_settings_load_openrouter_api_key_from_dotenv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("CARTOGRAPHY_OPENROUTER_API_KEY", raising=False)
    (tmp_path / ".env").write_text("CARTOGRAPHY_OPENROUTER_API_KEY=test-key\n", encoding="utf-8")

    settings = AppSettings(repo_root=tmp_path)

    assert settings.openrouter_api_key == "test-key"
