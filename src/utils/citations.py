"""Citation and evidence helpers for final-stage artifacts."""

from __future__ import annotations

from collections.abc import Iterable

from src.models.enums import AnalysisMethod, ConfidenceBand
from src.models.evidence import EvidenceRecord
from src.models.navigator import NavigatorCitation, NavigatorTrustLabel
from src.models.semantic import EvidenceReference


def evidence_record_to_reference(
    record: EvidenceRecord,
    *,
    source_kind: str = "source_excerpt",
    artifact_path: str | None = None,
    observed_or_inferred: str = "observed",
) -> EvidenceReference:
    """Convert a source evidence record into a semantic evidence reference."""

    return EvidenceReference(
        source_kind=source_kind,
        artifact_path=artifact_path,
        repository_path=record.source_path,
        line_start=record.line_start,
        line_end=record.line_end,
        quoted_text=record.excerpt,
        observed_or_inferred=observed_or_inferred,  # type: ignore[arg-type]
        analysis_method=record.analysis_method,
        confidence=record.confidence,
    )


def reference_to_navigator_citation(
    reference: EvidenceReference,
    *,
    artifact_reference: str | None = None,
) -> NavigatorCitation:
    """Convert a semantic evidence reference into a Navigator citation."""

    trust_label: NavigatorTrustLabel
    if reference.observed_or_inferred == "observed":
        trust_label = "static_analysis"
    elif reference.observed_or_inferred == "graph_inference":
        trust_label = "graph_inference"
    elif reference.observed_or_inferred == "llm_inference":
        trust_label = "llm_inference"
    else:
        trust_label = "artifact_reuse"
    return NavigatorCitation(
        source_file=reference.repository_path,
        line_start=reference.line_start,
        line_end=reference.line_end,
        analysis_method=reference.analysis_method,
        trust_label=trust_label,
        artifact_reference=artifact_reference or reference.artifact_path,
    )


def format_line_range(line_start: int | None, line_end: int | None) -> str:
    """Render a compact line-range label."""

    if line_start is None:
        return ""
    if line_end is None or line_end == line_start:
        return f":L{line_start}"
    return f":L{line_start}-L{line_end}"


def format_evidence_reference(reference: EvidenceReference) -> str:
    """Render a short markdown-friendly citation label."""

    path = reference.repository_path
    line_range = format_line_range(reference.line_start, reference.line_end)
    return f"`{path}{line_range}` ({reference.analysis_method.value}, {reference.observed_or_inferred})"


def dedupe_references(references: Iterable[EvidenceReference], *, limit: int | None = None) -> list[EvidenceReference]:
    """Deduplicate evidence references while preserving deterministic order."""

    seen: set[str] = set()
    result: list[EvidenceReference] = []
    for reference in sorted(references, key=lambda item: (item.repository_path, item.line_start or 0, item.line_end or 0, item.reference_id or "")):
        key = reference.reference_id or f"{reference.repository_path}:{reference.line_start}:{reference.line_end}:{reference.analysis_method.value}"
        if key in seen:
            continue
        seen.add(key)
        result.append(reference)
        if limit is not None and len(result) >= limit:
            break
    return result


def derive_confidence(references: Iterable[EvidenceReference]) -> ConfidenceBand:
    """Derive a conservative confidence from attached evidence."""

    values = {reference.confidence for reference in references}
    if not values:
        return ConfidenceBand.UNKNOWN
    if ConfidenceBand.LOW in values:
        return ConfidenceBand.LOW
    if ConfidenceBand.MEDIUM in values:
        return ConfidenceBand.MEDIUM
    if ConfidenceBand.HIGH in values:
        return ConfidenceBand.HIGH
    return ConfidenceBand.UNKNOWN


def trust_label_for_method(method: AnalysisMethod, *, inferred: bool = False) -> NavigatorTrustLabel:
    """Map analysis methods to the required trust labels."""

    if inferred or method == AnalysisMethod.LLM_INFERENCE:
        return "llm_inference"
    if method == AnalysisMethod.GRAPH_INFERENCE:
        return "graph_inference"
    if method == AnalysisMethod.HEURISTIC:
        return "artifact_reuse"
    return "static_analysis"
