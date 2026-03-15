# Implementation Plan: Brownfield Cartographer Phase 4 Archivist and Navigator

**Branch**: `008-archivist-navigator` | **Date**: 2026-03-15 | **Spec**: [spec.md](C:/Abdu/codebase-cartographer/specs/008-archivist-navigator/spec.md)
**Input**: Feature specification from `/specs/008-archivist-navigator/spec.md`

## Summary

Phase 4 adds Archivist as the living-context maintainer and Navigator as the
LangGraph-based query interface over existing Surveyor, Hydrologist, and
Semanticist artifacts. The implementation will generate final human- and
agent-facing artifacts, preserve a traceable audit record, build a semantic
search index, support incremental refresh from repository changes, and expose
four evidence-backed Navigator tools without unnecessarily recomputing upstream
analysis.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Pydantic v2, pydantic-settings, Typer, pytest, NetworkX, existing Surveyor/Hydrologist/Semanticist artifacts, existing `httpx`-backed provider abstraction, LangGraph for Navigator orchestration  
**Storage**: Project-controlled filesystem artifacts under `.cartography/`, including run-scoped outputs, mirrored latest artifacts, semantic index files, trace logs, incremental metadata, and run summaries  
**Testing**: pytest  
**Target Platform**: Local CLI and CI-like environments with filesystem access, optional network access for model-backed synthesis and embeddings, and graceful offline degradation  
**Project Type**: CLI application with staged agents, deterministic artifact builders, LangGraph query orchestration, filesystem-backed indexes, and bounded optional model assistance  
**Performance Goals**: Reuse existing stage artifacts instead of recomputing them, answer Navigator queries from stored artifacts and semantic index before synthesis, keep final artifact ordering deterministic across unchanged runs, and avoid full reruns when unaffected outputs can be reused  
**Constraints**: Target repositories remain read-only; all outputs must remain in `.cartography/`; Navigator must be implemented as a LangGraph agent with exactly four tools; every final artifact and Navigator answer must carry trust and evidence labels; incremental refresh must stay within the prepared analysis root; and model-backed work must remain optional, metered, and bounded  
**Scale/Scope**: Large mixed-language brownfield repositories with hundreds to thousands of modules and datasets, where final-stage artifacts and queries must stay practical for ongoing onboarding, investigation, and AI context injection

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Research Gate

- Multi-agent architecture is explicit: Phase 4 introduces `ArchivistAgent` and
  `NavigatorAgent` as separate responsibilities layered over Surveyor,
  Hydrologist, and Semanticist, preserving the staged artifact contract.
- Repository-scale performance is addressed: Archivist consumes persisted
  artifacts first, incremental refresh is first-class, and Navigator retrieves
  from generated artifacts and semantic index before any optional synthesis.
- Scanning boundaries are defined: prior-stage exclusion policies remain
  authoritative, incremental refresh does not escape the prepared analysis
  root, and outputs stay inside `.cartography/`.
- Multi-language routing is explicit: final-stage behavior relies on upstream
  routing for Python, SQL, YAML, JavaScript/TypeScript, JSON, notebooks, and
  partial or unsupported file classes rather than inventing a new parsing layer.
- Evidence model is defined: final artifacts and query responses distinguish
  static analysis, graph/lineage reasoning, reused artifact evidence, and LLM
  inference, with stable IDs and deterministic ordering.
- Degradation behavior is safe: missing upstream artifacts, insufficient
  evidence, stale citations, unavailable embeddings, provider failure, and
  incremental cache mismatches all yield structured partial results instead of
  run failure.
- Quality strategy is sufficient: pytest coverage is planned for markdown
  artifact generation, trace logging, LangGraph state contracts, query tools,
  incremental invalidation logic, and full-pipeline integration.
- Operation remains non-destructive: analyzed repositories remain read-only and
  all derived files, indexes, logs, and metadata stay in project-controlled
  directories.
- Living-context deliverables remain viable: this phase directly implements
  `CODEBASE.md`, `onboarding_brief.md`, `lineage_graph.json`, `semantic_index`,
  and `cartography_trace.jsonl`.
- Cost controls are explicit: static and graph methods remain primary, provider
  calls are isolated behind existing abstractions, embeddings are cached, and
  synthesis remains optional with deterministic fallback.

### Post-Design Gate

- PASS: Archivist and Navigator remain separate, typed stages that consume
  existing artifacts rather than recomputing upstream analysis.
- PASS: The design preserves deterministic ordering, stable artifact paths,
  evidence labeling, and explicit trust distinctions across all final outputs
  and query responses.
