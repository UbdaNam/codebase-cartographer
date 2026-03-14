"""Day-One answer synthesis for Semanticist."""

from __future__ import annotations

import json
import logging
from collections import Counter
from pathlib import Path
import re
from typing import Any

from src.config import AppSettings
from src.graph.survey import extract_git_velocity
from src.llm.budget import BudgetExceededError, ContextWindowBudget
from src.llm.prompts import build_day_one_prompt
from src.llm.provider import ChatRequest, LLMProvider, ProviderError
from src.models.enums import AnalysisMethod, ConfidenceBand
from src.models.graph import DatasetNode, GraphPayload, ModuleNode, TransformationNode
from src.models.semantic import DayOneAnswer, DomainCluster, EvidenceReference, SemanticModuleProfile
from src.utils.logging import log_event


DAY_ONE_QUESTIONS = [
    ("primary_ingestion_path", "What is the primary data ingestion path?"),
    ("critical_outputs", "What are the 3-5 most critical output datasets or endpoints?"),
    ("critical_module_blast_radius", "What is the blast radius if the most critical module fails?"),
    ("business_logic_concentration", "Where is the business logic concentrated versus distributed?"),
    ("recent_change_hotspots", "What has changed most frequently in the last 90 days?"),
]

_QUESTION_ORDER = [question_id for question_id, _ in DAY_ONE_QUESTIONS]


def synthesize_day_one_answers(
    *,
    prepared_repo_root: Path,
    settings: AppSettings,
    module_graph: GraphPayload,
    lineage_graph: GraphPayload,
    profiles: list[SemanticModuleProfile],
    domains: list[DomainCluster],
    provider: LLMProvider | None = None,
    budget: ContextWindowBudget | None = None,
    logger: logging.Logger | None = None,
) -> tuple[list[DayOneAnswer], list[str], bool]:
    module_nodes = [node for node in module_graph.nodes if isinstance(node, ModuleNode)]
    dataset_nodes = {node.node_id: node for node in lineage_graph.nodes if isinstance(node, DatasetNode)}
    transformation_nodes = {
        node.node_id: node for node in lineage_graph.nodes if isinstance(node, TransformationNode)
    }
    profile_by_module = {profile.module_id: profile for profile in profiles}
    fallback_answers = [
        _primary_ingestion_answer(transformation_nodes, dataset_nodes, lineage_graph),
        _critical_outputs_answer(lineage_graph, dataset_nodes, transformation_nodes),
        _blast_radius_answer(module_graph, module_nodes, profile_by_module),
        _business_logic_answer(domains),
        _velocity_answer(prepared_repo_root, settings, module_nodes),
    ]
    warnings: list[str] = []
    if provider is None or budget is None or not provider.is_available():
        return fallback_answers, warnings, False

    context, evidence_lookup = _build_day_one_context(
        module_graph=module_graph,
        lineage_graph=lineage_graph,
        fallback_answers=fallback_answers,
        profiles=profiles,
        domains=domains,
    )
    prompt = build_day_one_prompt(context)
    try:
        reserved_prompt_tokens, reserved_completion_tokens = budget.reserve(
            prompt,
            min(settings.semantic_max_completion_tokens, max(400, settings.semantic_completion_reserve_tokens * 3)),
        )
        result = provider.generate_text(
            ChatRequest(
                prompt=prompt,
                model=settings.semantic_synthesis_model,
                max_output_tokens=settings.semantic_max_completion_tokens,
            )
        )
        budget.record_usage(
            result.prompt_tokens,
            result.completion_tokens,
            reserved_prompt_tokens=reserved_prompt_tokens,
            reserved_completion_tokens=reserved_completion_tokens,
        )
        if logger:
            log_event(
                logger,
                event="semanticist_day_one_provider_success",
                model=result.model or settings.semantic_synthesis_model,
                prompt_tokens=result.prompt_tokens,
                completion_tokens=result.completion_tokens,
            )
        return _parse_day_one_response(
            raw_text=result.text,
            fallback_answers=fallback_answers,
            evidence_lookup=evidence_lookup,
        )
    except (BudgetExceededError, ProviderError, ValueError, json.JSONDecodeError) as exc:
        warning_code = (
            "semantic_day_one_fallback:BudgetExceededError"
            if isinstance(exc, BudgetExceededError)
            else f"semantic_day_one_fallback:{type(exc).__name__}"
        )
        warnings.append(warning_code)
        detail = str(exc).strip()
        if detail and not isinstance(exc, BudgetExceededError):
            warnings.append(f"semantic_day_one_detail:{detail[:160]}")
        if logger:
            log_event(
                logger,
                event="semanticist_day_one_provider_fallback",
                error_type=type(exc).__name__,
                error_detail=str(exc)[:240],
            )
        return _mark_day_one_fallback(fallback_answers, warnings), warnings, True


