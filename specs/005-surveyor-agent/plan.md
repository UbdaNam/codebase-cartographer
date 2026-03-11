# Implementation Plan: Brownfield Cartographer Stage 4 Surveyor Agent

**Branch**: `005-surveyor-agent` | **Date**: 2026-03-11 | **Spec**: [spec.md](C:/Abdu/codebase-cartographer/specs/005-surveyor-agent/spec.md)
**Input**: Feature specification from `/specs/005-surveyor-agent/spec.md`

## Summary

Stage 4 introduces the Surveyor agent as the first architectural intelligence
layer on top of manifest and structural-analysis outputs. The implementation
will consume existing typed artifacts, materialize or update module records,
build a deterministic import graph, compute git velocity and high-velocity core
signals, run graph analytics for hubs and cycles, and serialize stable module
graph and survey summary artifacts for downstream graph and onboarding stages.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Pydantic v2, pydantic-settings, Typer, pytest, NetworkX
**Storage**: Project-controlled filesystem artifacts under `.cartography/`, including manifest, structural outputs, module graph artifacts, survey summaries, cache, and logs
**Testing**: pytest
**Target Platform**: Local CLI execution on developer workstations and CI-like environments with filesystem and optional git metadata access
**Project Type**: CLI application with analyzers, agents, typed contracts, and deterministic artifact serialization
**Performance Goals**: Reuse existing manifest and structural artifacts, avoid repeated full-repository scans, scope git history parsing to a bounded lookback window, and keep graph outputs deterministic across repeated unchanged runs
**Constraints**: Target repositories remain read-only, secret-bearing contents must never be persisted, missing git metadata must degrade gracefully, unresolved imports and partial extraction must remain structured, and Stage 4 excludes lineage semantics, semantic indexing, LangGraph workflows, embeddings, and LLM features
**Scale/Scope**: Very large mixed-language brownfield repositories where supported architectural graph participation primarily comes from Python, JavaScript, and TypeScript modules, while other recognized languages may contribute partial context or remain non-graph participants

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Research Gate

- Multi-agent architecture is explicit: Stage 4 implements `src/agents/surveyor.py`
  as a bounded architectural-analysis agent that consumes Stage 2 and Stage 3
  artifacts and emits Surveyor-ready module graph intelligence without folding
  in Hydrologist, Semanticist, Archivist, or Navigator responsibilities.
- Repository-scale performance is addressed: Surveyor reuses manifest and
  structural outputs instead of reparsing repositories, keeps graph
  construction in memory over in-scope modules only, and bounds git-history
  extraction to a configurable recent window.
- Scanning boundaries are defined: Surveyor does not expand repository scope,
  does not inspect excluded or secret-bearing inputs outside prior stage
  eligibility, and only writes deterministic artifacts to project-controlled
  directories.
- Multi-language routing is explicit: Stage 4 consumes structural outputs from
  existing supported languages and preserves partial or unsupported status
  rather than inventing new parsing behavior.
- Evidence model is defined: module and dependency records remain
  static-analysis-backed where possible, graph analytics are labeled as
  graph-derived, and dead code candidates remain heuristic inferences with
  explicit confidence limits.
- Degradation behavior is safe: missing git metadata, unresolved imports, and
  partial structural extraction yield structured warnings and partial results
  instead of run failure.
- Quality strategy is sufficient: pytest coverage is planned for graph
  construction, git velocity, PageRank, strongly connected components, dead
  code heuristics, deterministic serialization, and missing-metadata paths.
- Operation remains non-destructive: Surveyor reads from repository and prior
  artifacts but does not modify analyzed source files.
- Living-context deliverables remain viable: the module graph and survey
  summaries are direct inputs for later `CODEBASE.md`, onboarding summaries,
  knowledge-graph expansion, and trace artifacts.
- Cost controls are explicit: Stage 4 uses only static analysis, git metadata,
  and graph methods; no LLM or embedding budget is consumed.

### Post-Design Gate

- PASS: Surveyor remains a separate agent layer over structural artifacts and
  does not reimplement Stage 3 parsing or Stage 5+ lineage logic.
- PASS: The design preserves deterministic serialization, stable IDs, explicit
  evidence boundaries, and heuristic labeling for inferential outputs.
- PASS: Git velocity and graph analytics remain bounded, testable, and
  optional when repository history is absent.
- PASS: The design supports large mixed-language repositories without
  introducing repeated repo walks or widening parse scope beyond existing
  manifest eligibility.

## Project Structure

### Documentation (this feature)

```text
specs/005-surveyor-agent/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- surveyor-contract.md
`-- tasks.md
```

### Source Code (repository root)

```text
src/
|-- agents/
|   `-- surveyor.py
|-- analyzers/
|   |-- repository_manifest.py
|   `-- tree_sitter_analyzer.py
|-- graph/
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
layout. Stage 4 adds a dedicated Surveyor agent under `src/agents/`, small
graph-analysis helpers under `src/graph/`, and any supporting typed-model
extensions needed to serialize deterministic module graph intelligence without
collapsing agent, graph, and orchestration concerns into one module.

## Phase 0: Research

Research will resolve the concrete design choices that affect determinism,
bounded performance, and conservative inference:

- mapping Stage 3 structural records into stable `ModuleNode` identities and
  dependency edges
- bounded git-history extraction strategy and graceful degradation when git
  metadata is shallow or absent
- deterministic NetworkX graph construction and serialization strategy
- PageRank and strongly connected component handling for reproducible outputs
- conservative dead code candidate heuristics and confidence labeling

## Phase 1: Design & Contracts

### Design Deliverables

- Typed Surveyor result and summary models
- Module graph contract covering module nodes, dependency edges, analytics
  outputs, velocity signals, and dead code candidates
- Surveyor agent contract for inputs, partial results, warnings, and artifact
  outputs
- Quickstart scenarios covering architectural analysis on repositories with and
  without git history

### Architectural Decisions

- Surveyor consumes typed manifest and structural artifacts from prior stages
  rather than reparsing repositories or rewalking the filesystem.
- Module identifiers are normalized once and reused consistently for module
  nodes, graph node IDs, git velocity attachment, and deterministic artifact
  output.
- Graph analytics are derived from a directed import graph and are serialized
  as graph-derived signals separate from static evidence.
- Dead code candidates remain conservative heuristics that combine structural
  reachability, visibility, and recency signals without claiming proof.

## Complexity Tracking

No constitution violations are required for this design.
