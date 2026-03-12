# Contract: Hydrologist Agent

## Purpose

Define the Stage 5 input and output contract for the Hydrologist agent so
orchestration, tests, and later graph consumers can rely on deterministic data
lineage artifacts.

## Inputs

- **Manifest artifact**: The deterministic repository manifest from Stage 2,
  including in-scope files, support status, skip outcomes, and file identity
  metadata.
- **Structural artifact set**: Stage 3 structural extraction outputs for
  eligible files, including file records, evidence, warnings, and partial-result
  markers.
- **Surveyor artifact set**: Stage 4 module graph and summary outputs used to
  align lineage transformations with module-level architectural context.
- **Analysis state**: Run context, artifact paths, warnings, and configuration
  needed to attach Hydrologist outputs back to the current run.
- **Configuration values**:
  - eligible lineage languages and support statuses
  - dataset normalization rules
  - SQL parsing safeguards and error-handling behavior
  - optional lineage summary thresholds if needed for bounded execution

## Outputs

- **Lineage graph artifact**: Deterministic serialized graph payload containing:
  - dataset nodes
  - transformation nodes
  - lineage edges
  - graph metadata
  - warning and partial-result summaries
- **Lineage summary artifact**: Deterministic summary containing:
  - dataset count
  - transformation count
  - edge count
  - source breakdown by SQL, Python, and YAML lineage signals
  - partial lineage summary
  - structured warning summary
- **Analysis state updates**:
  - artifact references
  - stage statistics
  - partial-result markers
  - warning records

## Behavioral Guarantees

- Hydrologist consumes prior artifacts and does not rewalk the repository or
  bypass manifest eligibility checks.
- Hydrologist only analyzes files already in scope from earlier safe-scanning,
  routing, and structural stages.
- SQL, Python, and YAML lineage signals are normalized before graph insertion so
  duplicate dataset identities are minimized deterministically.
- Malformed SQL, dynamic query generation, and unsupported framework patterns
  degrade to structured warnings and partial outputs instead of blocking graph
  creation.
- Serialization order is deterministic for nodes, edges, summaries, warning
  groups, and any source-specific lineage lists.

## Evidence Boundaries

- SQL parsing, Python data-operation detection, and YAML reference extraction
  are static-analysis evidence sources.
- Dataset and transformation records preserve source path and line metadata
  where available.
- Ambiguous lineage remains explicitly labeled as partial or inferential and is
  not promoted into definitive flow claims.
- This stage does not introduce graph-inference or LLM-derived lineage.

## Error and Partial-Result Contract

- Hydrologist emits structured warnings for:
  - malformed SQL
  - dynamic or weakly inferred Python data operations
  - unsupported or ambiguous YAML pipeline definitions
  - partial upstream structural or Surveyor artifacts
  - dataset normalization conflicts that cannot be resolved deterministically
- Hydrologist may emit partial artifacts as long as deterministic ordering,
  root containment, and evidence boundaries are preserved.
- Hydrologist does not persist secret file contents, raw excluded-file contents,
  or repository data outside project-controlled artifact locations.
