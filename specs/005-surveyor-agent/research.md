# Research: Surveyor Agent

## Decision: Reuse structural artifacts as the sole Surveyor source of code structure

**Rationale**: Stage 4 must consume Stage 3 outputs instead of rebuilding
parser infrastructure. This keeps architecture boundaries clean, avoids
repeated parse work, and preserves deterministic upstream evidence.

**Alternatives considered**:
- Reparse source files inside Surveyor: rejected because it duplicates Stage 3
  responsibilities and violates bounded-work expectations.
- Build graph edges directly from raw files without structural artifacts:
  rejected because it weakens evidence traceability and reintroduces
  language-specific logic in the wrong stage.

## Decision: Use normalized module identifiers derived from existing structural identity fields

**Rationale**: Surveyor needs one stable identifier shared by module nodes,
graph nodes, velocity attachment, and artifact serialization. Reusing a
canonical module identity avoids drift between graph analytics and stored
module records.

**Alternatives considered**:
- Use raw file paths everywhere: rejected because import targets and logical
  modules may require normalized forms beyond path strings.
- Use runtime-random graph node IDs: rejected because deterministic artifacts
  and stable diffs are constitutional requirements.

## Decision: Bound git velocity to a configurable recent lookback window and degrade to partial results when git is unavailable

**Rationale**: Surveyor needs actionable change-frequency signals without
turning git-history analysis into an unbounded scan. A bounded window aligns
with performance requirements and missing metadata should not block the stage.

**Alternatives considered**:
- Parse full repository history every run: rejected because it is unbounded and
  unnecessary for onboarding-oriented recency signals.
- Treat missing git metadata as a hard error: rejected because brownfield runs
  must degrade gracefully.

## Decision: Build a directed import graph and serialize sorted derived analytics separately from static evidence

**Rationale**: PageRank, strongly connected components, and dependency-based
dead code heuristics all depend on directed module relationships. Keeping
graph-derived outputs explicitly separate from static structural evidence makes
trust boundaries clear.

**Alternatives considered**:
- Store only adjacency lists without graph analytics: rejected because Stage 4
  explicitly requires hub and circular-dependency signals.
- Merge graph-derived ranks directly into structural evidence records as if
  they were static facts: rejected because it obscures evidence provenance.

## Decision: Keep dead code detection conservative and explicitly heuristic

**Rationale**: Stage 4 has only structural reachability and recent-change
signals, so dead code detection must remain advisory. Conservative heuristics
reduce false certainty while still surfacing useful review candidates.

**Alternatives considered**:
- Omit dead code candidates entirely: rejected because the stage requires an
  initial heuristic signal.
- Treat zero inbound imports as definitive dead code: rejected because dynamic
  frameworks, entrypoints, and external invocations would create false
  positives.
