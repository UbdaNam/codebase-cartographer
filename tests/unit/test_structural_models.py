from src.models.artifacts import SerializationMetadata
from src.models.enums import AnalysisMethod, SupportStatus
from src.models.repository_input import (
    PreparedRepository,
    PreparationStatus,
    RepositoryInput,
    RepositoryInputKind,
    RepositoryReuseMode,
)
from src.models.structural import (
    AstIndexEntry,
    AstIndexPayload,
    ParseStatus,
    StructuralFileResult,
    StructuralIndexPayload,
    StructuralRecord,
    StructuralSummary,
    StructuralSymbolKind,
)


def test_structural_record_ids_are_deterministic() -> None:
    one = StructuralRecord(
        file_path="src/app.py",
        language="python",
        symbol_kind=StructuralSymbolKind.FUNCTION,
        symbol_name="main",
    )
    two = StructuralRecord(
        file_path="src/app.py",
        language="python",
        symbol_kind=StructuralSymbolKind.FUNCTION,
        symbol_name="main",
    )

    assert one.record_id == two.record_id


def test_structural_payload_serializes_in_file_order() -> None:
    prepared = PreparedRepository(
        repository_input=RepositoryInput(raw_input="C:/repo", input_kind=RepositoryInputKind.LOCAL_PATH),
        local_repo_path="C:/repo",
        preparation_status=PreparationStatus.READY,
        reuse_mode=RepositoryReuseMode.DIRECT,
    )
    payload = StructuralIndexPayload(
        metadata=SerializationMetadata(run_id="run-001", artifact_dir=".cartography"),
        prepared_repository=prepared,
        file_results=[
            StructuralFileResult(
                manifest_file_id="b",
                file_path="src/z.py",
                language="python",
                support_status=SupportStatus.SUPPORTED,
                parse_status=ParseStatus.PARSED,
            ),
            StructuralFileResult(
                manifest_file_id="a",
                file_path="src/a.py",
                language="python",
                support_status=SupportStatus.SUPPORTED,
                parse_status=ParseStatus.PARSED,
            ),
        ],
        summary=StructuralSummary(total_files=2),
    )

    dumped = payload.model_dump(mode="json")
    assert [entry["file_path"] for entry in dumped["file_results"]] == ["src/a.py", "src/z.py"]


def test_ast_index_payload_serializes_in_file_order() -> None:
    prepared = PreparedRepository(
        repository_input=RepositoryInput(raw_input="C:/repo", input_kind=RepositoryInputKind.LOCAL_PATH),
        local_repo_path="C:/repo",
        preparation_status=PreparationStatus.READY,
        reuse_mode=RepositoryReuseMode.DIRECT,
    )
    payload = AstIndexPayload(
        metadata=SerializationMetadata(run_id="run-001", artifact_dir=".cartography"),
        prepared_repository=prepared,
        entries=[
            AstIndexEntry(manifest_file_id="b", file_path="src/z.py", language="python"),
            AstIndexEntry(manifest_file_id="a", file_path="src/a.py", language="python"),
        ],
    )

    dumped = payload.model_dump(mode="json")
    assert [entry["file_path"] for entry in dumped["entries"]] == ["src/a.py", "src/z.py"]
