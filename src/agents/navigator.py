"""LangGraph-based Navigator query interface for final-stage artifacts."""

from __future__ import annotations

from collections.abc import Iterable
import json
import logging
from pathlib import Path
from typing import Annotated, Any, TypedDict, cast

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import InjectedState, ToolNode

from src.config import AppSettings
from src.index.semantic_index import load_semantic_index, search_semantic_index
from src.llm.langgraph_openrouter import build_langgraph_chat_model
from src.llm.openrouter import OpenRouterProvider
from src.llm.provider import EmbeddingRequest, LLMProvider, NullProvider, ProviderError
from src.models.enums import ConfidenceBand, EdgeKind
from src.models.graph import DatasetNode, GraphPayload, LineageSummaryPayload, ModuleNode, SurveySummaryPayload, TransformationNode
from src.models.navigator import (
    NavigatorAnswerItem,
    NavigatorCitation,
    NavigatorRequest,
    NavigatorResponse,
    NavigatorSynthesisPayload,
    NavigatorToolEnvelope,
)
from src.models.run_metadata import RunSummary
from src.models.semantic import DayOneAnswersPayload, DocumentationDriftPayload, DomainMapPayload, EvidenceReference, ModuleSemanticsPayload
from src.models.trace import TraceEvent
from src.utils.citations import dedupe_references, derive_confidence, evidence_record_to_reference, format_evidence_reference, reference_to_navigator_citation
from src.utils.incremental import load_latest_successful_summary
from src.utils.ids import stable_id
from src.utils.trace import TraceWriter


class NavigatorGraphState(TypedDict, total=False):
    messages: Annotated[list[BaseMessage], add_messages]
    request: NavigatorRequest
    forced_tool_mode: bool
    chosen_tool: str
    retrieved_context: dict[str, object]
    repo_context_bundle: str
    repo_context_references: list[EvidenceReference]
    evidence_references: list[EvidenceReference]
    tool_outputs: list[NavigatorToolEnvelope]
    response_draft: list[NavigatorAnswerItem]
    summary: str
    partial_result_flags: list[str]
    trace_event_ids: list[str]
    used_model_synthesis: bool
    tool_round_count: int
    processed_tool_call_ids: list[str]


