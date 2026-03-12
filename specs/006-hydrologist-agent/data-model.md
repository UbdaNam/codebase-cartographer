# Data Model: Hydrologist Agent

## HydrologistResult

- **Purpose**: Represents the complete Stage 5 outcome for one analysis run.
- **Key fields**:
  - `run_id`
  - `analysis_root`
  - `lineage_graph_artifact_path`
  - `lineage_summary_artifact_path`
  - `dataset_count`
  - `transformation_count`
  - `edge_count`
  - `sql_signal_count`
  - `python_signal_count`
  - `yaml_signal_count`
  - `warning_count`
  - `partial_result_flags`
- **Relationships**:
  - Aggregates `DatasetNode`, `TransformationNode`, `LineageEdge`, and
    `LineageSignal` records.
- **Validation rules**:
  - Artifact paths must point to project-controlled `.cartography` outputs.
  - Counts must reflect deterministic serialized contents.

## DatasetNode

- **Purpose**: Represents one canonical dataset referenced or materialized by
  in-scope lineage sources.
- **Key fields**:
  - `dataset_id`
  - `canonical_name`
  - `display_name`
  - `namespace`
  - `support_status`
  - `confidence_band`
  - `evidence`
  - `source_kinds`
  - `warnings`
- **Relationships**:
  - Connected to `TransformationNode` through `LineageEdge` records.
- **Validation rules**:
  - `dataset_id` must be stable across repeated runs on unchanged input.
  - Canonical names must collapse equivalent deterministic identifiers.
  - Evidence metadata must preserve source path and lines where available.

## TransformationNode

- **Purpose**: Represents a deterministic transformation step, query, model,
  or data-processing unit that consumes and produces datasets.
- **Key fields**:
  - `transformation_id`
  - `display_name`
  - `module_or_file_id`
  - `language`
  - `transformation_kind`
  - `support_status`
  - `confidence_band`
  - `evidence`
  - `warnings`
- **Relationships**:
  - Consumes upstream `DatasetNode` records and produces downstream
    `DatasetNode` records through `LineageEdge` records.
- **Validation rules**:
  - Transformation IDs must be deterministic from canonical source cues.
  - Partial or weakly inferred transformations must remain explicitly labeled.

## LineageEdge

- **Purpose**: Represents a directed data-flow relationship between a dataset
  and a transformation.
- **Key fields**:
  - `edge_id`
  - `source_id`
  - `target_id`
  - `edge_kind`
  - `analysis_method`
  - `confidence_band`
  - `evidence`
  - `warnings`
- **Relationships**:
  - Connects `DatasetNode -> TransformationNode` for `CONSUMES` and
    `TransformationNode -> DatasetNode` for `PRODUCES`.
- **Validation rules**:
  - `edge_id` must be deterministic from normalized endpoints and edge kind.
  - Evidence and confidence must remain aligned with the originating signal.

## LineageSignal

- **Purpose**: Captures one extracted lineage fact before or alongside graph
  materialization.
- **Key fields**:
  - `signal_id`
  - `signal_source_kind`
  - `language`
  - `source_path`
  - `line_start`
  - `line_end`
  - `raw_identifier`
  - `canonical_identifier`
  - `transformation_hint`
  - `confidence_band`
  - `is_partial`
  - `warnings`
- **Relationships**:
  - May map to one `DatasetNode`, one `TransformationNode`, and one or more
    `LineageEdge` records.
- **Validation rules**:
  - Raw and canonical identifiers must remain distinguishable.
  - Partial signals must retain reason codes or warnings.

## LineageSummary

- **Purpose**: Stores deterministic run-level counts and warning summaries for
  one Hydrologist execution.
- **Key fields**:
  - `dataset_count`
  - `transformation_count`
  - `edge_count`
  - `sql_file_count`
  - `python_file_count`
  - `yaml_file_count`
  - `partial_signal_count`
  - `warning_groups`
- **Relationships**:
  - Summarizes `HydrologistResult` and the serialized lineage graph.
- **Validation rules**:
  - Summary lists and warning groups must be serialized in deterministic order.

## State Transitions

- `SurveyReady` -> manifest, structural artifacts, and module graph outputs are
  available for Hydrologist input.
- `HydrologistExtracting` -> SQL, Python, and YAML lineage signals are being
  collected and normalized.
- `HydrologistPartial` -> one or more extraction sources produced warnings or
  incomplete lineage, but durable artifacts were still emitted.
- `HydrologistComplete` -> deterministic lineage graph and summary artifacts are
  written and registered in analysis state.
