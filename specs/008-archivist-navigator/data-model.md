# Data Model: Archivist and Navigator

## ArchivistArtifactBundle

- **Purpose**: Represents the complete set of final-stage living artifacts for
  one run.
- **Key fields**:
  - `run_id`
  - `analysis_root`
  - `codebase_md_path`
  - `onboarding_brief_path`
  - `lineage_graph_path`
  - `semantic_index_path`
  - `trace_log_path`
  - `reused_artifact_paths`
  - `partial_result_flags`
  - `warning_codes`
- **Relationships**:
  - Aggregates one `CodebaseContextDocument`
  - Aggregates one `OnboardingBrief`
  - Aggregates one `SemanticIndexSnapshot`
  - Aggregates many `TraceEvent` entries
- **Validation rules**:
  - Artifact paths must remain inside project-controlled `.cartography/`
    directories.
  - Reused and regenerated artifact references must be explicit and
    deterministic.

## CodebaseContextDocument

- **Purpose**: Represents the structured content used to render `CODEBASE.md`.
- **Key fields**:
  - `architecture_overview`
  - `critical_path_entries`
  - `data_sources`
  - `data_sinks`
  - `known_debt_entries`
  - `recent_change_velocity_entries`
  - `module_purpose_index`
  - `evidence_references`
  - `is_partial`
- **Relationships**:
  - Consumes Surveyor, Hydrologist, and Semanticist outputs
  - Emits one markdown artifact
- **Validation rules**:
  - Every section must reference one or more evidence sources unless the
    document is explicitly partial.
  - Critical path entries must map back to known modules or stable graph nodes.

## OnboardingBrief

- **Purpose**: Represents the structured content used to render
  `onboarding_brief.md`.
- **Key fields**:
  - `question_sections`
  - `observed_facts`
  - `inferred_conclusions`
  - `evidence_references`
  - `warning_codes`
  - `is_partial`
- **Relationships**:
  - Reuses Semanticist Day-One answers
  - Emits one markdown artifact
- **Validation rules**:
  - All five Day-One questions must be present.
  - Each answer must clearly separate observed facts from inferred conclusions.

## SemanticIndexEntry

- **Purpose**: Represents one indexed semantic retrieval unit.
- **Key fields**:
  - `entry_id`
  - `module_id`
  - `module_path`
  - `purpose_statement`
  - `domain_cluster`
  - `retrieval_tokens`
  - `embedding_vector_ref`
  - `evidence_references`
  - `updated_at`
- **Relationships**:
  - Derived from one semantic module profile
  - Belongs to one `SemanticIndexSnapshot`
- **Validation rules**:
  - `module_path` must map to a real analyzed module.
  - Metadata ordering must remain deterministic for unchanged inputs.

## SemanticIndexSnapshot

- **Purpose**: Captures the semantic index state for one run or reused index.
- **Key fields**:
  - `snapshot_id`
  - `run_id`
  - `commit_hash`
  - `entry_count`
  - `embedding_model`
  - `used_fallback_indexing`
  - `source_module_ids`
  - `warning_codes`
- **Relationships**:
  - Contains many `SemanticIndexEntry` records
  - Supports Navigator retrieval
- **Validation rules**:
  - Snapshot metadata must record whether embeddings were generated, reused, or
    skipped.

## TraceEvent

- **Purpose**: Stores one append-only audit record for Archivist or Navigator.
- **Key fields**:
  - `event_id`
  - `timestamp`
  - `run_id`
  - `agent`
  - `action`
  - `input_summary`
  - `output_summary`
  - `evidence_sources`
  - `confidence`
  - `method_type`
  - `reuse_status`
- **Relationships**:
  - Belongs to one final-stage run
  - May be referenced by one or more `NavigatorResponse` records
- **Validation rules**:
  - Method type must be one of static, graph, lineage, llm, synthesis, or
    reuse.
  - Events must never include excluded secret-bearing content.

