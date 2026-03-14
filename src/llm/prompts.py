"""Prompt builders for Semanticist provider-backed operations."""

from __future__ import annotations

from src.models.semantic import PurposeEvidenceBundle


def build_purpose_prompt(bundle: PurposeEvidenceBundle) -> str:
    imports = ", ".join(bundle.imports[:8]) or "none"
    public_api = ", ".join(bundle.public_api_signals[:10]) or "none"
    inputs = ", ".join(bundle.lineage_relationships.get("inputs", [])[:8]) or "none"
    outputs = ", ".join(bundle.lineage_relationships.get("outputs", [])[:8]) or "none"
    excerpts = "\n".join(
        f"- {ref.repository_path}:{ref.line_start or 1}-{ref.line_end or ref.line_start or 1}: {ref.quoted_text or ''}".strip()
        for ref in bundle.code_excerpt_refs[:4]
    ) or "- no excerpts available"
    return (
        "You are generating a grounded business-purpose summary for one source module.\n"
        "Do not restate docstrings or comments unless the evidence proves the same behavior.\n"
        "Write exactly 2 concise sentences: first sentence describes what the module does, "
        "second sentence explains why it exists in the wider system.\n\n"
        f"Module path: {bundle.module_path}\n"
        f"Imports: {imports}\n"
        f"Public API signals: {public_api}\n"
        f"Lineage inputs: {inputs}\n"
        f"Lineage outputs: {outputs}\n"
        f"Graph metrics: {bundle.graph_metrics}\n"
        f"Git velocity: {bundle.git_velocity_signals}\n"
        f"Code evidence:\n{excerpts}\n"
    )


def build_day_one_prompt(context: str) -> str:
    return (
        "You are synthesizing five first-day-on-the-job answers for a brownfield repository.\n"
        "Use only the supplied evidence catalog and heuristic baselines.\n"
        "Every answer must clearly distinguish observed facts from inferred conclusions.\n"
        "Only cite evidence IDs that appear in the supplied context, and prefer citations with real file paths and line numbers.\n"
        "Return a single JSON object with this exact shape:\n"
        "{\n"
        '  "answers": [\n'
        "    {\n"
        '      "question_id": "primary_ingestion_path",\n'
        '      "observation": "Observed facts only",\n'
        '      "inference": "Reasoned conclusion from the observed facts",\n'
        '      "answer_text": "Optional final combined answer. If omitted, observation and inference will be combined.",\n'
        '      "confidence": "low|medium|high",\n'
        '      "evidence_ids": ["semantic_evidence:..."]\n'
        "    }\n"
        "  ]\n"
        "}\n"
        "Return all five required question IDs exactly once.\n\n"
        f"{context}\n"
    )
