from pathlib import Path

from src.config import AppSettings
from src.models.manifest import SupportStatus
from src.utils.file_classification import classify_path


def test_supported_classifications_cover_required_languages(tmp_path: Path) -> None:
    settings = AppSettings(repo_root=tmp_path)

    assert classify_path(Path("file.py"), settings)[1] == SupportStatus.SUPPORTED
    assert classify_path(Path("file.sql"), settings)[1] == SupportStatus.SUPPORTED
    assert classify_path(Path("file.yaml"), settings)[1] == SupportStatus.SUPPORTED
    assert classify_path(Path("file.ts"), settings)[1] == SupportStatus.SUPPORTED
    assert classify_path(Path("file.json"), settings)[1] == SupportStatus.SUPPORTED
    assert classify_path(Path("file.ipynb"), settings)[1] == SupportStatus.PARTIAL


def test_unknown_extensions_are_unsupported(tmp_path: Path) -> None:
    settings = AppSettings(repo_root=tmp_path)

    _, support_status, source = classify_path(Path("archive.xyz"), settings)

    assert support_status == SupportStatus.UNSUPPORTED
    assert source == "extension:.xyz"