def _build_day_one_context(
    *,
    module_graph: GraphPayload,
    lineage_graph: GraphPayload,
    fallback_answers: list[DayOneAnswer],
    profiles: list[SemanticModuleProfile],
    domains: list[DomainCluster],
) -> tuple[str, dict[str, EvidenceReference]]:
    profile_by_module = {profile.module_id: profile for profile in profiles}
    module_nodes = {node.node_id: node for node in module_graph.nodes if isinstance(node, ModuleNode)}
    transformation_nodes = {
        node.node_id: node for node in lineage_graph.nodes if isinstance(node, TransformationNode)
    }
    evidence_lookup: dict[str, EvidenceReference] = {}
    questions: list[dict[str, Any]] = []

    for fallback in fallback_answers:
        refs = _gather_answer_evidence(
            answer=fallback,
            profile_by_module=profile_by_module,
            module_nodes=module_nodes,
            transformation_nodes=transformation_nodes,
        )
        evidence_items = []
        for ref in refs:
            if ref.reference_id is None:
                continue
            evidence_lookup[ref.reference_id] = ref
            evidence_items.append(
                {
                    "evidence_id": ref.reference_id,
                    "source_kind": ref.source_kind,
                    "repository_path": ref.repository_path,
                    "line_start": ref.line_start,
                    "line_end": ref.line_end,
                    "quoted_text": ref.quoted_text,
                    "observed_or_inferred": ref.observed_or_inferred,
                }
            )
        related_modules = []
        for module_id in fallback.supporting_module_ids[:8]:
            profile = profile_by_module.get(module_id)
            node = module_nodes.get(module_id)
            if profile is None:
                continue
            related_modules.append(
                {
                    "module_id": module_id,
                    "relative_path": profile.relative_path,
                    "purpose_statement": profile.purpose_statement,
                    "domain_label": profile.domain_label,
                    "pagerank_score": node.pagerank_score if node else None,
                    "change_velocity_30d": node.change_velocity_recent if node else None,
                }
            )
        questions.append(
            {
                "question_id": fallback.question_id,
                "question_text": fallback.question_text,
                "heuristic_baseline": fallback.answer_text,
                "related_modules": related_modules,
                "evidence_catalog": evidence_items[:8],
            }
        )

    top_domains = sorted(domains, key=lambda item: (-len(item.module_ids), item.label.lower()))[:8]
    domain_summaries = [
        {
            "label": domain.label,
            "module_count": len(domain.module_ids),
            "summary": domain.summary,
            "sample_modules": [
                profile_by_module[module_id].relative_path
                for module_id in domain.module_ids[:5]
                if module_id in profile_by_module
            ],
        }
        for domain in top_domains
    ]
    graph_summary = {
        "module_graph": module_graph.graph_metadata,
        "lineage_graph": lineage_graph.graph_metadata,
    }
    payload = {
        "questions": questions,
        "domain_summaries": domain_summaries,
        "graph_summary": graph_summary,
    }
    return json.dumps(payload, indent=2, sort_keys=True), evidence_lookup


def _gather_answer_evidence(
    *,
    answer: DayOneAnswer,
    profile_by_module: dict[str, SemanticModuleProfile],
    module_nodes: dict[str, ModuleNode],
    transformation_nodes: dict[str, TransformationNode],
) -> list[EvidenceReference]:
    gathered: list[EvidenceReference] = []
    seen_ids: set[str] = set()

    def append_ref(ref: EvidenceReference) -> None:
        if ref.reference_id and ref.reference_id in seen_ids:
            return
        if ref.line_start is None:
            return
        if ref.reference_id:
            seen_ids.add(ref.reference_id)
        gathered.append(ref)

    for ref in answer.evidence_references:
        append_ref(ref)
    for module_id in answer.supporting_module_ids:
        profile = profile_by_module.get(module_id)
        if profile:
            for ref in profile.source_excerpt_refs[:2]:
                append_ref(ref)
        node = module_nodes.get(module_id)
        if node and node.path and not profile:
            gathered.append(
                EvidenceReference(
                    source_kind="module_path",
                    repository_path=node.path,
                    quoted_text=node.relative_path,
                    observed_or_inferred="observed",
                    analysis_method=AnalysisMethod.STATIC_ANALYSIS,
                    confidence=ConfidenceBand.LOW,
                    line_start=1,
                    line_end=1,
                )
            )
    for transformation in transformation_nodes.values():
        if transformation.module_or_file_id in answer.supporting_module_ids:
            gathered.append(
                EvidenceReference(
                    source_kind="lineage_transformation",
                    repository_path=transformation.path or ".",
                    quoted_text=transformation.display_name or transformation.canonical_name,
                    observed_or_inferred="graph_inference",
                    analysis_method=AnalysisMethod.GRAPH_INFERENCE,
                    confidence=ConfidenceBand.MEDIUM,
                    line_start=1,
                    line_end=1,
                )
            )
    return gathered[:10]


