from pydantic import BaseModel

from src.models.enums import AnalysisMethod, ConfidenceBand, EdgeKind, NodeKind, SkipReason, SupportStatus


class EnumEnvelope(BaseModel):
    node_kind: NodeKind
    edge_kind: EdgeKind
    support_status: SupportStatus
    analysis_method: AnalysisMethod
    skip_reason: SkipReason
    confidence: ConfidenceBand


def test_stage1_enums_serialize_to_stable_strings() -> None:
    envelope = EnumEnvelope(
        node_kind=NodeKind.MODULE,
        edge_kind=EdgeKind.IMPORTS,
        support_status=SupportStatus.PARTIAL,
        analysis_method=AnalysisMethod.STATIC_ANALYSIS,
        skip_reason=SkipReason.SECRET_SENSITIVE,
        confidence=ConfidenceBand.MEDIUM,
    )

    payload = envelope.model_dump(mode="json")

    assert payload == {
        "node_kind": "module",
        "edge_kind": "imports",
        "support_status": "partial",
        "analysis_method": "static_analysis",
        "skip_reason": "secret_sensitive",
        "confidence": "medium",
    }
