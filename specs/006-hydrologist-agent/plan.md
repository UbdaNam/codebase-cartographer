# Implementation Plan: Brownfield Cartographer Stage 5 Hydrologist Agent

**Branch**: `006-hydrologist-agent` | **Date**: 2026-03-12 | **Spec**: [spec.md](C:/Abdu/codebase-cartographer/specs/006-hydrologist-agent/spec.md)
**Input**: Feature specification from `/specs/006-hydrologist-agent/spec.md`

## Summary

Stage 5 introduces the Hydrologist agent as the lineage-intelligence layer on
 top of manifest, structural-analysis, and Surveyor outputs. The implementation
 will consume existing typed artifacts, extract deterministic dataset and
 transformation signals from SQL, embedded SQL in Python, Python data-access
 patterns, and YAML pipeline references, then build and serialize a stable data
 lineage graph and lineage summary for downstream knowledge-graph and onboarding
 stages.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Pydantic v2, pydantic-settings, Typer, pytest, NetworkX, sqlglot
**Storage**: Project-controlled filesystem artifacts under `.cartography/`, including manifest, structural outputs, module graph artifacts, lineage graph artifacts, summaries, cache, and logs
**Testing**: pytest
**Target Platform**: Local CLI execution on developer workstations and CI-like environments with filesystem access and optional prepared-repository state
**Project Type**: CLI application with analyzers, agents, typed contracts, deterministic artifact serialization, and staged graph construction
**Performance Goals**: Reuse manifest, structural, and Surveyor artifacts; restrict lineage scanning to eligible SQL, Python, and YAML files; avoid repeated full-repository scans; keep graph output deterministic across repeated unchanged runs
**Constraints**: Target repositories remain read-only, secret-bearing contents must never be persisted, malformed SQL and dynamic lineage cues must degrade gracefully, lineage must remain evidence-backed, and Stage 5 excludes semantic indexing, LangGraph workflows, embeddings, and LLM features
**Scale/Scope**: Very large mixed-language brownfield repositories where lineage extraction primarily targets SQL, Python, YAML, and dbt-style model inputs while other recognized languages may remain contextual, partial, or non-lineage participants

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Research Gate

- Multi-agent architecture is explicit: Stage 5 implements `src/agents/hydrologist.py`
  as a bounded lineage-analysis agent that consumes prior stage artifacts without
  absorbing Surveyor, Semanticist, Archivist, or Navigator responsibilities.
- Repository-scale performance is addressed: Hydrologist reuses manifest,
  structural, and Surveyor outputs, scopes parsing to eligible SQL, Python, and
  YAML inputs, and avoids repeated full-tree scans.
- Scanning boundaries are defined: lineage extraction only operates on files
  already in scope from prior stages, honors skip and size boundaries, and never
  persists secret-bearing contents into artifacts or logs.
- Multi-language routing is explicit: SQL, Python, YAML, and dbt-style models
  are first-class lineage sources, while partially supported file types remain
  explicit and do not silently widen parser scope.
- Evidence model is defined: dataset and transformation records preserve source
  metadata where available, lineage edges are evidence-backed, and ambiguous
  lineage remains labeled as partial or inferential rather than definitive.
- Degradation behavior is safe: malformed SQL, dynamic query generation,
  unsupported pipeline frameworks, and partial upstream artifacts yield
  structured warnings and partial outputs instead of run failure.
- Quality strategy is sufficient: pytest coverage is planned for SQL lineage,
  Python data-flow detection, YAML reference extraction, dataset normalization,
  lineage graph construction, deterministic serialization, and graceful
  degradation behavior.
- Operation remains non-destructive: Hydrologist reads repository and prior
  artifacts but writes only to project-controlled `.cartography` locations.
- Living-context deliverables remain viable: deterministic lineage graph outputs
  directly support later `lineage_graph.json`, onboarding views, graph expansion,
  and trace artifacts.
- Cost controls are explicit: Stage 5 uses static analysis, config parsing, and
  graph methods only; no LLM or embedding budget is consumed.

### Post-Design Gate

- PASS: Hydrologist remains a separate agent layer over manifest, structural,
  and Surveyor artifacts and does not reimplement repository discovery or Stage
  3 parsing infrastructure.
- PASS: The design preserves deterministic serialization, stable IDs, explicit
  evidence boundaries, and conservative labeling for partial or inferred lineage.
- PASS: SQL, Python, and YAML extraction remain bounded to manifest-eligible
  files and support graceful degradation on malformed, dynamic, or unsupported
  inputs.
- PASS: The design supports large mixed-language repositories without repeated
  repo walks and without broadening scope to semantic indexing, embeddings, or
  LLM-backed reasoning.

## Project Structure

### Documentation (this feature)

```text
specs/006-hydrologist-agent/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- hydrologist-contract.md
`-- tasks.md
```

### Source Code (repository root)

```text
src/
|-- agents/
|   |-- hydrologist.py
|   `-- surveyor.py
|-- analyzers/
|   |-- repository_manifest.py
|   `-- tree_sitter_analyzer.py
|-- graph/
|   |-- lineage.py
|   `-- survey.py
|-- models/
|   |-- artifacts.py
|   |-- evidence.py
|   |-- graph.py
|   |-- manifest.py
|   |-- state.py
|   `-- structural.py
|-- utils/
|   |-- artifacts.py
|   `-- ids.py
|-- cli.py
|-- config.py
`-- orchestrator.py

tests/
|-- contract/
|-- integration/
`-- unit/
```

**Structure Decision**: Continue the single-project `src/` and `tests/`
layout. Stage 5 adds a dedicated Hydrologist agent under `src/agents/`,
lineage-graph helpers under `src/graph/`, and typed-model extensions needed to
serialize deterministic data-lineage intelligence without collapsing analyzer,
agent, graph, and orchestration responsibilities into one module.

## Phase 0: Research

Research will resolve the concrete design choices that affect determinism,
bounded performance, and conservative inference:

- mapping Stage 3 structural and Stage 4 module artifacts into stable lineage
  dataset and transformation identities
- bounded SQL parsing strategy across standalone SQL, embedded SQL strings, and
  dbt-style models
- conservative Python data-operation detection for pandas, Spark, SQLAlchemy,
  and related static call patterns
- YAML pipeline-reference extraction strategy for deterministic dataset signals
- deterministic NetworkX lineage graph construction and serialization strategy

## Phase 1: Design & Contracts

### Design Deliverables

- Typed Hydrologist result and summary models
- Lineage graph contract covering dataset nodes, transformation nodes,
  flow edges, warnings, and partial-result markers
- Hydrologist agent contract for inputs, artifact reuse, evidence boundaries,
  graph outputs, and degraded execution paths
- Quickstart scenarios covering lineage extraction on supported, partial, and
  malformed input combinations

### Architectural Decisions

- Hydrologist consumes typed manifest, structural, and Surveyor artifacts from
  prior stages rather than rewalking the repository or rebuilding parser setup.
- Dataset identifiers are normalized once and reused consistently for graph
  nodes, edge endpoints, summaries, and deterministic artifact output.
- SQL, Python, and YAML extraction are modeled as static-analysis evidence
  sources feeding one directed lineage graph with explicit confidence and
  support-status boundaries.
- Ambiguous or dynamic lineage remains partial and evidence-scoped instead of
  being promoted into definitive dataset-flow claims.

## Complexity Tracking

No constitution violations are required for this design.
