from src.index.semantic_index import search_semantic_index
from src.models.archivist import SemanticIndexEntry, SemanticIndexSnapshot
from src.models.enums import AnalysisMethod, ConfidenceBand
from src.models.semantic import EvidenceReference


def test_search_semantic_index_penalizes_container_modules() -> None:
    snapshot = SemanticIndexSnapshot(
        run_id="run-001",
        entries=[
            SemanticIndexEntry(
                module_id="node:init",
                module_path="pkg/__init__.py",
                purpose_statement="Initialize the package and expose shared imports.",
                retrieval_tokens=["pkg", "__init__", "initialize", "shared", "imports", "order", "ingestion"],
            ),
            SemanticIndexEntry(
                module_id="node:ingestion",
                module_path="app/ingestion.py",
                purpose_statement="Load raw order data for downstream processing.",
                retrieval_tokens=["app", "ingestion", "load", "raw", "order", "data", "processing"],
                evidence_references=[
                    EvidenceReference(
                        source_kind="source_excerpt",
                        repository_path="app/ingestion.py",
                        line_start=1,
                        line_end=4,
                        observed_or_inferred="observed",
                        analysis_method=AnalysisMethod.STATIC_ANALYSIS,
                        confidence=ConfidenceBand.MEDIUM,
                    )
                ],
            ),
        ],
    )

    results = search_semantic_index(snapshot, "order ingestion", max_results=2)

    assert results[0].module_path == "app/ingestion.py"
