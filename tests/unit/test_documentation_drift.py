from src.analyzers.documentation_drift import detect_documentation_drift
from src.models.enums import AnalysisMethod, ConfidenceBand
from src.models.semantic import EvidenceReference, PurposeEvidenceBundle, SemanticModuleProfile


def test_detect_documentation_drift_flags_contradiction() -> None:
    profile = SemanticModuleProfile(
        module_id="module-1",
        relative_path="app/ingestion.py",
        language="python",
        purpose_statement="This module transforms raw orders into warehouse metrics. It exists to concentrate processing before downstream consumption.",
        purpose_confidence=ConfidenceBand.MEDIUM,
        evidence_bundle=PurposeEvidenceBundle(
            bundle_id="bundle-1",
            module_id="module-1",
            module_path="app/ingestion.py",
        ),
    )
    docs = [
        EvidenceReference(
            source_kind="module_docstring",
            repository_path="app/ingestion.py",
            quoted_text="This module serves API responses for the order dashboard.",
            observed_or_inferred="observed",
            analysis_method=AnalysisMethod.STATIC_ANALYSIS,
        )
    ]

    drift = detect_documentation_drift(profile, docs)

    assert drift is not None
    assert drift.drift_type == "contradiction"
