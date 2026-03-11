from pathlib import Path

from src.config import AppSettings
from src.models.manifest import ScanAction, SkipReason
from src.utils.ignore_policy import should_skip_path


def test_secret_sensitive_files_are_skipped(tmp_path: Path) -> None:
    secret_file = tmp_path / ".env"
    secret_file.write_text("SECRET=1", encoding="utf-8")
    settings = AppSettings(repo_root=tmp_path)

    decision = should_skip_path(secret_file, tmp_path, settings)

    assert decision.action == ScanAction.SKIP
    assert decision.reason_code == SkipReason.SECRET_SENSITIVE


def test_oversized_files_are_skipped(tmp_path: Path) -> None:
    large_file = tmp_path / "large.py"
    large_file.write_text("x" * 20, encoding="utf-8")
    settings = AppSettings(repo_root=tmp_path, max_file_size_bytes=10)

    decision = should_skip_path(large_file, tmp_path, settings)

    assert decision.reason_code == SkipReason.OVERSIZED_FILE


def test_ignored_directories_are_skipped(tmp_path: Path) -> None:
    node_module = tmp_path / "node_modules" / "lib.js"
    node_module.parent.mkdir(parents=True)
    node_module.write_text("module.exports = {}", encoding="utf-8")
    settings = AppSettings(repo_root=tmp_path)

    decision = should_skip_path(node_module, tmp_path, settings)

    assert decision.reason_code == SkipReason.IGNORED_DIRECTORY


def test_analysis_root_escape_is_rejected(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside.py"
    outside.write_text("print('x')", encoding="utf-8")
    settings = AppSettings(repo_root=tmp_path)

    decision = should_skip_path(outside, tmp_path, settings)

    assert decision.reason_code == SkipReason.ANALYSIS_ROOT_ESCAPE


def test_lockfiles_and_minified_assets_are_skipped(tmp_path: Path) -> None:
    lockfile = tmp_path / "uv.lock"
    lockfile.write_text("version = 1", encoding="utf-8")
    minified = tmp_path / "bundle.min.js"
    minified.write_text("var x=1;", encoding="utf-8")
    settings = AppSettings(repo_root=tmp_path)

    lockfile_decision = should_skip_path(lockfile, tmp_path, settings)
    minified_decision = should_skip_path(minified, tmp_path, settings)

    assert lockfile_decision.reason_code == SkipReason.IGNORED_FILENAME
    assert minified_decision.reason_code == SkipReason.MINIFIED_ASSET


def test_binary_like_assets_are_skipped(tmp_path: Path) -> None:
    asset = tmp_path / "assets" / "logo.png"
    asset.parent.mkdir(parents=True)
    asset.write_text("fake-binary", encoding="utf-8")
    settings = AppSettings(repo_root=tmp_path)

    decision = should_skip_path(asset, tmp_path, settings)

    assert decision.reason_code == SkipReason.BINARY_OR_ARCHIVE