- PASS: Repository-scale performance is supported through artifact reuse,
  semantic-index retrieval, incremental dependency tracking, and retrieval-first
  LangGraph flows.
- PASS: The design keeps the analyzed repository read-only, preserves
  exclusion/root-containment rules, and writes only to `.cartography/`.
- PASS: Optional model-backed work is bounded by existing provider and budget
  abstractions and backed by deterministic fallback paths.

## Project Structure

### Documentation (this feature)

```text
specs/008-archivist-navigator/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   |-- archivist-artifacts-contract.md
|   `-- navigator-query-contract.md
`-- tasks.md
```

### Source Code (repository root)

```text
src/
|-- agents/
|   |-- archivist.py
|   |-- hydrologist.py
|   |-- navigator.py
|   |-- semanticist.py
|   `-- surveyor.py
|-- analyzers/
|   |-- day_one_synthesis.py
|   |-- repository_manifest.py
|   `-- tree_sitter_analyzer.py
|-- index/
|   |-- __init__.py
|   `-- semantic_index.py
|-- llm/
|   |-- budget.py
|   |-- openrouter.py
|   |-- prompts.py
|   `-- provider.py
|-- models/
|   |-- archivist.py
|   |-- evidence.py
|   |-- graph.py
|   |-- manifest.py
|   |-- navigator.py
|   |-- run_metadata.py
|   |-- semantic.py
|   |-- state.py
|   |-- structural.py
|   `-- trace.py
|-- utils/
|   |-- artifacts.py
|   |-- citations.py
|   |-- incremental.py
|   |-- ids.py
|   |-- logging.py
|   `-- trace.py
|-- cli.py
|-- config.py
`-- orchestrator.py

tests/
|-- contract/
|-- integration/
`-- unit/
```

**Structure Decision**: Continue the single-project `src/` and `tests/`
layout. Phase 4 adds Archivist and Navigator agents under `src/agents/`,
portable semantic-index support under `src/index/`, final-stage models under
`src/models/`, and artifact/trace/incremental helpers under `src/utils/`,
while preserving the existing orchestrator and CLI structure.

## Phase 0: Research

Research resolves the final-stage decisions that affect trust, incremental
operation, and LangGraph orchestration:

- how to generate `CODEBASE.md` and `onboarding_brief.md` deterministically
  while still allowing optional model-backed wording assistance
- how to represent a portable filesystem-backed semantic index with cached
  embeddings and retrieval metadata
- how to structure append-only trace records so every major Archivist and
  Navigator action is auditable
- how to model incremental refresh state from git baseline metadata and
  upstream artifact dependencies
- how to implement the required LangGraph workflow so it stays retrieval-first
  and preserves explicit trust metadata

## Phase 1: Design & Contracts

### Design Deliverables

- Typed models for Archivist artifacts, semantic-index entries, trace events,
  incremental baseline metadata, LangGraph Navigator state, Navigator
  requests, citations, and responses
- Archivist artifact contract covering required files, trust labels, reuse
  rules, deterministic ordering, and degradation behavior
- Navigator query contract covering the four mandatory tools, LangGraph state
  flow, response schema, citation requirements, and trust semantics
- Quickstart scenarios covering full-pipeline generation, query flows,
  incremental reruns, and offline/provider-disabled execution

### Architectural Decisions

- Archivist consumes persisted Surveyor, Hydrologist, and Semanticist artifacts
  plus run metadata, and generates final artifacts through deterministic
  section builders rather than open-ended free-form synthesis.
- `CODEBASE.md` and `onboarding_brief.md` are assembled from structured section
  inputs, with optional bounded provider-backed wording only after evidence is
  already collected.
- `semantic_index/` is a portable filesystem-backed index of module-purpose
  records, optional embeddings, retrieval tokens, and trust metadata; it does
  not require a separate database service.
- `cartography_trace.jsonl` is append-only per run and records every major
  Archivist generation step and Navigator tool action with inputs, outputs,
  evidence references, method type, and confidence.
- Incremental refresh uses stored commit hashes, source coverage, and upstream
  artifact references to invalidate only affected final artifacts and query
  support data.
- Navigator is a LangGraph agent with the mandatory stages `classify_query`,
  `retrieve_relevant_artifacts`, `select_tool`, `execute_tool`,
  `synthesize_response`, and `attach_citations_and_trust_metadata`, and it
  prefers retrieval from stored artifacts and semantic index before any model
  synthesis.

## Complexity Tracking

No constitution violations are required for this design.
