# Implementation Plan: Brownfield Cartographer Stage 1 Typed Contracts

**Branch**: `002-define-typed-contracts` | **Date**: 2026-03-11 | **Spec**: [spec.md](c:/Abdu/codebase-cartographer/specs/002-define-typed-contracts/spec.md)
**Input**: Feature specification from `/specs/002-define-typed-contracts/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See
`.specify/templates/plan-template.md` for the execution workflow.

## Summary

Define the Stage 1 typed contract layer for Brownfield Cartographer so later
agents and pipelines share deterministic, evidence-aware schemas. The plan
covers Pydantic v2 models and enums for graph nodes, graph edges, graph
containers, evidence and citations, analysis artifacts, run and pipeline state,
and future Navigator query state, together with stable ID helpers and tests for
validation, enum behavior, partial data support, and serialization stability.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Pydantic v2, pytest  
**Storage**: Project-controlled filesystem artifacts under `.cartography/`  
**Testing**: pytest for model validation, enum behavior, stable IDs, and
serialization consistency  
**Target Platform**: Local developer environments for deterministic schema and
serialization work on Windows, macOS, and Linux  
**Project Type**: Typed contracts layer under `src/models/` with small
supporting helpers  
**Performance Goals**: Deterministic model validation and serialization for
production-minded contract payloads, with stable IDs and predictable outputs
for large brownfield repository artifacts  
**Constraints**: No AST parsing, SQL lineage extraction, graph algorithms,
LangGraph workflow execution, or LLM summarization; contracts must support
partial results, graceful degradation, mixed-language records, and evidence
metadata without runtime randomness  
**Scale/Scope**: Shared contracts for future Surveyor, Hydrologist,
Semanticist, Archivist, and Navigator stages; Stage 1 defines models only, not
analyzers or workflow engines

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Research Gate Review

- PASS: Multi-agent architecture is explicit because the contract layer is
  shared across Surveyor, Hydrologist, Semanticist, Archivist, and Navigator,
  with separate state models for pipeline flow and future query execution.
- PASS: Repository-scale performance is addressed through deterministic,
  reusable contracts and stable serialization, avoiding stage-specific schema
  rewrites for large repository artifacts.
- PASS: Scanning boundaries are preserved because contracts represent skipped,
  unsupported, and secret-sensitive outcomes without requiring unsafe source
  parsing.
- PASS: Multi-language routing is explicit through support-status fields,
  language or dialect fields where relevant, and mixed-language-safe graph and
  evidence records.
- PASS: Evidence and trustworthiness are central because every reusable contract
  family carries deterministic IDs, method metadata, and evidence-aware fields.
- PASS: Graceful degradation is built into support-status, skip-reason, and
  partial-result representations rather than assuming perfect analysis.
- PASS: Testing and developer quality are covered by pytest validation of
  schemas, enums, IDs, defaults, and serialization stability.
- PASS: Non-destructive operation is preserved because Stage 1 only defines
  contracts and intended `.cartography` output payloads.
- PASS: Living-context deliverables remain viable because graph, artifact,
  evidence, and query-state contracts prepare the path to later onboarding and
  graph outputs.
- PASS: Cost discipline is satisfied because no model-backed execution is in
  scope, only future-facing contract fields.

### Post-Design Gate Review

- PASS: Research resolves the Stage 1 contract choices without unresolved
  clarifications.
- PASS: Data model captures graph, evidence, artifact, and state entities with
  deterministic IDs and partial-result support.
- PASS: Contracts define the public payload surface for future graph and query
  outputs without overcommitting implementation internals.
- PASS: Quickstart stays within Stage 1 scope and validates schema behavior and
  serialization stability without introducing analyzers or workflows.

## Project Structure

### Documentation (this feature)

```text
specs/002-define-typed-contracts/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- model-contracts.md
|-- checklists/
|   `-- requirements.md
`-- spec.md
```

### Source Code (repository root)

```text
src/
|-- models/
|   |-- enums.py
|   |-- evidence.py
|   |-- graph.py
|   |-- artifacts.py
|   |-- state.py
|   `-- __init__.py
`-- utils/
    `-- ids.py

tests/
|-- unit/
|   |-- test_enums.py
|   |-- test_evidence.py
|   |-- test_graph_models.py
|   |-- test_state_models.py
|   `-- test_ids.py
`-- integration/
    `-- test_serialization_contracts.py
```

**Structure Decision**: Keep Stage 1 centered under `src/models/` with a small
ID helper in `src/utils/`. This keeps contract definitions cohesive while
preserving clean seams for later analyzers, orchestrators, and query workflows.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | The Stage 1 design satisfies the constitution without exceptions. |
