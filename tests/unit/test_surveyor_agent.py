from pathlib import Path

from src.agents.surveyor import SurveyorAgent
from src.config import AppSettings
from src.models.artifacts import SerializationMetadata
from src.models.enums import AnalysisMethod, SupportStatus
from src.models.evidence import EvidenceRecord
from src.models.manifest import ManifestSummary, RepositoryManifest
from src.models.repository_input import (
    PreparedRepository,
    PreparationStatus,
    RepositoryInput,
    RepositoryInputKind,
    RepositoryReuseMode,
)
from src.models.structural import (
    ParseStatus,
    StructuralFileResult,
    StructuralIndexPayload,
    StructuralRecord,
    StructuralSummary,
    StructuralSymbolKind,
)


def _prepared_repository(repo_root: Path) -> PreparedRepository:
    return PreparedRepository(
        repository_input=RepositoryInput(raw_input=str(repo_root), input_kind=RepositoryInputKind.LOCAL_PATH),
        local_repo_path=str(repo_root),
        preparation_status=PreparationStatus.READY,
        reuse_mode=RepositoryReuseMode.DIRECT,
    )


def _structural_payload(repo_root: Path, file_results: list[StructuralFileResult]) -> StructuralIndexPayload:
    return StructuralIndexPayload(
        metadata=SerializationMetadata(run_id="run-001", artifact_dir=".cartography"),
        prepared_repository=_prepared_repository(repo_root),
        file_results=file_results,
        summary=StructuralSummary(
            total_files=len(file_results),
            parsed_files=len(file_results),
            record_count=sum(len(item.records) for item in file_results),
        ),
    )


def test_surveyor_maps_structural_results_to_module_nodes(tmp_path: Path) -> None:
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "main.py").write_text(
        "from pkg import helper\n\ndef public_api():\n    return helper.run()\n",
        encoding="utf-8",
    )
    (tmp_path / "pkg" / "helper.py").write_text("def run():\n    return 1\n", encoding="utf-8")

    file_results = [
        StructuralFileResult(
            manifest_file_id="pkg/main.py",
            file_path="pkg/main.py",
            language="python",
            support_status=SupportStatus.SUPPORTED,
            parse_status=ParseStatus.PARSED,
            records=[
                StructuralRecord(
                    file_path="pkg/main.py",
                    language="python",
                    symbol_kind=StructuralSymbolKind.IMPORT,
                    analysis_method=AnalysisMethod.STATIC_ANALYSIS,
                    evidence=[EvidenceRecord(source_path="pkg/main.py", line_start=1, line_end=1, analysis_method=AnalysisMethod.STATIC_ANALYSIS)],
                ),
                StructuralRecord(
                    file_path="pkg/main.py",
                    language="python",
                    symbol_kind=StructuralSymbolKind.FUNCTION,
                    symbol_name="public_api",
                    analysis_method=AnalysisMethod.STATIC_ANALYSIS,
                    evidence=[EvidenceRecord(source_path="pkg/main.py", line_start=3, line_end=4, analysis_method=AnalysisMethod.STATIC_ANALYSIS)],
                ),
            ],
        ),
        StructuralFileResult(
            manifest_file_id="pkg/helper.py",
            file_path="pkg/helper.py",
            language="python",
            support_status=SupportStatus.SUPPORTED,
            parse_status=ParseStatus.PARSED,
            records=[
                StructuralRecord(
                    file_path="pkg/helper.py",
                    language="python",
                    symbol_kind=StructuralSymbolKind.FUNCTION,
                    symbol_name="run",
                    analysis_method=AnalysisMethod.STATIC_ANALYSIS,
                    evidence=[EvidenceRecord(source_path="pkg/helper.py", line_start=1, line_end=2, analysis_method=AnalysisMethod.STATIC_ANALYSIS)],
                )
            ],
        ),
    ]

    graph_payload, summary = SurveyorAgent(AppSettings(repo_root=tmp_path)).analyze(
        _prepared_repository(tmp_path),
        RepositoryManifest(summary=ManifestSummary()),
        _structural_payload(tmp_path, file_results),
        run_id="run-001",
        artifact_dir=".cartography",
    )

    assert len(graph_payload.nodes) == 2
    assert len(graph_payload.edges) == 1
    assert summary.module_count == 2
    assert summary.import_edge_count == 1


def test_surveyor_marks_dead_code_candidates_conservatively(tmp_path: Path) -> None:
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "unused.py").write_text("def _helper():\n    return 1\n", encoding="utf-8")

    file_results = [
        StructuralFileResult(
            manifest_file_id="pkg/unused.py",
            file_path="pkg/unused.py",
            language="python",
            support_status=SupportStatus.SUPPORTED,
            parse_status=ParseStatus.PARSED,
            records=[
                StructuralRecord(
                    file_path="pkg/unused.py",
                    language="python",
                    symbol_kind=StructuralSymbolKind.FUNCTION,
                    symbol_name="_helper",
                    analysis_method=AnalysisMethod.STATIC_ANALYSIS,
                    evidence=[EvidenceRecord(source_path="pkg/unused.py", line_start=1, line_end=2, analysis_method=AnalysisMethod.STATIC_ANALYSIS)],
                )
            ],
        )
    ]

    _, summary = SurveyorAgent(AppSettings(repo_root=tmp_path)).analyze(
        _prepared_repository(tmp_path),
        RepositoryManifest(summary=ManifestSummary()),
        _structural_payload(tmp_path, file_results),
        run_id="run-001",
        artifact_dir=".cartography",
    )

    assert summary.dead_code_candidate_count == 1
    assert summary.dead_code_candidates[0].relative_path == "pkg/unused.py"
