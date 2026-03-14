# Contract: Archivist Artifacts

## Purpose

Define the final-stage Archivist artifact contract so orchestration, tests,
Navigator, and downstream consumers can rely on deterministic living-context
outputs.

## Inputs

- **Surveyor artifact set**: module graph, PageRank, cycle, velocity, and
  dead-code context.
- **Hydrologist artifact set**: lineage graph, source/sink information, and
  blast-radius-capable lineage context.
- **Semanticist artifact set**: module semantics, domain clustering,
  documentation drift, and Day-One answers.
- **Run metadata**: prior run summary, artifact paths, commit metadata, and
  incremental baseline state.
- **Prepared repository references**: bounded source references for citation
  refresh when needed.
- **Configuration values**:
  - final artifact paths
  - semantic-index settings
  - provider and budget settings
  - incremental refresh rules
  - trace logging policy

## Outputs

- **`CODEBASE.md`** with:
  - architecture overview
  - critical path
  - data sources and sinks
  - known debt
  - recent change velocity
  - module purpose index
- **`onboarding_brief.md`** with:
  - five Day-One answers
  - explicit observed-versus-inferred labeling
  - evidence citations
- **`lineage_graph.json`** preserved for downstream tooling and query reuse
- **`semantic_index/`** containing index metadata, entries, and optional
  embeddings
- **`cartography_trace.jsonl`** as append-only trace output
- **Run-summary updates** for final artifact paths, reuse statistics, warnings,
  and partial-result markers

## Behavioral Guarantees

- Archivist consumes prior-stage artifacts instead of recomputing upstream
  analysis from raw repository content.
- Final artifacts remain deterministic, diffable, and confined to the
  configured analysis root.
- Every major section or answer carries evidence references and trust labels.
- Reuse versus regeneration decisions are recorded explicitly.
- Missing evidence, disabled providers, and invalid reuse candidates yield
  bounded partial artifacts rather than silent failure.

## Artifact Files

- `.cartography/<run>/CODEBASE.md`
- `.cartography/<run>/onboarding_brief.md`
- `.cartography/<run>/lineage_graph.json`
- `.cartography/<run>/semantic_index/`
- `.cartography/<run>/cartography_trace.jsonl`

Optional mirrored latest-run paths may exist under `.cartography/` if they
remain deterministic and project-controlled.

## Error and Partial-Result Contract

- Archivist emits structured warnings for:
  - missing or inconsistent upstream artifacts
  - stale or invalid citation ranges
  - provider or embedding failure
  - incremental reuse invalidation
  - incomplete section evidence
- Archivist must never persist excluded secret-bearing content or unbounded raw
  source text into final-stage artifacts.
