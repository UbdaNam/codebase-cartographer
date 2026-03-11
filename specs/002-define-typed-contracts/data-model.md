# Data Model: Brownfield Cartographer Stage 1 Typed Contracts

## RunContext

**Purpose**: Stable metadata describing a contract-producing or contract-using
analysis run.

**Fields**:
- `run_id`
- `repo_root`
- `artifact_dir`
- `started_at`
- `finished_at`
- `status`
- `warnings`
- `generated_artifact_paths`

**Validation Rules**:
- `run_id` must be deterministic or externally supplied in stable form
- artifact paths must remain within project-controlled output directories
- warnings must support empty defaults

## AnalysisState

**Purpose**: Shared pipeline state for the analysis flow.

**Fields**:
- `run_context`
- `stage_name`
- `stage_stats`
- `skipped_file_summaries`
- `artifact_references`
- `partial_results`
- `errors`

**Validation Rules**:
- state must allow partial and incomplete data
- skipped summaries must preserve support status and skip reasons

## NavigatorState

**Purpose**: Future LangGraph-ready query state for Navigator.

**Fields**:
- `incoming_query`
- `artifact_references`
- `retrieved_evidence`
- `tool_history`
- `working_notes`
- `final_answer`
- `citations`

**Validation Rules**:
- query text must be present
- citations and evidence must support empty defaults
- final answer may be absent until query completion

## EvidenceRecord

**Purpose**: Reusable evidence and citation payload shared by nodes, edges,
artifacts, and query responses.

**Fields**:
- `source_path`
- `line_start`
- `line_end`
- `language`
- `analysis_method`
- `confidence`
- `excerpt`
- `symbol_name`

**Validation Rules**:
- `source_path` is required
- line numbers are optional but must be ordered when both exist
- confidence must use the approved confidence band set

## GraphNode

**Purpose**: Base graph entity with shared identity and evidence fields.

**Fields**:
- `node_id`
- `kind`
- `canonical_name`
- `path`
- `language_or_dialect`
- `metadata`
- `evidence`
- `support_status`
- `confidence`

**Validation Rules**:
- `node_id` must be deterministic from canonical fields
- `kind` must use the approved node kind enum
- support status and confidence may be optional for complete records

## ModuleNode

**Purpose**: Graph node representing a code or configuration module.

**Fields**:
- all base graph node fields
- `relative_path`
- `module_name`

## DatasetNode

**Purpose**: Graph node representing a data source, sink, or named dataset.

**Fields**:
- all base graph node fields
- `dataset_name`
- `platform`
- `namespace`

## TransformationNode

**Purpose**: Graph node representing a transformation or processing step.

**Fields**:
- all base graph node fields
- `transformation_name`
- `operation_type`

## GraphEdge

**Purpose**: Typed relationship connecting two graph nodes.

**Fields**:
- `edge_id`
- `source_node_id`
- `target_node_id`
- `kind`
- `evidence`
- `analysis_method`
- `confidence`
- `metadata`

**Validation Rules**:
- `edge_id` must be deterministic from source, target, and edge kind
- kind must use the approved edge kind enum

## GraphPayload

**Purpose**: Deterministic graph container intended for `.cartography`
serialization.

**Fields**:
- `version`
- `generated_at`
- `run_id`
- `graph_metadata`
- `nodes`
- `edges`

**Validation Rules**:
- nodes and edges must serialize in stable order
- version and run ID must be present

## AnalysisArtifact

**Purpose**: Typed record describing a produced analysis output.

**Fields**:
- `artifact_id`
- `artifact_kind`
- `support_status`
- `analysis_method`
- `evidence`
- `metadata`
- `serialization_path`

**Validation Rules**:
- support status must allow partial and skipped outcomes
- serialization path may be absent until persistence occurs
