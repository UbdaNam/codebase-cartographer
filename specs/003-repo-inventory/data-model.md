# Data Model: Brownfield Cartographer Stage 2 Repository Inventory

## InventoryRecord

**Purpose**: Stable per-file inventory record produced by repository discovery
and classification.

**Fields**:
- `relative_path`
- `file_id`
- `size_bytes`
- `modified_time`
- `extension`
- `language`
- `support_status`
- `skip_reason`
- `is_parse_eligible`
- `digest`
- `digest_strategy`
- `classification_source`
- `notes`

**Validation Rules**:
- `relative_path` must remain analysis-root-relative and use deterministic path
  normalization
- `file_id` must be stable from canonical path identity rather than runtime
  randomness
- `skip_reason` must be present when a record is skipped
- `is_parse_eligible` must be false for skipped and unsupported records
- `digest` may be absent when `digest_strategy` indicates deferred or bounded
  hashing

## ClassificationDecision

**Purpose**: Structured routing result for a discovered path.

**Fields**:
- `language`
- `support_status`
- `classification_source`
- `is_parse_eligible`
- `notes`

**Validation Rules**:
- `language` must use the normalized routing label for the file class
- `support_status` must be one of supported, partial, skipped, or unsupported
- `classification_source` must identify the rule family that determined the
  result

## ScanPolicyDecision

**Purpose**: Structured safety and exclusion result evaluated before parse
eligibility.

**Fields**:
- `path`
- `action`
- `reason_code`
- `matched_rule`
- `is_secret_sensitive`
- `size_bytes`

**Validation Rules**:
- `reason_code` must use the approved skip-reason enum set
- secret-sensitive outcomes must not include persisted secret contents
- root-escape outcomes must remain structured and inspectable

## RepositoryManifest

**Purpose**: Deterministic inventory artifact containing ordered file records
for the full analysis root.

**Fields**:
- `records`
- `summary`

**Validation Rules**:
- records must serialize in stable order
- summary counts must reconcile with record statuses

## InventorySummary

**Purpose**: Lightweight aggregate view of repository inventory outcomes.

**Fields**:
- `total_candidates`
- `supported_count`
- `partial_count`
- `unsupported_count`
- `skipped_count`
- `bytes_considered`
- `bytes_scanned`
- `parse_eligible_count`

**Validation Rules**:
- counts must match manifest record totals
- `bytes_scanned` must remain bounded by configured scan limits
- parse-eligible count must exclude skipped and unsupported records

## InventoryArtifact

**Purpose**: Serialized repository inventory output written to
`.cartography` for later orchestrator and analyzer consumption.

**Fields**:
- `run_id`
- `manifest_path`
- `summary_path`
- `generated_at`
- `repo_root`

**Validation Rules**:
- artifact paths must remain in project-controlled output directories
- artifact references must be stable and deterministic for the same run output

## Relationships

- `RepositoryManifest` contains many `InventoryRecord` entries.
- `RepositoryManifest` contains one `InventorySummary`.
- Each `InventoryRecord` is informed by one effective `ClassificationDecision`
  and one effective `ScanPolicyDecision`.
- `InventoryArtifact` references the persisted `RepositoryManifest` and
  `InventorySummary` outputs for a run.
