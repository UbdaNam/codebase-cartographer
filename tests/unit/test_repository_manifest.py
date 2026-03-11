from pathlib import Path

from src.analyzers.repository_manifest import build_repository_manifest
from src.config import AppSettings
from src.models.manifest import SkipReason, SupportStatus


def test_manifest_is_deterministic(tmp_path: Path) -> None:
    (tmp_path / "b.py").write_text("print('b')", encoding="utf-8")
    (tmp_path / "a.py").write_text("print('a')", encoding="utf-8")
    settings = AppSettings(repo_root=tmp_path)

    manifest_one = build_repository_manifest(settings)
    manifest_two = build_repository_manifest(settings)

    assert [record.relative_path for record in manifest_one.records] == [
        "a.py",
        "b.py",
    ]
    assert manifest_one.model_dump() == manifest_two.model_dump()


def test_manifest_marks_secret_and_unsupported_files(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("SECRET=1", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("notes", encoding="utf-8")
    settings = AppSettings(repo_root=tmp_path)

    manifest = build_repository_manifest(settings)
    by_path = {record.relative_path: record for record in manifest.records}

    assert by_path[".env"].support_status == SupportStatus.SKIPPED
    assert by_path[".env"].skip_reason == SkipReason.SECRET_SENSITIVE
    assert by_path["notes.txt"].support_status == SupportStatus.UNSUPPORTED


def test_manifest_respects_total_byte_budget(tmp_path: Path) -> None:
    (tmp_path / "first.py").write_text("print('a')", encoding="utf-8")
    (tmp_path / "second.py").write_text("print('b')", encoding="utf-8")
    settings = AppSettings(repo_root=tmp_path, max_total_bytes_scanned=11)

    manifest = build_repository_manifest(settings)

    assert any(
        record.skip_reason == SkipReason.TOTAL_BUDGET_EXCEEDED
        for record in manifest.records
    )
