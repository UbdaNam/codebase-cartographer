"""Semanticist agent for semantic understanding over Surveyor and Hydrologist artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import logging

from src.analyzers.day_one_synthesis import DAY_ONE_QUESTIONS, synthesize_day_one_answers
from src.analyzers.documentation_drift import detect_documentation_drift
from src.analyzers.domain_clustering import cluster_profiles
from src.analyzers.semantic_evidence import build_evidence_bundle, extract_documentation_refs
from src.config import AppSettings
from src.llm.budget import BudgetExceededError, ContextWindowBudget
from src.llm.openrouter import OpenRouterProvider
from src.llm.prompts import build_purpose_prompt
from src.llm.provider import ChatRequest, LLMProvider, NullProvider, ProviderError
from src.models.artifacts import SerializationMetadata
from src.models.enums import ConfidenceBand
from src.models.graph import GraphPayload, ModuleNode
from src.models.manifest import RepositoryManifest
from src.models.repository_input import PreparedRepository
from src.models.semantic import (
    DayOneAnswersPayload,
    DocumentationDriftPayload,
    DomainMapPayload,
    ModuleSemanticsPayload,
    SemanticModuleProfile,
    SemanticRunLedger,
)
from src.models.structural import StructuralIndexPayload
from src.utils.logging import log_event


@dataclass(slots=True)
class SemanticistResult:
    module_semantics: ModuleSemanticsPayload
    documentation_drift: DocumentationDriftPayload
    domain_map: DomainMapPayload
    day_one_answers: DayOneAnswersPayload
    ledger: SemanticRunLedger


class SemanticistAgent:
    """Consume Stage 0-5 artifacts and emit Stage 6 semantic artifacts."""

    def __init__(self, settings: AppSettings, provider: LLMProvider | None = None):
        self.settings = settings
        self.provider = provider or self._build_provider()

    def analyze(
        self,
        prepared_repository: PreparedRepository,
        manifest: RepositoryManifest,
        structural_index: StructuralIndexPayload,
        module_graph: GraphPayload,
        lineage_graph: GraphPayload,
        *,
        run_id: str,
        artifact_dir: str,
        logger: logging.Logger | None = None,
    ) -> SemanticistResult:
        del manifest
        repo_root = Path(prepared_repository.local_repo_path)
        metadata = SerializationMetadata(run_id=run_id, artifact_dir=artifact_dir.replace("\\", "/"))
        budget = ContextWindowBudget(
            max_prompt_tokens=self.settings.semantic_max_total_prompt_tokens,
            max_completion_tokens=self.settings.semantic_max_total_completion_tokens,
            max_requests=self.settings.semantic_max_requests_per_run,
        )
        warnings: list[str] = []
        partial_flags: list[str] = []
        profiles: list[SemanticModuleProfile] = []
        drift_records = []
        structural_by_path = {result.file_path: result for result in structural_index.file_results}
        module_nodes = [node for node in module_graph.nodes if isinstance(node, ModuleNode)]
        if logger:
            log_event(logger, event="semanticist_started", run_id=run_id, module_count=len(module_nodes))

        for module in sorted(module_nodes, key=lambda item: item.relative_path):
            structural_result = structural_by_path.get(module.relative_path)
            bundle = build_evidence_bundle(module, structural_result, lineage_graph, repo_root, self.settings)
            purpose_statement, confidence, module_warnings, is_partial = self._generate_purpose(
                bundle,
                budget,
                logger=logger,
            )
            warnings.extend(module_warnings)
            if is_partial:
                partial_flags.append("semantic_purpose_partial")
            profile = SemanticModuleProfile(
                module_id=module.node_id,
                relative_path=module.relative_path,
                language=module.language_or_dialect or "unknown",
                purpose_statement=purpose_statement,
                purpose_confidence=confidence,
                evidence_references=(bundle.code_excerpt_refs + bundle.documentation_refs)[:6],
                source_excerpt_refs=bundle.code_excerpt_refs,
                warning_codes=module_warnings,
                is_partial=is_partial,
                evidence_bundle=bundle,
            )
            source_text = (repo_root / module.relative_path).read_text(encoding="utf-8", errors="replace") if (repo_root / module.relative_path).exists() else ""
            documentation_refs = list(extract_documentation_refs(module.relative_path, source_text, repo_root))
            drift = detect_documentation_drift(profile, documentation_refs)
            if drift is not None:
                drift_records.append(drift)
                profile.doc_drift_status = "drift_detected"
            elif documentation_refs:
                profile.doc_drift_status = "aligned"
            else:
                profile.doc_drift_status = "not_found"
            profiles.append(profile)

        if budget.snapshot.exhausted:
            partial_flags.append("semantic_budget_exhausted")

        domains = cluster_profiles(
            profiles,
            provider=self.provider if self.provider.is_available() else None,
            embedding_model=self.settings.semantic_embedding_model,
            min_clusters=self.settings.semantic_domain_min_clusters,
            max_clusters=self.settings.semantic_domain_max_clusters,
        )
        domain_lookup = {}
        for domain in domains:
            for assignment in domain.assignments:
                domain_lookup[assignment.module_id] = (domain.domain_id, domain.label)
        for profile in profiles:
            domain_id, domain_label = domain_lookup.get(profile.module_id, (None, None))
            profile.domain_id = domain_id
            profile.domain_label = domain_label

        answers, day_one_warnings, day_one_partial = synthesize_day_one_answers(
            prepared_repo_root=repo_root,
            settings=self.settings,
            module_graph=module_graph,
            lineage_graph=lineage_graph,
            profiles=profiles,
            domains=domains,
            provider=self.provider if self.provider.is_available() else None,
            budget=budget,
            logger=logger,
        )
        warnings.extend(day_one_warnings)
        if len(answers) != len(DAY_ONE_QUESTIONS):
            warnings.append("day_one_answer_count_mismatch")
            partial_flags.append("semantic_day_one_partial")
        if day_one_partial:
            partial_flags.append("semantic_day_one_partial")

        ledger = SemanticRunLedger(
            run_id=run_id,
            analyzed_module_count=len(profiles),
            partial_module_count=sum(1 for profile in profiles if profile.is_partial),
            drift_record_count=len(drift_records),
            domain_count=len(domains),
            provider_request_count=budget.snapshot.request_count,
            estimated_prompt_tokens=budget.snapshot.estimated_prompt_tokens,
            estimated_completion_tokens=budget.snapshot.estimated_completion_tokens,
            budget_exhausted=budget.snapshot.exhausted,
            warning_codes=warnings + budget.snapshot.warnings,
        )
        if logger:
            log_event(
                logger,
                event="semanticist_completed",
                run_id=run_id,
                semantic_module_count=len(profiles),
                drift_record_count=len(drift_records),
                domain_count=len(domains),
                day_one_answer_count=len(answers),
            )
        return SemanticistResult(
            module_semantics=ModuleSemanticsPayload(
                metadata=metadata,
                analysis_root=prepared_repository.local_repo_path,
                warnings=warnings,
                partial_result_flags=partial_flags,
                profiles=profiles,
                ledger=ledger,
            ),
            documentation_drift=DocumentationDriftPayload(
                metadata=metadata,
                analysis_root=prepared_repository.local_repo_path,
                warnings=warnings,
                partial_result_flags=partial_flags,
                drift_records=drift_records,
                ledger=ledger,
            ),
            domain_map=DomainMapPayload(
                metadata=metadata,
                analysis_root=prepared_repository.local_repo_path,
                warnings=warnings,
                partial_result_flags=partial_flags,
                domains=domains,
                ledger=ledger,
            ),
            day_one_answers=DayOneAnswersPayload(
                metadata=metadata,
                analysis_root=prepared_repository.local_repo_path,
                warnings=warnings,
                partial_result_flags=partial_flags,
                answers=answers,
                ledger=ledger,
            ),
            ledger=ledger,
        )

    def _generate_purpose(
        self,
        bundle,
        budget: ContextWindowBudget,
        *,
        logger: logging.Logger | None = None,
    ) -> tuple[str, ConfidenceBand, list[str], bool]:
        warnings: list[str] = []
        prompt = build_purpose_prompt(bundle)
        if self.provider.is_available():
            try:
                reserved_prompt_tokens, reserved_completion_tokens = budget.reserve(
                    prompt,
                    min(
                        self.settings.semantic_max_completion_tokens,
                        self.settings.semantic_completion_reserve_tokens,
                    ),
                )
                result = self.provider.generate_text(
                    ChatRequest(
                        prompt=prompt,
                        model=self.settings.semantic_purpose_model,
                        max_output_tokens=self.settings.semantic_max_completion_tokens,
                    )
                )
                budget.record_usage(
                    result.prompt_tokens,
                    result.completion_tokens,
                    reserved_prompt_tokens=reserved_prompt_tokens,
                    reserved_completion_tokens=reserved_completion_tokens,
                )
                if result.text:
                    if logger:
                        log_event(
                            logger,
                            event="semanticist_provider_success",
                            module_path=bundle.module_path,
                            model=result.model or self.settings.semantic_purpose_model,
                            prompt_tokens=result.prompt_tokens,
                            completion_tokens=result.completion_tokens,
                        )
                    return result.text, ConfidenceBand.MEDIUM, warnings, False
            except (ProviderError, BudgetExceededError) as exc:
                if isinstance(exc, BudgetExceededError):
                    warnings.append("semantic_provider_fallback:BudgetExceededError")
                else:
                    warnings.append(f"semantic_provider_fallback:{type(exc).__name__}")
                    detail = str(exc).strip()
                    if detail:
                        warnings.append(f"semantic_provider_detail:{detail[:160]}")
                if logger:
                    log_event(
                        logger,
                        event="semanticist_provider_fallback",
                        module_path=bundle.module_path,
                        error_type=type(exc).__name__,
                        error_detail=str(exc)[:240],
                    )
                return self._heuristic_purpose(bundle), ConfidenceBand.LOW, warnings, True
        warnings.append("semantic_heuristic_purpose")
        return self._heuristic_purpose(bundle), ConfidenceBand.MEDIUM, warnings, False

    def _heuristic_purpose(self, bundle) -> str:
        path = bundle.module_path.lower()
        inputs = bundle.lineage_relationships.get("inputs", [])
        outputs = bundle.lineage_relationships.get("outputs", [])
        public_api = ", ".join(bundle.public_api_signals[:3]) or "its exported entry points"
        if any(token in path for token in ("ingest", "load", "extract")):
            return f"This module handles ingestion work around {public_api}. It exists to bring external or raw inputs into the repository's managed processing flow."
        if outputs and inputs:
            return f"This module transforms {', '.join(inputs[:2])} into {', '.join(outputs[:2])} through {public_api}. It exists to concentrate business processing between upstream ingestion and downstream consumption."
        if any(token in path for token in ("api", "serve", "endpoint", "view")):
            return f"This module serves or exposes behavior through {public_api}. It exists to make processed information available to downstream users, services, or interfaces."
        if any(token in path for token in ("dag", "job", "schedule", "orchestr", "cli")):
            return f"This module coordinates execution through {public_api}. It exists to orchestrate how work is triggered, sequenced, or operated within the codebase."
        return f"This module provides shared application behavior through {public_api}. It exists to support other parts of the system with reusable logic tied to `{bundle.module_path}`."

    def _build_provider(self) -> LLMProvider:
        if not self.settings.semantic_provider_enabled or not self.settings.openrouter_api_key:
            return NullProvider()
        return OpenRouterProvider(
            api_key=self.settings.openrouter_api_key,
            base_url=self.settings.openrouter_base_url,
            app_name=self.settings.openrouter_app_name,
            referer=self.settings.openrouter_referer,
        )