class NavigatorAgent:
    """Retrieval-first LangGraph agent over persisted Cartographer artifacts."""

    def __init__(self, settings: AppSettings, provider: LLMProvider | None = None):
        self.settings = settings
        self.provider = provider or self._build_provider()
        self._chat_model = build_langgraph_chat_model(settings, model_name=settings.navigator_agent_model)
        self._tools = self._build_tools()
        self._tool_node = ToolNode(self._tools)
        self._planner_model = self._chat_model.bind_tools(self._tools) if self._chat_model is not None else None
        self._graph = self._build_graph()

    def query(self, request: NavigatorRequest, *, logger: logging.Logger | None = None) -> NavigatorResponse:
        """Execute a Navigator request against the latest or selected run."""

        initial_state: NavigatorGraphState = {
            "messages": [HumanMessage(content=request.query_text)],
            "request": request,
            "forced_tool_mode": request.query_type is not None,
            "chosen_tool": request.query_type or "",
            "retrieved_context": {},
            "repo_context_bundle": "",
            "repo_context_references": [],
            "evidence_references": [],
            "tool_outputs": [],
            "response_draft": [],
            "summary": "",
            "partial_result_flags": [],
            "trace_event_ids": [],
            "used_model_synthesis": False,
            "tool_round_count": 0,
            "processed_tool_call_ids": [],
        }
        state = self._graph.invoke(initial_state)
        if logger:
            logger.info("navigator_query_completed")
        return NavigatorResponse(
            request=state["request"],
            summary=state["summary"],
            results=state["response_draft"],
            partial_result_flags=state["partial_result_flags"],
            trace_event_ids=state["trace_event_ids"],
            used_model_synthesis=state["used_model_synthesis"],
        )

    def _build_graph(self):
        graph = StateGraph(NavigatorGraphState)
        graph.add_node("classify_query", self.classify_query)
        graph.add_node("retrieve_relevant_artifacts", self.retrieve_relevant_artifacts)
        graph.add_node("select_tool", self.select_tool)
        graph.add_node("execute_tool", self.execute_tool)
        graph.add_node("synthesize_response", self.synthesize_response)
        graph.add_node("attach_citations_and_trust_metadata", self.attach_citations_and_trust_metadata)
        graph.add_edge(START, "classify_query")
        graph.add_edge("classify_query", "retrieve_relevant_artifacts")
        graph.add_edge("retrieve_relevant_artifacts", "select_tool")
        graph.add_conditional_edges(
            "select_tool",
            self._route_after_select_tool,
            {
                "execute_tool": "execute_tool",
                "synthesize_response": "synthesize_response",
            },
        )
        graph.add_conditional_edges(
            "execute_tool",
            self._route_after_execute_tool,
            {
                "select_tool": "select_tool",
                "synthesize_response": "synthesize_response",
            },
        )
        graph.add_edge("synthesize_response", "attach_citations_and_trust_metadata")
        graph.add_edge("attach_citations_and_trust_metadata", END)
        return graph.compile()

    def classify_query(self, state: NavigatorGraphState) -> NavigatorGraphState:
        return {
            "request": state["request"],
            "forced_tool_mode": state["request"].query_type is not None,
            "chosen_tool": state["request"].query_type or "",
        }

    def retrieve_relevant_artifacts(self, state: NavigatorGraphState) -> NavigatorGraphState:
        request = state["request"]
        summary, run_dir = self._resolve_run(request.run_id)
        if summary is None or run_dir is None:
            return {
                "retrieved_context": {},
                "partial_result_flags": ["navigator_run_not_found"],
            }
        context = {
            "summary": summary,
            "run_dir": run_dir,
            "module_graph": GraphPayload.model_validate_json((run_dir / "module_graph.json").read_text(encoding="utf-8")),
            "survey_summary": SurveySummaryPayload.model_validate_json((run_dir / "survey_summary.json").read_text(encoding="utf-8")),
            "lineage_graph": GraphPayload.model_validate_json((run_dir / "lineage_graph.json").read_text(encoding="utf-8")),
            "lineage_summary": LineageSummaryPayload.model_validate_json((run_dir / "lineage_summary.json").read_text(encoding="utf-8")),
            "module_semantics": ModuleSemanticsPayload.model_validate_json((run_dir / "module_semantics.json").read_text(encoding="utf-8")),
            "documentation_drift": DocumentationDriftPayload.model_validate_json((run_dir / "documentation_drift.json").read_text(encoding="utf-8")),
            "domain_map": DomainMapPayload.model_validate_json((run_dir / "domain_map.json").read_text(encoding="utf-8")),
            "day_one_answers": DayOneAnswersPayload.model_validate_json((run_dir / "day_one_answers.json").read_text(encoding="utf-8")),
            "semantic_index": load_semantic_index(run_dir / "semantic_index"),
            "codebase_markdown": self._safe_read_text(run_dir / "CODEBASE.md"),
            "onboarding_markdown": self._safe_read_text(run_dir / "onboarding_brief.md"),
            "trace_writer": TraceWriter(self.settings.trace_log_path(run_dir)),
        }
        return {
            "retrieved_context": context,
            "repo_context_bundle": self._build_repo_context_bundle(context),
            "repo_context_references": self._build_repo_context_references(context),
        }

    def select_tool(self, state: NavigatorGraphState) -> NavigatorGraphState:
        if not state.get("retrieved_context"):
            event = self._trace(
                state,
                action="planner_skipped_without_context",
                output_summary={"reason": "missing_run_context"},
                references=[],
                method_type="reuse",
            )
            return {"trace_event_ids": [*state["trace_event_ids"], event.event_id or ""]}
        if state.get("forced_tool_mode") and state.get("tool_round_count", 0) == 0:
            request = state["request"]
            forced_tool = request.query_type or "find_implementation"
            ai_message = AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": forced_tool,
                        "args": self._forced_tool_args(request),
                        "id": stable_id("navigator_forced_tool", request.query_text, forced_tool),
                        "type": "tool_call",
                    }
                ],
            )
            event = self._trace(
                state,
                action="planner_decision",
                output_summary={"selected_tools": [forced_tool], "forced": True},
                references=state["repo_context_references"],
                method_type="reuse",
            )
            return {
                "messages": [ai_message],
                "chosen_tool": forced_tool,
                "tool_round_count": 1,
                "trace_event_ids": [*state["trace_event_ids"], event.event_id or ""],
            }
        if not self._planner_is_available(state):
            event = self._trace(
                state,
                action="planner_unavailable",
                output_summary={"reason": "provider_unavailable_or_inference_disabled"},
                references=state["repo_context_references"],
                method_type="reuse",
            )
            flags = [*state["partial_result_flags"]]
            if state["request"].query_type is None:
                flags.append("navigator_model_unavailable")
            return {
                "partial_result_flags": sorted(dict.fromkeys(flags)),
                "trace_event_ids": [*state["trace_event_ids"], event.event_id or ""],
            }
        if state.get("tool_round_count", 0) >= self.settings.navigator_max_tool_rounds:
            event = self._trace(
                state,
                action="planner_round_limit_reached",
                output_summary={"tool_round_count": state.get("tool_round_count", 0)},
                references=state["evidence_references"],
                method_type="reuse",
            )
            return {
                "partial_result_flags": sorted(dict.fromkeys([*state["partial_result_flags"], "navigator_tool_round_limit_reached"])),
                "trace_event_ids": [*state["trace_event_ids"], event.event_id or ""],
            }
        ai_message = self._invoke_planner_model(state)
        chosen_tool = ai_message.tool_calls[0]["name"] if ai_message.tool_calls else "direct_answer"
        event = self._trace(
            state,
            action="planner_decision",
            output_summary={"selected_tools": [call["name"] for call in ai_message.tool_calls] or ["direct_answer"]},
            references=state["repo_context_references"],
            method_type="llm",
        )
        return {
            "messages": [ai_message],
            "chosen_tool": chosen_tool,
            "tool_round_count": state.get("tool_round_count", 0) + (1 if ai_message.tool_calls else 0),
            "trace_event_ids": [*state["trace_event_ids"], event.event_id or ""],
        }

    def execute_tool(self, state: NavigatorGraphState) -> NavigatorGraphState:
        if not state.get("retrieved_context"):
            event = self._trace(
                state,
                action="execute_tool_without_context",
                output_summary={"result_count": 0},
                references=[],
                method_type="reuse",
            )
            return {
                "response_draft": [],
                "evidence_references": [],
                "partial_result_flags": sorted(dict.fromkeys([*state["partial_result_flags"], "navigator_run_not_found"])),
                "trace_event_ids": [*state["trace_event_ids"], event.event_id or ""],
            }
        tool_state = cast(dict[str, Any], self._tool_node.invoke(state))
        new_messages = cast(list[BaseMessage], tool_state.get("messages", []))
        processed_ids = set(state.get("processed_tool_call_ids", []))
        envelopes: list[NavigatorToolEnvelope] = []
        trace_event_ids = list(state["trace_event_ids"])
        partial_flags = list(state["partial_result_flags"])
        references = list(state["evidence_references"])
        for message in new_messages:
            if not isinstance(message, ToolMessage):
                continue
            if message.tool_call_id in processed_ids:
                continue
            processed_ids.add(message.tool_call_id)
            envelope = self._parse_tool_message(message)
            envelopes.append(envelope)
            references.extend(envelope.evidence_references)
            partial_flags.extend(envelope.partial_result_flags)
            event = self._trace(
                state,
                action=f"tool_{envelope.tool_name}",
                output_summary={"result_count": len(envelope.answer_items)},
                references=envelope.evidence_references,
                method_type=self._tool_method_type(envelope.tool_name),
            )
            trace_event_ids.append(event.event_id or "")
        accumulated_outputs = [*state["tool_outputs"], *envelopes]
        if (not state.get("forced_tool_mode")) and state.get("tool_round_count", 0) >= self.settings.navigator_max_tool_rounds:
            partial_flags.append("navigator_tool_round_limit_reached")
        return {
            "messages": new_messages,
            "tool_outputs": accumulated_outputs,
            "response_draft": self._flatten_tool_outputs(accumulated_outputs),
            "evidence_references": dedupe_references(references),
            "partial_result_flags": sorted(dict.fromkeys(partial_flags)),
            "processed_tool_call_ids": sorted(processed_ids),
            "trace_event_ids": trace_event_ids,
        }

    def synthesize_response(self, state: NavigatorGraphState) -> NavigatorGraphState:
        items = list(state.get("response_draft", []))
        references = dedupe_references([*state.get("repo_context_references", []), *state.get("evidence_references", [])])
        summary = self._last_direct_answer(state)
        used_model = False
        synthesis = None
        if self._planner_is_available(state) and (items or summary or self._looks_like_repo_summary_question(state["request"].query_text)):
            synthesis = self._invoke_synthesis_model(state, items, summary)
            if synthesis is not None:
                summary = synthesis.summary.strip()
                used_model = True
        if not items:
            fallback_item = self._build_repo_context_item(
                state,
                answer_text=summary or self._deterministic_repo_summary(state),
                observed_facts=synthesis.observed_facts if synthesis is not None else self._repo_observed_facts(state),
                inferred_notes=synthesis.inferred_notes if synthesis is not None else self._repo_inferred_notes(state),
            )
            items = [fallback_item] if fallback_item is not None else []
        if not summary:
            summary = items[0].answer_text if items else "No matching architectural context was found."
        if used_model:
            items = self._merge_summary_notes_into_results(items, synthesis)
        elif state["request"].query_type is None and not self._planner_is_available(state) and not self._looks_like_repo_summary_question(state["request"].query_text):
            summary = (
                "Navigator query planning is unavailable without model access. "
                "Use --query-type for a deterministic tool query or enable the configured model provider."
            )
            items = []
        event = self._trace(
            state,
            action="synthesize_response",
            output_summary={"used_model_synthesis": used_model, "result_count": len(items)},
            references=references,
            method_type="llm" if used_model else "synthesis",
        )
        return {
            "response_draft": items,
            "summary": summary,
            "used_model_synthesis": used_model or bool(self._last_direct_answer(state)),
            "trace_event_ids": [*state["trace_event_ids"], event.event_id or ""],
        }

    def attach_citations_and_trust_metadata(self, state: NavigatorGraphState) -> NavigatorGraphState:
        items: list[NavigatorAnswerItem] = []
        partial_flags = list(state["partial_result_flags"])
        missing_citations = False
        for item in state["response_draft"]:
            citations = self._dedupe_citations(item.citations)
            warning_codes = list(item.warning_codes)
            if not citations:
                warning_codes.append("navigator_missing_citations")
                missing_citations = True
            items.append(item.model_copy(update={"citations": citations, "warning_codes": sorted(dict.fromkeys(warning_codes))}))
        if missing_citations:
            partial_flags.append("navigator_missing_citations")
        event = self._trace(
            state,
            action="attach_citations_and_trust_metadata",
            output_summary={"citation_count": sum(len(item.citations) for item in items)},
            references=state["evidence_references"],
            method_type="reuse",
        )
        return {
            "response_draft": items,
            "partial_result_flags": sorted(dict.fromkeys(partial_flags)),
            "trace_event_ids": [*state["trace_event_ids"], event.event_id or ""],
        }

    def run_find_implementation(self, concept: str, request: NavigatorRequest, context: dict[str, object]):
        snapshot = context["semantic_index"]
        query_vector = self._embed_query_text(concept, snapshot.embedding_model)
        results = search_semantic_index(
            snapshot,
            concept,
            max_results=request.max_results * 3,
            query_vector=query_vector,
        )
        items: list[NavigatorAnswerItem] = []
        refs: list[EvidenceReference] = []
        profiles = {profile.module_id: profile for profile in context["module_semantics"].profiles}
        candidates = []
        for entry in results:
            profile = profiles.get(entry.module_id)
            entry_refs = dedupe_references((profile.evidence_references if profile is not None else entry.evidence_references), limit=4)
            candidates.append((entry, profile, entry_refs))
        evidence_backed = [candidate for candidate in candidates if candidate[2]]
        if evidence_backed:
            candidates = evidence_backed
        for entry, profile, entry_refs in candidates[: request.max_results]:
            refs.extend(entry_refs)
            warning_codes = [] if entry_refs else ["navigator_semantic_match_without_evidence"]
            items.append(
                NavigatorAnswerItem(
                    title=entry.module_path,
                    answer_text=profile.purpose_statement if profile is not None else entry.purpose_statement,
                    confidence=derive_confidence(entry_refs) if entry_refs else (profile.purpose_confidence if profile is not None else ConfidenceBand.LOW),
                    citations=[reference_to_navigator_citation(reference, artifact_reference="semantic_index/snapshot.json") for reference in entry_refs],
                    observed_facts=[
                        f"Assigned to domain {entry.domain_cluster or 'unclassified'}.",
                        *(["This match is grounded in module evidence references."] if entry_refs else []),
                    ],
                    inferred_notes=["Implementation ranking combines semantic retrieval with lexical overlap."],
                    warning_codes=warning_codes,
                )
            )
        flags = [] if items else ["navigator_no_semantic_matches"]
        return items, dedupe_references(refs), flags

    def run_trace_lineage(self, dataset: str, direction: str, request: NavigatorRequest, context: dict[str, object]):
        lineage_graph: GraphPayload = context["lineage_graph"]
        node_by_id = {node.node_id or "": node for node in lineage_graph.nodes}
        edges = sorted(lineage_graph.edges, key=lambda item: item.edge_id or "")
        target = dataset.lower()
        datasets = [
            node
            for node in lineage_graph.nodes
            if isinstance(node, DatasetNode) and target in ((node.display_name or node.canonical_name).lower())
        ]
        items: list[NavigatorAnswerItem] = []
        refs: list[EvidenceReference] = []
        for dataset_node in datasets[: request.max_results]:
            local_refs: list[EvidenceReference] = []
            chains: list[str] = []
            related_edges = [
                edge
                for edge in edges
                if edge.source_node_id == dataset_node.node_id or edge.target_node_id == dataset_node.node_id
            ]
            for edge in related_edges[:8]:
                if direction == "upstream" and edge.kind != EdgeKind.PRODUCES:
                    continue
                if direction == "downstream" and edge.kind != EdgeKind.CONSUMES:
                    continue
                other_id = edge.source_node_id if edge.target_node_id == dataset_node.node_id else edge.target_node_id
                other = node_by_id.get(other_id)
                if other is None:
                    continue
                if edge.target_node_id == dataset_node.node_id:
                    chains.append(f"{other.canonical_name} --{edge.kind.value}--> {dataset_node.canonical_name}")
                else:
                    chains.append(f"{dataset_node.canonical_name} --{edge.kind.value}--> {other.canonical_name}")
                local_refs.extend(
                    evidence_record_to_reference(record, source_kind="lineage_graph", artifact_path="lineage_graph.json")
                    for record in [*dataset_node.evidence[:1], *edge.evidence[:1]]
                )
            local_refs = dedupe_references(local_refs, limit=6)
            refs.extend(local_refs)
            items.append(
                NavigatorAnswerItem(
                    title=dataset_node.canonical_name,
                    answer_text="; ".join(chains) if chains else "No lineage edges were found for the requested dataset.",
                    confidence=derive_confidence(local_refs) if chains else ConfidenceBand.LOW,
                    citations=[reference_to_navigator_citation(reference, artifact_reference="lineage_graph.json") for reference in local_refs],
                    observed_facts=[f"Dataset node `{dataset_node.canonical_name}` exists in the persisted lineage graph."],
                    inferred_notes=["Lineage traversal is graph-based over Hydrologist output."],
                    warning_codes=[] if local_refs else ["navigator_lineage_without_citations"],
                )
            )
        flags = [] if items else ["navigator_lineage_target_not_found"]
        return items, dedupe_references(refs), flags

    def run_blast_radius(self, module_path: str, _: NavigatorRequest, context: dict[str, object]):
        module_graph: GraphPayload = context["module_graph"]
        lineage_graph: GraphPayload = context["lineage_graph"]
        target = module_path.lower()
        module = next(
            (node for node in module_graph.nodes if isinstance(node, ModuleNode) and target in node.relative_path.lower()),
            None,
        )
        if module is None:
            return [], [], ["navigator_module_not_found"]
        reverse_dependents = [
            edge.source_node_id
            for edge in module_graph.edges
            if edge.kind == EdgeKind.IMPORTS and edge.target_node_id == module.node_id
        ]
        dependent_modules = sorted(
            (
                node.relative_path
                for node in module_graph.nodes
                if isinstance(node, ModuleNode) and node.node_id in reverse_dependents
            ),
        )
        impacted_datasets = sorted(
            {
                produced.canonical_name
                for node in lineage_graph.nodes
                if isinstance(node, TransformationNode) and (node.path or "").lower() == module.relative_path.lower()
                for edge in lineage_graph.edges
                if edge.source_node_id == node.node_id and edge.kind == EdgeKind.PRODUCES
                for produced in [next((item for item in lineage_graph.nodes if item.node_id == edge.target_node_id and isinstance(item, DatasetNode)), None)]
                if produced is not None
            }
        )
        refs = dedupe_references(
            [
                *(evidence_record_to_reference(record, source_kind="module_graph", artifact_path="module_graph.json") for record in module.evidence[:1]),
                *(
                    evidence_record_to_reference(record, source_kind="lineage_graph", artifact_path="lineage_graph.json")
                    for transformation in lineage_graph.nodes
                    if isinstance(transformation, TransformationNode) and (transformation.path or "") == module.relative_path
                    for record in transformation.evidence[:1]
                ),
            ],
            limit=6,
        )
        item = NavigatorAnswerItem(
            title=module.relative_path,
            answer_text=(
                f"{len(dependent_modules)} modules import this module and "
                f"{len(impacted_datasets)} datasets are produced by transformations mapped to the same path."
            ),
            confidence=derive_confidence(refs) if refs else ConfidenceBand.MEDIUM,
            citations=[reference_to_navigator_citation(reference, artifact_reference="module_graph.json") for reference in refs],
            observed_facts=[
                *(f"Dependent module: {path}" for path in dependent_modules[:5]),
                *(f"Impacted dataset: {name}" for name in impacted_datasets[:5]),
            ] or ["No downstream dependencies were detected."],
            inferred_notes=["Blast radius combines import-graph reachability with lineage production edges."],
            warning_codes=[] if refs else ["navigator_blast_radius_without_citations"],
        )
        return [item], refs, []

    def run_explain_module(self, path: str, _: NavigatorRequest, context: dict[str, object]):
        module_semantics: ModuleSemanticsPayload = context["module_semantics"]
        drifts: DocumentationDriftPayload = context["documentation_drift"]
        target = path.lower()
        profile = next((item for item in module_semantics.profiles if target in item.relative_path.lower()), None)
        if profile is None:
            return [], [], ["navigator_module_not_found"]
        drift = next((item for item in drifts.drift_records if item.module_id == profile.module_id), None)
        refs = dedupe_references(profile.evidence_references, limit=6)
        observed = [
            f"Purpose confidence: {profile.purpose_confidence.value}.",
            f"Domain: {profile.domain_label or 'unclassified'}.",
            f"Documentation drift status: {profile.doc_drift_status}.",
        ]
        if drift is not None:
            observed.append(f"Drift type: {drift.drift_type}.")
            refs = dedupe_references([*refs, *drift.evidence_references[:2]], limit=6)
        item = NavigatorAnswerItem(
            title=profile.relative_path,
            answer_text=profile.purpose_statement,
            confidence=profile.purpose_confidence,
            citations=[reference_to_navigator_citation(reference, artifact_reference="module_semantics.json") for reference in refs],
            observed_facts=observed,
            inferred_notes=["Purpose statement is derived from Semanticist evidence bundling and may include bounded inference."],
            warning_codes=[] if refs else ["navigator_module_without_citations"],
        )
        return [item], refs, []

    def _build_tools(self):
        @tool
        def find_implementation(
            concept: str,
            state: Annotated[NavigatorGraphState, InjectedState],
        ) -> str:
            """Find likely implementation locations for a concept using persisted semantic artifacts."""

            items, refs, flags = self.run_find_implementation(concept, state["request"], state["retrieved_context"])
            return NavigatorToolEnvelope(
                tool_name="find_implementation",
                answer_items=items,
                evidence_references=refs,
                partial_result_flags=flags,
            ).model_dump_json()

        @tool
        def trace_lineage(
            dataset: str,
            direction: str = "both",
            state: Annotated[NavigatorGraphState, InjectedState] = None,
        ) -> str:
            """Trace upstream or downstream lineage for a dataset from the persisted lineage graph."""

            items, refs, flags = self.run_trace_lineage(dataset, direction, state["request"], state["retrieved_context"])
            return NavigatorToolEnvelope(
                tool_name="trace_lineage",
                answer_items=items,
                evidence_references=refs,
                partial_result_flags=flags,
            ).model_dump_json()

        @tool
        def blast_radius(
            module_path: str,
            state: Annotated[NavigatorGraphState, InjectedState],
        ) -> str:
            """Estimate blast radius for a module by combining import and lineage dependencies."""

            items, refs, flags = self.run_blast_radius(module_path, state["request"], state["retrieved_context"])
            return NavigatorToolEnvelope(
                tool_name="blast_radius",
                answer_items=items,
                evidence_references=refs,
                partial_result_flags=flags,
            ).model_dump_json()

        @tool
        def explain_module(
            path: str,
            state: Annotated[NavigatorGraphState, InjectedState],
        ) -> str:
            """Explain one module using persisted Semanticist profiles and documentation-drift signals."""

            items, refs, flags = self.run_explain_module(path, state["request"], state["retrieved_context"])
            return NavigatorToolEnvelope(
                tool_name="explain_module",
                answer_items=items,
                evidence_references=refs,
                partial_result_flags=flags,
            ).model_dump_json()

        return [find_implementation, trace_lineage, blast_radius, explain_module]

    def _build_provider(self) -> LLMProvider:
        if not self.settings.semantic_provider_enabled or not self.settings.openrouter_api_key:
            return NullProvider()
        return OpenRouterProvider(
            api_key=self.settings.openrouter_api_key,
            base_url=self.settings.openrouter_base_url,
            app_name=self.settings.openrouter_app_name,
            referer=self.settings.openrouter_referer,
        )

    def _planner_is_available(self, state: NavigatorGraphState) -> bool:
        return bool(self._planner_model is not None and state["request"].include_inference)

    def _invoke_planner_model(self, state: NavigatorGraphState) -> AIMessage:
        if self._planner_model is None:
            raise RuntimeError("planner model is unavailable")
        response = self._planner_model.invoke(
            [
                SystemMessage(content=self._build_planner_prompt(state)),
                *state.get("messages", []),
            ]
        )
        return cast(AIMessage, response)

    def _invoke_synthesis_model(
        self,
        state: NavigatorGraphState,
        items: list[NavigatorAnswerItem],
        current_summary: str,
    ) -> NavigatorSynthesisPayload | None:
        if self._chat_model is None or not state["request"].include_inference:
            return None
        response = self._chat_model.invoke(
            [
                SystemMessage(content=self._build_synthesis_prompt(state, items, current_summary)),
            ]
        )
        text = getattr(response, "content", "") or ""
        if not text.strip():
            return None
        return self._parse_synthesis_payload(text)

    def _resolve_run(self, run_id: str | None) -> tuple[RunSummary | None, Path | None]:
        runs_dir = self.settings.resolved_artifact_dir() / self.settings.runs_dir_name
        if run_id:
            run_dir = runs_dir / run_id
            summary_path = run_dir / "run_summary.json"
            if summary_path.exists():
                return RunSummary.model_validate_json(summary_path.read_text(encoding="utf-8")), run_dir
            return None, None
        return load_latest_successful_summary(runs_dir)

    def _trace(
        self,
        state: NavigatorGraphState,
        *,
        action: str,
        output_summary: dict[str, object],
        references: Iterable[EvidenceReference],
        method_type: str,
    ) -> TraceEvent:
        context = state.get("retrieved_context") or {}
        trace_writer = context.get("trace_writer")
        event = TraceEvent(
            run_id=(context["summary"].run_id if "summary" in context else state["request"].run_id or "unknown"),
            agent="navigator",
            action=action,
            input_summary={"query_text": state["request"].query_text, "chosen_tool": state.get("chosen_tool", "")},
            output_summary=output_summary,
            evidence_sources=dedupe_references(references, limit=8),
            confidence=derive_confidence(references),
            method_type=method_type,  # type: ignore[arg-type]
        )
        if not isinstance(trace_writer, TraceWriter):
            return event
        return trace_writer.append(event)

    def _route_after_select_tool(self, state: NavigatorGraphState) -> str:
        last_message = state.get("messages", [])[-1] if state.get("messages") else None
        if (
            isinstance(last_message, AIMessage)
            and last_message.tool_calls
            and state.get("tool_round_count", 0) <= self.settings.navigator_max_tool_rounds
        ):
            return "execute_tool"
        return "synthesize_response"

    def _route_after_execute_tool(self, state: NavigatorGraphState) -> str:
        if state.get("forced_tool_mode"):
            return "synthesize_response"
        if not self._planner_is_available(state):
            return "synthesize_response"
        if state.get("tool_round_count", 0) >= self.settings.navigator_max_tool_rounds:
            return "synthesize_response"
        return "select_tool"

    def _parse_tool_message(self, message: ToolMessage) -> NavigatorToolEnvelope:
        content = cast(str, message.content)
        return NavigatorToolEnvelope.model_validate_json(content)

    def _flatten_tool_outputs(self, envelopes: list[NavigatorToolEnvelope]) -> list[NavigatorAnswerItem]:
        items = [item for envelope in envelopes for item in envelope.answer_items]
        return sorted(items, key=lambda item: item.title.lower())

    def _build_planner_prompt(self, state: NavigatorGraphState) -> str:
        request = state["request"]
        return (
            "You are Navigator for Brownfield Cartographer.\n"
            "Decide whether the query can be answered directly from the retrieved repository context or whether you need tools.\n"
            "You may call only these tools: find_implementation, trace_lineage, blast_radius, explain_module.\n"
            "Use tools when the user is asking for implementation locations, lineage, impact, or a module explanation.\n"
            "If the repository context is sufficient, answer directly without tools.\n"
            "Do not invent citations or repository facts.\n"
            f"User query: {request.query_text}\n"
            f"Retrieved repository context:\n{self._truncate_text(state.get('repo_context_bundle', ''), self.settings.navigator_max_context_tokens)}\n"
        )

    def _build_synthesis_prompt(
        self,
        state: NavigatorGraphState,
        items: list[NavigatorAnswerItem],
        current_summary: str,
    ) -> str:
        request = state["request"]
        item_lines = "\n".join(
            (
                f"- {item.title}: {item.answer_text}\n"
                f"  Observed: {', '.join(item.observed_facts) or 'none'}\n"
                f"  Inferred: {', '.join(item.inferred_notes) or 'none'}\n"
                f"  Citations: {', '.join(self._format_citations_for_prompt(item.citations)) or 'none'}"
            )
            for item in items[:6]
        ) or "- none"
        repo_citations = "\n".join(f"- {format_evidence_reference(reference)}" for reference in state.get("repo_context_references", [])[:8]) or "- none"
        return (
            "You are finalizing an evidence-backed architectural answer.\n"
            "Use only the supplied repository context and tool outputs.\n"
            "Return JSON only with this exact shape:\n"
            '{"summary": "short final answer", "observed_facts": ["..."], "inferred_notes": ["..."]}\n'
            "Observed facts must stay close to the evidence. Inferred notes must be clearly reasoned conclusions.\n"
            f"User query: {request.query_text}\n"
            f"Existing direct answer draft: {current_summary or 'none'}\n"
            f"Tool outputs:\n{item_lines}\n"
            f"Repository evidence:\n{repo_citations}\n"
        )

    def _build_repo_context_bundle(self, context: dict[str, object]) -> str:
        survey_summary: SurveySummaryPayload = context["survey_summary"]
        lineage_summary: LineageSummaryPayload = context["lineage_summary"]
        day_one_answers: DayOneAnswersPayload = context["day_one_answers"]
        domain_map: DomainMapPayload = context["domain_map"]
        top_domains = ", ".join(domain.label for domain in domain_map.domains[:5]) or "unclassified"
        day_one_lines = "\n".join(
            f"- {answer.question_text}: {answer.answer_text}"
            for answer in day_one_answers.answers[:5]
        ) or "- none"
        return (
            f"CODEBASE.md excerpt:\n{context['codebase_markdown'][:2400]}\n\n"
            f"onboarding_brief.md excerpt:\n{context['onboarding_markdown'][:1800]}\n\n"
            f"Surveyor summary: modules={survey_summary.module_count}, top_hubs={len(survey_summary.top_hubs)}, "
            f"circular_dependencies={survey_summary.circular_dependency_group_count}\n"
            f"Hydrologist summary: datasets={lineage_summary.dataset_count}, transformations={lineage_summary.transformation_count}, "
            f"edges={lineage_summary.edge_count}\n"
            f"Top inferred domains: {top_domains}\n"
            f"Day-One answers:\n{day_one_lines}\n"
        )

    def _build_repo_context_references(self, context: dict[str, object]) -> list[EvidenceReference]:
        refs: list[EvidenceReference] = []
        day_one_answers: DayOneAnswersPayload = context["day_one_answers"]
        refs.extend(
            reference
            for answer in day_one_answers.answers
            for reference in answer.evidence_references[:2]
            if reference.repository_path not in {".", ""}
        )
        module_graph: GraphPayload = context["module_graph"]
        module_semantics: ModuleSemanticsPayload = context["module_semantics"]
        profile_by_module = {profile.module_id: profile for profile in module_semantics.profiles}
        top_modules = sorted(
            (
                node
                for node in module_graph.nodes
                if isinstance(node, ModuleNode) and node.pagerank_score is not None
            ),
            key=lambda item: (-(item.pagerank_score or 0.0), item.relative_path),
        )[:4]
        for module in top_modules:
            profile = profile_by_module.get(module.node_id or "")
            if profile is not None:
                refs.extend(profile.evidence_references[:2])
            refs.extend(
                evidence_record_to_reference(record, source_kind="module_graph", artifact_path="module_graph.json")
                for record in module.evidence[:1]
            )
        return dedupe_references((reference for reference in refs if reference.repository_path not in {".", ""}), limit=10)

    def _build_repo_context_item(
        self,
        state: NavigatorGraphState,
        *,
        answer_text: str,
        observed_facts: list[str],
        inferred_notes: list[str],
    ) -> NavigatorAnswerItem | None:
        refs = dedupe_references(state.get("repo_context_references", []), limit=6)
        if not answer_text.strip():
            return None
        return NavigatorAnswerItem(
            title="Repository overview",
            answer_text=answer_text.strip(),
            confidence=derive_confidence(refs) if refs else ConfidenceBand.LOW,
            citations=[reference_to_navigator_citation(reference, artifact_reference=reference.artifact_path) for reference in refs],
            observed_facts=observed_facts,
            inferred_notes=inferred_notes,
            warning_codes=[] if refs else ["navigator_repo_summary_without_source_citations"],
        )

    def _repo_observed_facts(self, state: NavigatorGraphState) -> list[str]:
        context = state.get("retrieved_context") or {}
        if not context:
            return ["No retrieved run artifacts were available."]
        survey_summary: SurveySummaryPayload = context["survey_summary"]
        lineage_summary: LineageSummaryPayload = context["lineage_summary"]
        domain_map: DomainMapPayload = context["domain_map"]
        top_domains = ", ".join(domain.label for domain in domain_map.domains[:3]) or "unclassified"
        return [
            f"Surveyor recorded {survey_summary.module_count} modules and {survey_summary.import_edge_count} import edges.",
            f"Hydrologist recorded {lineage_summary.dataset_count} datasets and {lineage_summary.transformation_count} transformations.",
            f"Top inferred domains include {top_domains}.",
        ]

    def _repo_inferred_notes(self, state: NavigatorGraphState) -> list[str]:
        return ["This repository-level answer is synthesized from Archivist, Semanticist, Surveyor, and Hydrologist artifacts."]

    def _deterministic_repo_summary(self, state: NavigatorGraphState) -> str:
        context = state.get("retrieved_context") or {}
        if not context:
            return "No repository context is available for this query."
        domain_map: DomainMapPayload = context["domain_map"]
        top_domains = ", ".join(domain.label for domain in domain_map.domains[:3]) or "shared utilities"
        day_one_answers: DayOneAnswersPayload = context["day_one_answers"]
        leading_answer = day_one_answers.answers[0].answer_text if day_one_answers.answers else "No Day-One summary is available."
        return f"This codebase centers on {top_domains}. {leading_answer}"

    def _last_direct_answer(self, state: NavigatorGraphState) -> str:
        for message in reversed(state.get("messages", [])):
            if isinstance(message, AIMessage) and not message.tool_calls and isinstance(message.content, str):
                return message.content.strip()
        return ""

    def _merge_summary_notes_into_results(
        self,
        items: list[NavigatorAnswerItem],
        synthesis: NavigatorSynthesisPayload | None,
    ) -> list[NavigatorAnswerItem]:
        if synthesis is None or not items:
            return items
        first_item = items[0].model_copy(
            update={
                "observed_facts": synthesis.observed_facts or items[0].observed_facts,
                "inferred_notes": synthesis.inferred_notes or items[0].inferred_notes,
            }
        )
        return [first_item, *items[1:]]

    def _embed_query_text(self, query: str, embedding_model: str | None) -> list[float] | None:
        if not embedding_model or not self.provider.is_available():
            return None
        try:
            result = self.provider.embed_texts(EmbeddingRequest(texts=[query], model=embedding_model))
        except ProviderError:
            return None
        return result.vectors[0] if result.vectors else None

    def _forced_tool_args(self, request: NavigatorRequest) -> dict[str, object]:
        target = self._target_text(request)
        if request.query_type == "trace_lineage":
            return {"dataset": target, "direction": request.direction or "both"}
        if request.query_type == "blast_radius":
            return {"module_path": target}
        if request.query_type == "explain_module":
            return {"path": target}
        return {"concept": target}

    def _parse_synthesis_payload(self, text: str) -> NavigatorSynthesisPayload:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.startswith("json"):
                cleaned = cleaned[4:].strip()
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1:
            cleaned = cleaned[start : end + 1]
        try:
            return NavigatorSynthesisPayload.model_validate(json.loads(cleaned))
        except (ValueError, json.JSONDecodeError):
            return NavigatorSynthesisPayload(summary=text.strip())

    def _tool_method_type(self, tool_name: str) -> str:
        if tool_name == "trace_lineage":
            return "lineage"
        if tool_name == "blast_radius":
            return "graph"
        return "reuse"

    def _format_citations_for_prompt(self, citations: list[NavigatorCitation]) -> list[str]:
        formatted: list[str] = []
        for citation in citations[:4]:
            line = str(citation.line_start) if citation.line_start is not None else "?"
            end = str(citation.line_end) if citation.line_end is not None else line
            formatted.append(f"{citation.source_file}:{line}-{end} ({citation.analysis_method.value}, {citation.trust_label})")
        return formatted

    def _dedupe_citations(self, citations: list[NavigatorCitation]) -> list[NavigatorCitation]:
        seen: set[tuple[str, int | None, int | None, str, str]] = set()
        result: list[NavigatorCitation] = []
        for citation in sorted(
            citations,
            key=lambda item: (item.source_file, item.line_start or 0, item.line_end or 0, item.analysis_method.value, item.trust_label),
        ):
            key = (citation.source_file, citation.line_start, citation.line_end, citation.analysis_method.value, citation.trust_label)
            if key in seen:
                continue
            seen.add(key)
            result.append(citation)
        return result

    def _looks_like_repo_summary_question(self, query_text: str) -> bool:
        lowered = query_text.lower()
        return any(
            marker in lowered
            for marker in (
                "what is this codebase about",
                "what is this repository about",
                "what does this codebase do",
                "what does this repository do",
                "give me an overview",
                "repository overview",
                "codebase overview",
            )
        )

    def _safe_read_text(self, path: Path) -> str:
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8")

    def _truncate_text(self, text: str, token_budget: int) -> str:
        char_budget = max(token_budget * 4, 0)
        if len(text) <= char_budget:
            return text
        return f"{text[:char_budget]}\n...[truncated]"

    @staticmethod
    def _target_text(request: NavigatorRequest) -> str:
        if request.target_identifier:
            return request.target_identifier
        lowered = request.query_text.strip()
        for prefix in ("explain ", "find ", "where is ", "what is ", "trace ", "blast radius of "):
            if lowered.lower().startswith(prefix):
                return lowered[len(prefix):].strip()
        return lowered
