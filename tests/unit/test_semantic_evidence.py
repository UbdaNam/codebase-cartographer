from pathlib import Path

from src.analyzers.semantic_evidence import build_evidence_bundle
from src.config import AppSettings
from src.models.enums import AnalysisMethod, ConfidenceBand, SupportStatus
from src.models.evidence import EvidenceRecord
from src.models.graph import GraphPayload, ModuleNode
from src.models.repository_input import PreparedRepository, RepositoryInput, RepositoryInputKind, RepositoryReuseMode
from src.models.structural import ParseStatus, StructuralFileResult, StructuralRecord, StructuralSymbolKind


def test_build_evidence_bundle_collects_public_api_and_excerpts(tmp_path: Path) -> None:
    module_path = tmp_path / "app" / "ingestion.py"
    module_path.parent.mkdir(parents=True)
    module_path.write_text('"""Load order data."""\n\ndef load_orders():\n    return 1\n', encoding="utf-8")
    module = ModuleNode(
        relative_path="app/ingestion.py",
        module_name="app.ingestion",
        language_or_dialect="python",
        support_status=SupportStatus.SUPPORTED,
        confidence=ConfidenceBand.HIGH,
        evidence=[],
    )
    file_result = StructuralFileResult(
        manifest_file_id="file-1",
        file_path="app/ingestion.py",
        language="python",
        support_status=SupportStatus.SUPPORTED,
        parse_status=ParseStatus.PARSED,
        records=[
            StructuralRecord(
                file_path="app/ingestion.py",
                language="python",
                symbol_kind=StructuralSymbolKind.FUNCTION,
                symbol_name="load_orders",
                evidence=[
                    EvidenceRecord(
                        source_path="app/ingestion.py",
                        line_start=3,
                        line_end=4,
                        language="python",
                        analysis_method=AnalysisMethod.STATIC_ANALYSIS,
                    )
                ],
            )
        ],
    )
    bundle = build_evidence_bundle(module, file_result, GraphPayload(run_id="run-1"), tmp_path, AppSettings(repo_root=tmp_path))

    assert bundle.module_id == module.node_id
    assert "load_orders" in bundle.public_api_signals
    assert bundle.code_excerpt_refs
    assert bundle.documentation_refs
