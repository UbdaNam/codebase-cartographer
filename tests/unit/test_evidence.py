import pytest

from src.models.enums import AnalysisMethod, ConfidenceBand
from src.models.evidence import Citation, EvidenceRecord


def test_evidence_supports_optional_line_numbers() -> None:
    evidence = EvidenceRecord(
        source_path="src/cli.py",
        analysis_method=AnalysisMethod.STATIC_ANALYSIS,
        confidence=ConfidenceBand.HIGH,
    )

    assert evidence.line_start is None
    assert evidence.model_dump(mode="json")["source_path"] == "src/cli.py"


def test_citation_validates_line_order() -> None:
    with pytest.raises(ValueError):
        Citation(
            source_path="src/cli.py",
            line_start=20,
            line_end=10,
            analysis_method=AnalysisMethod.GRAPH_INFERENCE,
        )
