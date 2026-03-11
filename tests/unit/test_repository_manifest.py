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
    assert [record.file_id for record in manifest_one.records] == [record.file_id for record in manifest_two.records]


def test_manifest_marks_secret_and_unsupported_files(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("SECRET=1", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("notes", encoding="utf-8")
    settings = AppSettings(repo_root=tmp_path)

    manifest = build_repository_manifest(settings)
    by_path = {record.relative_path: record for record in manifest.records}

    assert by_path[".env"].support_status == SupportStatus.SKIPPED
    assert by_path[".env"].skip_reason == SkipReason.SECRET_SENSITIVE
    assert by_path[".env"].is_parse_eligible is False
    assert by_path["notes.txt"].support_status == SupportStatus.UNSUPPORTED
    assert by_path["notes.txt"].is_parse_eligible is False


def test_manifest_tracks_parse_eligibility_and_extension_fields(tmp_path: Path) -> None:
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "settings.json").write_text('{"debug": false}', encoding="utf-8")
    (tmp_path / "script.sh").write_text("echo hi", encoding="utf-8")
    settings = AppSettings(repo_root=tmp_path)

    manifest = build_repository_manifest(settings)
    by_path = {record.relative_path: record for record in manifest.records}

    assert by_path["config/settings.json"].extension == ".json"
    assert by_path["config/settings.json"].is_parse_eligible is True
    assert "config directory JSON" in by_path["config/settings.json"].notes
    assert by_path["script.sh"].support_status == SupportStatus.PARTIAL
    assert manifest.summary.parse_eligible_count == 2


def test_manifest_respects_total_byte_budget(tmp_path: Path) -> None:
    (tmp_path / "first.py").write_text("print('a')", encoding="utf-8")
    (tmp_path / "second.py").write_text("print('b')", encoding="utf-8")
    settings = AppSettings(repo_root=tmp_path, max_total_bytes_scanned=11)

    manifest = build_repository_manifest(settings)

    assert any(
        record.skip_reason == SkipReason.TOTAL_BUDGET_EXCEEDED
        for record in manifest.records
    )


def test_manifest_classifies_polyglot_fixture_repo() -> None:
    fixture_root = Path("tests/fixtures/inventory_polyglot_repo").resolve()
    settings = AppSettings(repo_root=fixture_root)

    manifest = build_repository_manifest(settings)
    by_path = {record.relative_path: record for record in manifest.records}

    assert by_path["src/app.py"].support_status == SupportStatus.SUPPORTED
    assert by_path["sql/query.sql"].language == "sql"
    assert by_path["configs/pipeline.yaml"].language == "yaml"
    assert by_path["configs/settings.json"].notes == ["config directory JSON"]
    assert by_path["frontend/legacy.js"].support_status == SupportStatus.SUPPORTED
    assert by_path["frontend/app.tsx"].support_status == SupportStatus.PARTIAL
    assert by_path["scripts/bootstrap.sh"].support_status == SupportStatus.PARTIAL
    assert by_path["notebooks/explore.ipynb"].support_status == SupportStatus.PARTIAL
    assert by_path["assets/logo.png"].skip_reason == SkipReason.BINARY_OR_ARCHIVE
    assert by_path["locks/uv.lock"].skip_reason == SkipReason.IGNORED_FILENAME