def _parse_day_one_response(
    *,
    raw_text: str,
    fallback_answers: list[DayOneAnswer],
    evidence_lookup: dict[str, EvidenceReference],
) -> tuple[list[DayOneAnswer], list[str], bool]:
    payload = _extract_json_payload(raw_text)
    answer_items = payload.get("answers")
    if not isinstance(answer_items, list):
        raise ValueError("day-one synthesis response did not contain an answers list")
    answer_map = {answer.question_id: answer for answer in fallback_answers}
    parsed: dict[str, DayOneAnswer] = {}
    warnings: list[str] = []
    for item in answer_items:
        if not isinstance(item, dict):
            continue
        question_id = str(item.get("question_id") or "").strip()
        if question_id not in answer_map:
            continue
        base = answer_map[question_id]
        observation = str(item.get("observation") or "").strip()
        inference = str(item.get("inference") or "").strip()
        answer_text = str(item.get("answer_text") or "").strip()
        if not answer_text:
            answer_text = f"Observation: {observation}\nInference: {inference}".strip()
        confidence = _parse_confidence(str(item.get("confidence") or "medium"))
        evidence_ids = [str(value) for value in item.get("evidence_ids", []) if str(value)]
        refs = [evidence_lookup[evidence_id] for evidence_id in evidence_ids if evidence_id in evidence_lookup]
        if not refs:
            refs = base.evidence_references[:4]
            warnings.append(f"semantic_day_one_missing_citations:{question_id}")
        parsed[question_id] = base.model_copy(
            update={
                "answer_text": answer_text,
                "confidence": confidence,
                "evidence_references": refs[:6],
                "is_partial": base.is_partial,
                "warning_codes": sorted(dict.fromkeys(base.warning_codes + ([] if refs else [f"missing_citations:{question_id}"]))),
            }
        )
    ordered: list[DayOneAnswer] = []
    missing_questions = False
    for question_id in _QUESTION_ORDER:
        if question_id in parsed:
            ordered.append(parsed[question_id])
        else:
            missing_questions = True
            ordered.append(
                answer_map[question_id].model_copy(
                    update={
                        "is_partial": True,
                        "warning_codes": sorted(dict.fromkeys(answer_map[question_id].warning_codes + [f"llm_answer_missing:{question_id}"])),
                    }
                )
            )
    return ordered, warnings, missing_questions