## IncrementalBaseline

- **Purpose**: Tracks the baseline required for incremental refresh decisions.
- **Key fields**:
  - `run_id`
  - `commit_hash`
  - `generated_at`
  - `source_files`
  - `upstream_artifact_paths`
  - `dependency_keys`
  - `reusable_artifacts`
- **Relationships**:
  - Supports many `ArchivistArtifactBundle` reuse decisions
  - Feeds incremental invalidation logic
- **Validation rules**:
  - Source file and artifact ordering must be deterministic.
  - Reuse decisions must be explainable through dependency keys or commit
    changes.

## NavigatorRequest

- **Purpose**: Represents one typed Navigator query request.
- **Key fields**:
  - `query_type`
  - `query_text`
  - `target_identifier`
  - `include_inference`
  - `direction`
  - `max_results`
  - `run_id`
- **Relationships**:
  - Produces one `NavigatorResponse`
- **Validation rules**:
  - `query_type` must map to one of the four required tools.
  - `direction` is required only for lineage tracing queries.

## NavigatorState

- **Purpose**: Represents LangGraph state for retrieval-first query execution.
- **Key fields**:
  - `user_query`
  - `chosen_tool`
  - `retrieved_context`
  - `evidence_references`
  - `response_draft`
  - `trust_metadata`
  - `warnings`
- **Relationships**:
  - Wraps one `NavigatorRequest`
  - Produces one `NavigatorResponse`
- **Validation rules**:
  - State transitions must preserve explicit evidence and trust metadata.

## NavigatorCitation

- **Purpose**: Represents one evidence citation attached to a Navigator answer.
- **Key fields**:
  - `source_file`
  - `line_start`
  - `line_end`
  - `analysis_method`
  - `trust_label`
  - `artifact_reference`
- **Relationships**:
  - Belongs to one `NavigatorAnswerItem`
- **Validation rules**:
  - Every citation must indicate whether it comes from direct analysis,
    graph/lineage reasoning, reused artifact evidence, or LLM inference.

## NavigatorAnswerItem

- **Purpose**: Represents one structured result item returned by Navigator.
- **Key fields**:
  - `title`
  - `answer_text`
  - `confidence`
  - `citations`
  - `observed_facts`
  - `inferred_notes`
  - `warning_codes`
- **Relationships**:
  - Belongs to one `NavigatorResponse`
- **Validation rules**:
  - Each answer item must include one or more citations unless the response is
    explicitly partial.

## NavigatorResponse

- **Purpose**: Represents the full structured output of one Navigator query.
- **Key fields**:
  - `request`
  - `summary`
  - `results`
  - `partial_result_flags`
  - `trace_event_ids`
  - `used_model_synthesis`
- **Relationships**:
  - References one `NavigatorRequest`
  - References one or more `TraceEvent` entries
- **Validation rules**:
  - Response ordering must remain deterministic for unchanged artifacts and the
    same query.

## State Transitions

- `SemanticistComplete` -> upstream artifacts are available for final-stage use.
- `ArchivistAuthoring` -> CODEBASE and onboarding brief sections are assembled
  from structured evidence.
- `ArchivistIndexing` -> semantic index entries and optional embeddings are
  generated or reused.
- `ArchivistTracing` -> trace events are appended for all major final-stage
  actions.
- `ArchivistPartial` -> one or more final-stage outputs degrade gracefully, but
  usable artifacts are still written.
- `ArchivistComplete` -> final living artifacts are ready for downstream use.
- `NavigatorClassifying` -> query is classified into one of the four tools.
- `NavigatorRetrieving` -> relevant artifacts and evidence are loaded before
  synthesis.
- `NavigatorExecuting` -> selected tool runs over retrieved context.
- `NavigatorSynthesizing` -> optional synthesis refines the response when
  retrieval alone is insufficient.
- `NavigatorComplete` -> structured response and trace events are available.
