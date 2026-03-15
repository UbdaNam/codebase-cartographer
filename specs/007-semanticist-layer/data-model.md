# Data Model: Semanticist Agent

## SemanticModuleProfile

- **Purpose**: Represents the semantic understanding for one eligible module.
- **Key fields**:
  - `module_id`
  - `relative_path`
  - `language`
  - `purpose_statement`
  - `purpose_confidence`
  - `domain_id`
  - `domain_label`
  - `evidence_references`
  - `source_excerpt_refs`
  - `doc_drift_status`
  - `warning_codes`
  - `is_partial`
- **Relationships**:
  - References one `PurposeEvidenceBundle`
  - May link to zero or more `DocumentationDriftRecord` entries
  - Belongs to one `DomainCluster`
- **Validation rules**:
  - `module_id` and `relative_path` must map to an existing Surveyor module
    node.
  - `purpose_statement` must be 2-3 sentences unless the profile is marked
    partial.
  - Purpose text must not substantially duplicate documentation snippets beyond
    bounded evidence quotes.

## PurposeEvidenceBundle

- **Purpose**: Captures the observed facts used to generate one module's purpose
  statement.
- **Key fields**:
  - `bundle_id`
  - `module_id`
  - `module_path`
  - `imports`
  - `public_api_signals`
  - `graph_metrics`
  - `lineage_relationships`
  - `git_velocity_signals`
  - `code_excerpt_refs`
  - `documentation_refs`
  - `analysis_methods`
- **Relationships**:
  - Produces one or more `EvidenceReference` records
  - Feeds one `SemanticModuleProfile`
- **Validation rules**:
  - Documentation references may appear in the bundle for drift comparison but
    must not be the sole evidence supporting a purpose statement.
  - Code excerpts must be bounded and refer to real prepared-repository files.

## DocumentationDriftRecord

- **Purpose**: Stores a likely mismatch between current implementation behavior
  and nearby documentation.
- **Key fields**:
  - `drift_id`
  - `module_id`
  - `module_path`
  - `observed_documentation`
  - `inferred_purpose`
  - `drift_type`
  - `confidence`
  - `evidence_references`
  - `is_partial`
  - `warning_codes`
- **Relationships**:
  - Belongs to one `SemanticModuleProfile`
  - May contribute to one or more `DayOneAnswer` evidence sets
- **Validation rules**:
  - `drift_type` must be one of contradiction, omission, outdated, or
    insufficient_evidence.
  - Low-confidence or provider-fallback cases must remain explicitly labeled.

## DomainCluster

- **Purpose**: Represents one inferred business or architectural domain.
- **Key fields**:
  - `domain_id`
  - `label`
  - `summary`
  - `confidence`
  - `module_ids`
  - `primary_signals`
  - `is_partial`
- **Relationships**:
  - Groups many `SemanticModuleProfile` records
  - Contributes to Day-One answers about business-logic concentration
- **Validation rules**:
  - Domain labels must be human-readable and stable for unchanged inputs.
  - Module membership ordering must be deterministic.

## DomainAssignment

- **Purpose**: Records the mapping between one module and its inferred domain.
- **Key fields**:
  - `module_id`
  - `domain_id`
  - `assignment_confidence`
  - `assignment_signals`
- **Relationships**:
  - Joins `SemanticModuleProfile` to `DomainCluster`
- **Validation rules**:
  - Every eligible semantic module must either have a domain assignment or a
    structured partial-warning reason.

## DayOneAnswer

- **Purpose**: Represents one answer to an FDE Day-One question.
- **Key fields**:
  - `question_id`
  - `question_text`
  - `answer_text`
  - `confidence`
  - `evidence_references`
  - `supporting_module_ids`
  - `supporting_dataset_ids`
  - `is_partial`
  - `warning_codes`
- **Relationships**:
  - Aggregates evidence from `SemanticModuleProfile`, `DomainCluster`,
    Surveyor, and Hydrologist artifacts
- **Validation rules**:
  - All five required questions must be present.
  - If an answer cannot be completed confidently, `is_partial` must be true and
    evidence must explain the gap.

## SemanticRunLedger

- **Purpose**: Captures stage-level Semanticist execution accounting and
  metering.
- **Key fields**:
  - `run_id`
  - `analyzed_module_count`
  - `partial_module_count`
  - `drift_record_count`
  - `domain_count`
  - `provider_request_count`
  - `estimated_prompt_tokens`
  - `estimated_completion_tokens`
  - `budget_exhausted`
  - `warning_codes`
- **Relationships**:
  - Summarizes one full Semanticist run and links to the semantic artifacts
- **Validation rules**:
  - Budget and request counts must be non-negative and deterministic for a
    fixed run path.

## EvidenceReference

- **Purpose**: Points to a concrete supporting source for a semantic claim.
- **Key fields**:
  - `reference_id`
  - `source_kind`
  - `artifact_path`
  - `repository_path`
  - `line_start`
  - `line_end`
  - `quoted_text`
  - `observed_or_inferred`
- **Relationships**:
  - May be attached to profiles, drift findings, domain clusters, and Day-One
    answers
- **Validation rules**:
  - Evidence must indicate whether it is directly observed, graph-derived, or
    inferred.
  - Quoted text must remain bounded and must not expose excluded secret content.

## State Transitions

- `HydrologistComplete` -> manifest, structural, module graph, and lineage
  artifacts are available for Semanticist input.
- `SemanticistBundling` -> evidence bundles are assembled per eligible module.
- `SemanticistPurposing` -> purpose statements and drift comparisons are
  generated with budget tracking and partial-result handling.
- `SemanticistClustering` -> modules are grouped into inferred domains using
  embeddings when available or deterministic fallbacks when not.
- `SemanticistSynthesis` -> the five Day-One answers are produced from all
  available evidence.
- `SemanticistPartial` -> one or more semantic substeps degraded gracefully, but
  durable artifacts were still written.
- `SemanticistComplete` -> semantic artifacts, summaries, and run-state updates
  are persisted for downstream Archivist consumption.
