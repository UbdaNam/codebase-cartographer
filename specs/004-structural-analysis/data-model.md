# Data Model: Brownfield Cartographer Stage 3 Repository Input Resolution and Structural Analysis

## RepositoryInput

**Purpose**: Represents the user-supplied repository target before preparation.

**Fields**:
- `raw_input`: original CLI or orchestrator input string
- `input_kind`: local path or git URL
- `canonical_identity`: deterministic repository identity for reuse
- `requested_ref`: optional branch, tag, or revision hint

**Validation Rules**:
- Local paths must resolve inside the allowed local filesystem context.
- Git URLs must match supported Git or GitHub URL formats.
- Canonical identity must be deterministic for equivalent inputs.

## PreparedRepository

**Purpose**: Represents the prepared local repository root returned to
downstream discovery and structural analysis.

**Fields**:
- `repository_input`
- `local_repo_path`
- `preparation_status`
- `reuse_mode`
- `prepared_at`
- `source_url`
- `source_ref`
- `warnings`

**Relationships**:
- Produced from one `RepositoryInput`
- Referenced by one `StructuralAnalysisState`

**Validation Rules**:
- `local_repo_path` must be project-controlled for URL-based inputs.
- Prepared repositories must remain read-only from the analyzer's perspective.
- Reuse mode must distinguish fresh clone, reused clone, or refreshed clone.

## StructuralArtifactRecord

**Purpose**: Describes one extracted structural fact from a manifest-eligible
file.

**Fields**:
- `record_id`
- `file_path`
- `language`
- `symbol_kind`
- `symbol_name`
- `container_name`
- `signature`
- `line_start`
- `line_end`
- `analysis_method`
- `support_status`
- `confidence`
- `warnings`

**Relationships**:
- Belongs to one `StructuralFileResult`
- May contain or reference one or more evidence records

**Validation Rules**:
- `record_id` must be deterministic from canonical identifying fields.
- `file_path` must be analysis-root-relative.
- Line metadata may be absent but must be valid when present.

## StructuralFileResult

**Purpose**: Represents the full structural outcome for one manifest record.

**Fields**:
- `file_result_id`
- `manifest_file_id`
- `file_path`
- `language`
- `support_status`
- `parse_status`
- `is_partial`
- `records`
- `warnings`
- `error_code`

**Relationships**:
- Produced from one manifest record
- Contains zero or more `StructuralArtifactRecord` entries

**Validation Rules**:
- Files marked skipped or unsupported by manifest eligibility must not produce
  deep parsed records.
- Partial and failed parses must still preserve structured warnings or error
  details.

## StructuralAnalysisState

**Purpose**: Tracks run-level structural analysis execution.

**Fields**:
- `run_context`
- `prepared_repository`
- `analyzed_file_ids`
- `skipped_file_ids`
- `partial_file_ids`
- `artifact_paths`
- `warning_count`
- `error_count`
- `summary_stats`

**Relationships**:
- References one `PreparedRepository`
- References many `StructuralFileResult` entries

**Validation Rules**:
- Summary stats must reconcile with emitted file results.
- Artifact paths must be deterministic and project-controlled.

## StructuralArtifactPayload

**Purpose**: Durable artifact container for Stage 3 structural outputs.

**Fields**:
- `run_id`
- `prepared_repository_identity`
- `generated_at`
- `artifact_version`
- `records`
- `file_results`
- `summary`

**Validation Rules**:
- Output ordering must be deterministic.
- Payload must not persist raw secret-bearing content.
- Payload must remain compatible with later Surveyor and graph stages.

## State Transitions

- `RepositoryInput` -> `PreparedRepository`: after validation and local-path or
  clone preparation
- `PreparedRepository` -> manifest reuse: after Stage 2 inventory is loaded or
  regenerated consistently
- manifest-eligible file -> `StructuralFileResult`: after routing and parsing
- `StructuralFileResult` collection -> `StructuralArtifactPayload`: after
  deterministic serialization
