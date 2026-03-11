from pathlib import Path

from src.config import AppSettings
from src.models.manifest import SupportStatus
from src.utils.file_classification import classify_path


def test_supported_classifications_cover_required_languages(tmp_path: Path) -> None:
    settings = AppSettings(repo_root=tmp_path)

    assert classify_path(Path("file.py"), settings)[1] == SupportStatus.SUPPORTED
    assert classify_path(Path("file.sql"), settings)[1] == SupportStatus.SUPPORTED
    assert classify_path(Path("file.yaml"), settings)[1] == SupportStatus.SUPPORTED
    assert classify_path(Path("file.js"), settings)[1] == SupportStatus.SUPPORTED
    assert classify_path(Path("file.mjs"), settings)[1] == SupportStatus.SUPPORTED
    assert classify_path(Path("file.ts"), settings)[1] == SupportStatus.SUPPORTED
    assert classify_path(Path("file.tsx"), settings)[1] == SupportStatus.PARTIAL
    assert classify_path(Path("file.json"), settings)[1] == SupportStatus.SUPPORTED
    assert classify_path(Path("file.ipynb"), settings)[1] == SupportStatus.PARTIAL
    assert classify_path(Path("file.sh"), settings)[1] == SupportStatus.PARTIAL


def test_classification_returns_parse_eligibility_and_notes(tmp_path: Path) -> None:
    settings = AppSettings(repo_root=tmp_path)

    language, support_status, source, is_parse_eligible, notes = classify_path(
        Path("config/settings.json"),
        settings,
    )

    assert language == "json"
    assert support_status == SupportStatus.SUPPORTED
    assert source == "extension:.json"
    assert is_parse_eligible is True
    assert "config directory JSON" in notes


def test_unknown_extensions_are_unsupported(tmp_path: Path) -> None:
    settings = AppSettings(repo_root=tmp_path)

    language, support_status, source, is_parse_eligible, notes = classify_path(Path("archive.xyz"), settings)

    assert language == "unknown"
    assert support_status == SupportStatus.UNSUPPORTED
    assert source == "extension:.xyz"
    assert is_parse_eligible is False
    assert notes == ["unsupported extension"]


def test_package_json_and_lockfiles_have_special_routing(tmp_path: Path) -> None:
    settings = AppSettings(repo_root=tmp_path)

    package_payload = classify_path(Path("package.json"), settings)
    lockfile_payload = classify_path(Path("uv.lock"), settings)

    assert package_payload[0] == "json"
    assert package_payload[1] == SupportStatus.PARTIAL
    assert package_payload[3] is True
    assert lockfile_payload[0] == "lockfile"
    assert lockfile_payload[1] == SupportStatus.SKIPPED
    assert lockfile_payload[3] is False
