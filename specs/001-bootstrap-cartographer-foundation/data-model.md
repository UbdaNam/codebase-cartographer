# Data Model: Brownfield Cartographer Stage 0 Foundation

## RepositorySettings

**Purpose**: Central runtime configuration for repository scanning and artifact
placement.

**Fields**:
- `repo_root`: absolute path to the analysis root
- `artifact_dir`: absolute or repo-relative `.cartography` root
- `max_file_size_bytes`: per-file read limit
- `max_total_bytes_scanned`: total scan budget
- `supported_extensions`: mapping of extensions to language and support status
- `ignore_patterns`: directory and filename exclusion patterns
- `secret_sensitive_patterns`: filename patterns such as `.env` and `.env.*`
- `concurrency_limit`: future concurrency control placeholder
- `cache_enabled`: future cache toggle placeholder
- `cache_dir`: project-controlled cache location

**Validation Rules**:
- `repo_root` must resolve inside the intended analysis root
- byte limits must be positive integers
- artifact and cache directories must remain project-controlled
- supported-extension entries must map to deterministic support-status labels

## ScanPolicyDecision

**Purpose**: Structured result returned before file contents are read.

**Fields**:
- `path`: relative path under the analysis root
- `action`: include or skip
- `reason_code`: structured skip reason or inclusion reason
- `matched_rule`: policy rule that produced the decision
- `is_secret_sensitive`: boolean flag for sensitive filename matches
- `size_bytes`: file size when available

**Validation Rules**:
- skipped files must always include a `reason_code`
- decisions must be deterministic for the same path and metadata inputs

## ManifestRecord

**Purpose**: Single inventory entry for a candidate repository file.

**Fields**:
- `relative_path`: normalized repository-relative path
- `size_bytes`: file size
- `modified_time`: last modified timestamp
- `digest`: placeholder or hash strategy output
- `language`: classified language or file family
- `support_status`: supported, partial, skipped, or unsupported
- `skip_reason`: optional structured reason for skipped files
- `classification_source`: registry or rule source used for classification

**Validation Rules**:
- `relative_path` must be unique within a manifest
- `support_status` must come from the approved status set
- skipped records must include `skip_reason`
- manifest serialization must be stable and path-ordered

## ManifestSummary

**Purpose**: Deterministic summary of a repository inventory run.

**Fields**:
- `total_candidates`
- `supported_count`
- `partial_count`
- `unsupported_count`
- `skipped_count`
- `bytes_considered`
- `bytes_scanned`

**Validation Rules**:
- summary counts must reconcile with manifest records
- byte totals must not exceed configured scan budgets

## RunContext

**Purpose**: Metadata describing a Stage 0 execution.

**Fields**:
- `run_id`: stable unique identifier for the run
- `started_at`: run start timestamp
- `finished_at`: optional run finish timestamp
- `branch`: current feature or runtime branch label
- `repo_root`: analysis root
- `artifact_root`: `.cartography` location
- `status`: running, completed, partial, or failed
- `summary_path`: path to the run summary artifact

**Validation Rules**:
- `run_id` must be unique per run
- `artifact_root` must stay within project-controlled output directories
- `status` transitions must be monotonic from running to terminal state

## AgentBoundary

**Purpose**: Declared future ownership seam for a major subsystem.

**Fields**:
- `name`: Surveyor, Hydrologist, Semanticist, Archivist, Navigator, or shared
  subsystem
- `responsibility`: concise description of intended scope
- `input_contracts`: upstream artifacts or messages consumed
- `output_contracts`: artifacts or messages produced
- `status`: placeholder or implemented

**Relationships**:
- future analyzers feed shared manifest and typed records
- orchestrator coordinates agent boundaries but does not own analyzer logic
- graph, index, and llm layers remain downstream extension seams in Stage 0
