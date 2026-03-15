from pathlib import Path

from src.models.enums import AnalysisMethod, ConfidenceBand
from src.models.semantic import EvidenceReference
from src.models.trace import TraceEvent
from src.utils.trace import TraceWriter, read_trace_events


def test_trace_writer_appends_and_reads_events(tmp_path: Path) -> None:
    path = tmp_path / "cartography_trace.jsonl"
    writer = TraceWriter(path)
    event = TraceEvent(
        run_id="run-001",
        agent="archivist",
        action="generate_codebase_md",
        input_summary={"modules": 3},
        output_summary={"sections": 6},
        evidence_sources=[
            EvidenceReference(
                source_kind="module_graph",
                artifact_path="module_graph.json",
                repository_path="app/main.py",
                line_start=1,
                line_end=4,
                observed_or_inferred="observed",
                analysis_method=AnalysisMethod.STATIC_ANALYSIS,
                confidence=ConfidenceBand.MEDIUM,
            )
        ],
        confidence=ConfidenceBand.MEDIUM,
        method_type="synthesis",
    )

    writer.append(event)
    events = read_trace_events(path)

    assert len(events) == 1
    assert events[0].agent == "archivist"
    assert events[0].evidence_sources[0].repository_path == "app/main.py"
