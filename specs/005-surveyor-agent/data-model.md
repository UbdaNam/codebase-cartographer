# Data Model: Surveyor Agent

## SurveyResult

- **Purpose**: Represents the complete Stage 4 outcome for one analysis run.
- **Key fields**:
  - `run_id`
  - `analysis_root`
  - `module_graph_artifact_path`
  - `survey_summary_artifact_path`
  - `module_count`
  - `import_edge_count`
  - `high_velocity_file_count`
  - `high_velocity_core_count`
  - `circular_dependency_group_count`
  - `dead_code_candidate_count`
  - `warnings`
  - `partial_result_flags`
- **Relationships**:
  - Aggregates `ModuleNode`, `ModuleDependency`, `VelocitySignal`,
    `GraphAnalytics`, and `DeadCodeCandidate`.
- **Validation rules**:
  - Artifact paths must point to project-controlled `.cartography` outputs.
  - Counts must reflect deterministic serialized contents.

## ModuleNode

- **Purpose**: Represents a module-level architectural record used in the
  Surveyor graph and downstream knowledge graph stages.
- **Key fields**:
  - `module_id`
  - `path`
  - `language`
  - `support_status`
  - `evidence`
  - `import_targets`
  - `public_symbol_count`
  - `class_count`
  - `function_count`
  - `pagerank_score`
  - `change_velocity_recent`
  - `is_high_velocity_core`
  - `dead_code_candidate`
  - `warnings`
- **Relationships**:
  - Connected to other `ModuleNode` records through `ModuleDependency`.
  - May reference zero or more `VelocitySignal` and `DeadCodeCandidate`
    records.
- **Validation rules**:
  - `module_id` must be stable across repeated runs on unchanged input.
  - Evidence metadata must preserve source path and lines where available.
  - Derived signals must remain optional when upstream inputs are partial.

## ModuleDependency

- **Purpose**: Represents a directed module import or dependency relation.
- **Key fields**:
  - `edge_id`
  - `source_module_id`
  - `target_module_id`
  - `target_display`
  - `resolved`
  - `evidence`
  - `analysis_method`
  - `confidence`
  - `warnings`
- **Relationships**:
  - Connects one `ModuleNode` to another `ModuleNode` or to an unresolved
    external target placeholder.
- **Validation rules**:
  - `edge_id` must be deterministic from normalized source, target, and edge
    kind.
  - Unresolved targets must remain explicit rather than being dropped.

## VelocitySignal

- **Purpose**: Captures recent change-frequency signals for one file or module.
- **Key fields**:
  - `module_id`
  - `path`
  - `lookback_days`
  - `change_count`
  - `included_in_high_velocity_core`
  - `rank`
  - `history_available`
- **Relationships**:
  - Attaches to `ModuleNode`.
- **Validation rules**:
  - `lookback_days` must be recorded with the result.
  - If history is unavailable, the record must either be absent or clearly
    marked partial.

## GraphAnalytics

- **Purpose**: Stores graph-derived architectural signals computed from the
  module import graph.
- **Key fields**:
  - `top_hubs`
  - `pagerank_scores`
  - `strongly_connected_components`
  - `isolated_module_ids`
  - `graph_node_count`
  - `graph_edge_count`
- **Relationships**:
  - Derived from the set of `ModuleNode` and `ModuleDependency` records.
- **Validation rules**:
  - Rankings and component members must be serialized in deterministic order.

## DeadCodeCandidate

- **Purpose**: Represents a conservative heuristic signal that a module may be
  unused or weakly connected.
- **Key fields**:
  - `module_id`
  - `path`
  - `reason_codes`
  - `inbound_dependency_count`
  - `recent_change_count`
  - `visibility_signal`
  - `confidence_band`
  - `evidence`
- **Relationships**:
  - References one `ModuleNode`.
- **Validation rules**:
  - Must remain labeled as heuristic or inferential.
  - Must include supporting signals, not just a boolean outcome.

## State Transitions

- `StructuralReady` -> structural artifacts and manifest are available for
  Surveyor input.
- `Surveying` -> module normalization, graph construction, and history analysis
  are in progress.
- `SurveyPartial` -> one or more substeps produced warnings or skipped derived
  signals, but durable artifacts were still emitted.
- `SurveyComplete` -> deterministic module graph and summary artifacts are
  written and registered in analysis state.
