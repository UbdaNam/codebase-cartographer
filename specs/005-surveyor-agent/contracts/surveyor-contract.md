# Contract: Surveyor Agent

## Purpose

Define the Stage 4 input and output contract for the Surveyor agent so
orchestration, tests, and later graph consumers can rely on deterministic
architectural artifacts.

## Inputs

- **Manifest artifact**: The deterministic repository manifest from Stage 2,
  including in-scope files, support status, skip outcomes, and file identity
  metadata.
- **Structural artifact set**: Stage 3 structural extraction outputs for
  eligible files, including module/file records, imports, symbols, evidence,
  warnings, and partial-result markers.
- **Analysis state**: Run context, artifact paths, warnings, and configuration
  needed to attach Surveyor outputs back to the current run.
- **Configuration values**:
  - recent history lookback window
  - high-velocity core threshold rule
  - maximum graph analytics scope safeguards if needed for bounded execution

## Outputs

- **Module graph artifact**: Deterministic serialized graph payload containing:
  - module nodes
  - module dependency edges
  - graph metadata
  - graph-derived analytics summaries
- **Survey summary artifact**: Deterministic summary containing:
  - module count
  - import edge count
  - top hub list
  - circular dependency group count
  - high-velocity file summary
  - dead code candidate summary
  - structured warning summary
- **Analysis state updates**:
  - artifact references
  - stage statistics
  - partial-result markers
  - warning records

## Behavioral Guarantees

- Surveyor consumes prior artifacts and does not reparse repositories or
  rewalk the full filesystem.
- Surveyor only materializes graph participants for files already in scope from
  prior manifest and structural stages.
- Unresolved imports remain represented explicitly with partial or unresolved
  status instead of being silently dropped.
- Missing git metadata degrades velocity signals and summaries without blocking
  graph construction.
- Dead code results remain heuristic and must never be labeled as certain.
- Serialization order is deterministic for nodes, edges, rankings, and summary
  lists.

## Evidence Boundaries

- Module nodes and dependency edges are backed by static structural evidence
  where available.
- Hub rankings, strongly connected components, and high-velocity core signals
  are graph- or history-derived outputs.
- Dead code candidates are inferential outputs and must include supporting
  evidence or reason codes.

## Error and Partial-Result Contract

- Surveyor emits structured warnings for:
  - missing git metadata
  - unresolved imports
  - partial upstream structural extraction
  - malformed or unsupported upstream module records
- Surveyor may emit partial artifacts as long as deterministic ordering and
  evidence boundaries are preserved.
- Surveyor does not persist secret file contents, raw excluded file contents,
  or repository data outside project-controlled artifact locations.
