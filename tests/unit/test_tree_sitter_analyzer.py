from pathlib import Path

from src.analyzers.repository_manifest import build_repository_manifest
from src.analyzers.tree_sitter_analyzer import TreeSitterAnalyzer
from src.config import AppSettings
from src.models.repository_input import PreparedRepository, PreparationStatus, RepositoryInput, RepositoryInputKind, RepositoryReuseMode


def _prepared_repo(path: Path) -> PreparedRepository:
    return PreparedRepository(
        repository_input=RepositoryInput(raw_input=str(path), input_kind=RepositoryInputKind.LOCAL_PATH),
        local_repo_path=str(path),
        preparation_status=PreparationStatus.READY,
        reuse_mode=RepositoryReuseMode.DIRECT,
    )


def test_tree_sitter_analyzer_extracts_records_from_mixed_language_fixture() -> None:
    repo_root = Path("tests/fixtures/structural_polyglot_repo").resolve()
    settings = AppSettings(repo_root=repo_root)
    manifest = build_repository_manifest(settings)

    structural_index, ast_index = TreeSitterAnalyzer().analyze_manifest(
        _prepared_repo(repo_root),
        manifest,
        run_id="run-001",
        artifact_dir=".cartography",
    )

    by_path = {result.file_path: result for result in structural_index.file_results}
    assert any(record.symbol_kind.value == "function" for record in by_path["src/app.py"].records)
    assert any(record.symbol_kind.value == "class" for record in by_path["frontend/app.js"].records)
    assert any(record.symbol_kind.value == "statement" for record in by_path["sql/report.sql"].records)
    assert any(record.symbol_kind.value == "mapping" for record in by_path["configs/pipeline.yaml"].records)
    assert by_path["notebooks/analysis.ipynb"].is_partial is True
    assert ast_index.entries


def test_tree_sitter_analyzer_marks_malformed_files_as_partial() -> None:
    repo_root = Path("tests/fixtures/structural_malformed_repo").resolve()
    settings = AppSettings(repo_root=repo_root)
    manifest = build_repository_manifest(settings)

    structural_index, _ = TreeSitterAnalyzer().analyze_manifest(
        _prepared_repo(repo_root),
        manifest,
        run_id="run-002",
        artifact_dir=".cartography",
    )

    by_path = {result.file_path: result for result in structural_index.file_results}
    assert by_path["broken.py"].is_partial is True
    assert "tree_sitter_parse_has_error" in by_path["broken.py"].warnings
