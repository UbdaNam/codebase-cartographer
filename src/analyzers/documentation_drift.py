"""Documentation extraction and drift detection for Semanticist."""

from __future__ import annotations

import re

from src.models.enums import ConfidenceBand
from src.models.semantic import DocumentationDriftRecord, EvidenceReference, SemanticModuleProfile

TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9_/-]+")


def detect_documentation_drift(
    profile: SemanticModuleProfile,
    documentation_refs: list[EvidenceReference],
) -> DocumentationDriftRecord | None:
    if not documentation_refs:
        return None
    observed_text = "\n".join(filter(None, (ref.quoted_text for ref in documentation_refs))).strip()
    if not observed_text:
        return None
    purpose_text = profile.purpose_statement.strip()
    doc_tokens = {token.lower() for token in TOKEN_RE.findall(observed_text)}
    purpose_tokens = {token.lower() for token in TOKEN_RE.findall(purpose_text)}
    overlap = len(doc_tokens & purpose_tokens) / max(1, len(doc_tokens))
    drift_type = _classify_drift(observed_text.lower(), purpose_text.lower(), overlap)
    if drift_type is None:
        return None
    confidence = ConfidenceBand.HIGH if overlap < 0.25 else ConfidenceBand.MEDIUM
    return DocumentationDriftRecord(
        module_id=profile.module_id,
        module_path=profile.relative_path,
        observed_documentation=observed_text[:600],
        inferred_purpose=purpose_text,
        drift_type=drift_type,
        confidence=confidence,
        evidence_references=documentation_refs[:4] + profile.evidence_references[:3],
        is_partial=confidence == ConfidenceBand.MEDIUM and drift_type == "omission",
        warning_codes=["documentation_drift_detected"],
    )


def _classify_drift(observed_text: str, purpose_text: str, overlap: float) -> str | None:
    if overlap >= 0.55:
        return None
    observed_role = _role_token(observed_text)
    purpose_role = _role_token(purpose_text)
    if observed_role and purpose_role and observed_role != purpose_role:
        return "contradiction"
    if any(word in observed_text for word in ("deprecated", "legacy", "old")) and "deprecated" not in purpose_text:
        return "outdated"
    if overlap < 0.2:
        return "omission"
    return "outdated"


def _role_token(text: str) -> str | None:
    for token in ("ingest", "transform", "serve", "monitor", "orchestr", "util", "shared"):
        if token in text:
            return token
    return None