def _extract_json_payload(raw_text: str) -> dict[str, Any]:
    stripped = raw_text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*|\s*```$", "", stripped, flags=re.DOTALL).strip()
    try:
        payload = json.loads(stripped)
        if isinstance(payload, dict):
            return payload
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", stripped, flags=re.DOTALL)
    if not match:
        raise ValueError("day-one synthesis response did not contain a JSON object")
    payload = json.loads(match.group(0))
    if not isinstance(payload, dict):
        raise ValueError("day-one synthesis payload must be a JSON object")
    return payload


def _parse_confidence(value: str) -> ConfidenceBand:
    normalized = value.strip().lower()
    if normalized == "high":
        return ConfidenceBand.HIGH
    if normalized == "low":
        return ConfidenceBand.LOW
    if normalized == "medium":
        return ConfidenceBand.MEDIUM
    return ConfidenceBand.UNKNOWN


def _mark_day_one_fallback(answers: list[DayOneAnswer], warnings: list[str]) -> list[DayOneAnswer]:
    return [
        answer.model_copy(
            update={
                "is_partial": True,
                "warning_codes": sorted(dict.fromkeys(answer.warning_codes + warnings)),
            }
        )
        for answer in answers
    ]


def _primary_ingestion_answer(
    transformation_nodes: dict[str, TransformationNode],
    dataset_nodes: dict[str, DatasetNode],
    lineage_graph: GraphPayload,
) -> DayOneAnswer:
    candidate = None
    for node in sorted(transformation_nodes.values(), key=lambda item: item.path or ""):
        inputs = [
            dataset_nodes[edge.source_node_id]
            for edge in lineage_graph.edges
            if edge.target_node_id == node.node_id and edge.source_node_id in dataset_nodes
        ]
        outputs = [
            dataset_nodes[edge.target_node_id]
            for edge in lineage_graph.edges
            if edge.source_node_id == node.node_id and edge.target_node_id in dataset_nodes
        ]
        if inputs and outputs:
            candidate = (node, inputs, outputs)
            break
    if candidate is None:
        return DayOneAnswer(
            question_id=DAY_ONE_QUESTIONS[0][0],
            question_text=DAY_ONE_QUESTIONS[0][1],
            answer_text="No clear primary ingestion path could be confirmed from the available lineage evidence.",
            confidence=ConfidenceBand.LOW,
            is_partial=True,
            warning_codes=["insufficient_ingestion_evidence"],
        )
    node, inputs, outputs = candidate
    return DayOneAnswer(
        question_id=DAY_ONE_QUESTIONS[0][0],
        question_text=DAY_ONE_QUESTIONS[0][1],
        answer_text=(
            f"The strongest ingestion path starts in `{node.display_name}` where "
            f"{', '.join(item.display_name or item.canonical_name for item in inputs[:2])} flow into "
            f"{', '.join(item.display_name or item.canonical_name for item in outputs[:2])}."
        ),
        confidence=ConfidenceBand.MEDIUM,
        supporting_dataset_ids=[item.node_id for item in inputs + outputs],
        supporting_module_ids=[node.module_or_file_id] if node.module_or_file_id else [],
        evidence_references=[
            EvidenceReference(
                source_kind="lineage_transformation",
                repository_path=node.path or ".",
                quoted_text=node.display_name,
                observed_or_inferred="graph_inference",
                analysis_method=AnalysisMethod.GRAPH_INFERENCE,
                confidence=ConfidenceBand.MEDIUM,
                line_start=1,
                line_end=1,
            )
        ],
    )


def _critical_outputs_answer(
    lineage_graph: GraphPayload,
    dataset_nodes: dict[str, DatasetNode],
    transformation_nodes: dict[str, TransformationNode],
) -> DayOneAnswer:
    sink_counts: Counter[str] = Counter()
    producer_modules: set[str] = set()
    for edge in lineage_graph.edges:
        if edge.target_node_id in dataset_nodes:
            sink_counts[edge.target_node_id] += 1
            transformation = transformation_nodes.get(edge.source_node_id)
            if transformation and transformation.module_or_file_id:
                producer_modules.add(transformation.module_or_file_id)
    top_sinks = [dataset_nodes[node_id] for node_id, _ in sink_counts.most_common(5)]
    if not top_sinks:
        return DayOneAnswer(
            question_id=DAY_ONE_QUESTIONS[1][0],
            question_text=DAY_ONE_QUESTIONS[1][1],
            answer_text="No output datasets or endpoints could be ranked from the current lineage graph.",
            confidence=ConfidenceBand.LOW,
            is_partial=True,
            warning_codes=["insufficient_output_evidence"],
        )
    return DayOneAnswer(
        question_id=DAY_ONE_QUESTIONS[1][0],
        question_text=DAY_ONE_QUESTIONS[1][1],
        answer_text="The most critical outputs are " + ", ".join(
            f"`{item.display_name or item.canonical_name}`" for item in top_sinks[:5]
        ) + ".",
        confidence=ConfidenceBand.MEDIUM,
        supporting_dataset_ids=[item.node_id for item in top_sinks],
        supporting_module_ids=sorted(producer_modules),
        evidence_references=[
            EvidenceReference(
                source_kind="lineage_dataset",
                repository_path=item.path or ".",
                quoted_text=item.display_name or item.canonical_name,
                observed_or_inferred="graph_inference",
                analysis_method=AnalysisMethod.GRAPH_INFERENCE,
                confidence=ConfidenceBand.MEDIUM,
                line_start=1,
                line_end=1,
            )
            for item in top_sinks[:5]
        ],
    )


def _blast_radius_answer(
    module_graph: GraphPayload,
    module_nodes: list[ModuleNode],
    profile_by_module: dict[str, SemanticModuleProfile],
) -> DayOneAnswer:
    critical = max(
        module_nodes,
        key=lambda node: ((node.pagerank_score or 0.0), node.change_velocity_recent or 0, node.relative_path),
        default=None,
    )
    if critical is None:
        return DayOneAnswer(
            question_id=DAY_ONE_QUESTIONS[2][0],
            question_text=DAY_ONE_QUESTIONS[2][1],
            answer_text="No critical module could be derived from the current module graph.",
            confidence=ConfidenceBand.LOW,
            is_partial=True,
            warning_codes=["insufficient_module_graph"],
        )
    downstream = [edge.target_node_id for edge in module_graph.edges if edge.source_node_id == critical.node_id]
    profile = profile_by_module.get(critical.node_id)
    return DayOneAnswer(
        question_id=DAY_ONE_QUESTIONS[2][0],
        question_text=DAY_ONE_QUESTIONS[2][1],
        answer_text=(
            f"The most critical module is `{critical.relative_path}`. "
            f"If it fails, at least {len(downstream)} directly dependent modules or graph edges are at risk."
        ),
        confidence=ConfidenceBand.MEDIUM,
        supporting_module_ids=[critical.node_id, *downstream],
        evidence_references=profile.evidence_references[:2] if profile else [],
    )


def _business_logic_answer(domains: list[DomainCluster]) -> DayOneAnswer:
    if not domains:
        return DayOneAnswer(
            question_id=DAY_ONE_QUESTIONS[3][0],
            question_text=DAY_ONE_QUESTIONS[3][1],
            answer_text="Business-logic concentration could not be inferred because no domains were formed.",
            confidence=ConfidenceBand.LOW,
            is_partial=True,
            warning_codes=["insufficient_domain_evidence"],
        )
    largest = max(domains, key=lambda item: len(item.module_ids))
    total = sum(len(item.module_ids) for item in domains)
    share = len(largest.module_ids) / max(1, total)
    distribution = "concentrated" if share >= 0.45 else "distributed"
    return DayOneAnswer(
        question_id=DAY_ONE_QUESTIONS[3][0],
        question_text=DAY_ONE_QUESTIONS[3][1],
        answer_text=(
            f"Business logic is {distribution}, with the strongest concentration in the `{largest.label}` domain "
            f"covering {len(largest.module_ids)} of {total} semantic modules."
        ),
        confidence=ConfidenceBand.MEDIUM,
        supporting_module_ids=largest.module_ids,
    )


def _velocity_answer(prepared_repo_root: Path, settings: AppSettings, module_nodes: list[ModuleNode]) -> DayOneAnswer:
    module_paths = {node.relative_path for node in module_nodes}
    module_id_by_path = {node.relative_path: node.node_id for node in module_nodes}
    velocity, warnings = extract_git_velocity(prepared_repo_root, days=settings.semantic_git_lookback_days)
    filtered = [(path, count) for path, count in velocity.items() if path in module_paths]
    filtered.sort(key=lambda item: (-item[1], item[0]))
    top = filtered[:5]
    if not top:
        return DayOneAnswer(
            question_id=DAY_ONE_QUESTIONS[4][0],
            question_text=DAY_ONE_QUESTIONS[4][1],
            answer_text="Recent change hotspots could not be derived from git history.",
            confidence=ConfidenceBand.LOW,
            is_partial=True,
            warning_codes=warnings or ["git_velocity_unavailable"],
        )
    return DayOneAnswer(
        question_id=DAY_ONE_QUESTIONS[4][0],
        question_text=DAY_ONE_QUESTIONS[4][1],
        answer_text="The most frequently changed modules in the last 90 days are " + ", ".join(
            f"`{path}` ({count} changes)" for path, count in top
        ) + ".",
        confidence=ConfidenceBand.MEDIUM,
        evidence_references=[
            EvidenceReference(
                source_kind="git_velocity",
                repository_path=path,
                quoted_text=str(count),
                observed_or_inferred="observed",
                analysis_method=AnalysisMethod.STATIC_ANALYSIS,
                confidence=ConfidenceBand.MEDIUM,
                line_start=1,
                line_end=1,
            )
            for path, count in top
        ],
        supporting_module_ids=[
            module_id_by_path[path]
            for path, _count in top
            if path in module_id_by_path
        ],
        warning_codes=warnings,
    )
