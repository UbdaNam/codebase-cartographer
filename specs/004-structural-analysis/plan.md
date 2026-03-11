# Implementation Plan: Brownfield Cartographer Stage 3 Repository Input Resolution and Structural Analysis

**Branch**: `004-structural-analysis` | **Date**: 2026-03-11 | **Spec**: [spec.md](C:/Abdu/codebase-cartographer/specs/004-structural-analysis/spec.md)
**Input**: Feature specification from `/specs/004-structural-analysis/spec.md`

## Summary

Stage 3 adds two tightly related capabilities: repository input resolution for
local paths and Git URLs, and deterministic multi-language structural
extraction for Surveyor-ready artifacts. The implementation will introduce a
separate repository-preparation layer, a centralized language router for
tree-sitter-backed parsing, typed structural result models aligned to Stage 1
contracts, and deterministic structural artifacts built only from manifest
eligible files.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Pydantic v2, pydantic-settings, Typer, pytest, tree-sitter, git-based repository preparation
**Storage**: Project-controlled filesystem artifacts under `.cartography/`, including prepared repositories, run artifacts, cache, and logs
**Testing**: pytest
**Target Platform**: Local CLI execution on developer workstations and CI-like environments with filesystem access
**Project Type**: CLI application with analyzers, typed contracts, and artifact serialization
**Performance Goals**: Resolve repository input once per run, avoid repeated full-repo scans, analyze only manifest-eligible files, and keep structural artifact ordering deterministic across repeated unchanged runs
**Constraints**: Repositories remain read-only, remote repository preparation uses shallow clone by default, structural extraction excludes manifest-ineligible files, secret contents must never be persisted, and Stage 3 excludes graph algorithms, lineage extraction, LangGraph workflows, and LLM features
**Scale/Scope**: Very large polyglot brownfield repositories with mixed Python, SQL, YAML, JavaScript, TypeScript, JSON config, notebooks, and shell files; primary extraction scope is Python, SQL, YAML, JavaScript, and TypeScript with partial recognition for notebooks and shell files

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Research Gate

- Multi-agent architecture is explicit: Stage 3 feeds the future Surveyor agent
  with repository-preparation outputs, manifest-scoped structural records, and
  deterministic structural artifacts without coupling to Hydrologist,
  Semanticist, Archivist, or Navigator execution.
- Repository-scale performance is addressed: repository preparation reuses
  local working copies where safe, discovery is reused from Stage 2, parsing is
  limited to manifest-eligible files, and parser initialization is kept
  centralized and reusable.
- Scanning boundaries are defined: manifest eligibility remains authoritative,
  excluded and secret-bearing files remain out of scope, root containment stays
  enforced, and prepared repositories are stored only in project-controlled
  locations.
- Multi-language routing is explicit: Python, SQL, YAML, JavaScript, and
  TypeScript receive structural routing; notebooks and shell are recognized as
  partial; unsupported and skipped files remain explicit.
- Evidence model is defined: Stage 3 emits deterministic static-analysis
  artifacts with source paths, line metadata, stable IDs, and typed partial or
  warning outcomes; no graph inference or LLM inference is introduced.
- Degradation behavior is safe: malformed and dynamically difficult files yield
  structured warnings and partial outputs instead of run failure.
- Quality strategy is sufficient: pytest coverage is planned for repository
  preparation, clone reuse, routing, parsing, malformed-file handling, and
  deterministic artifact generation.
- Operation remains non-destructive: target repositories are treated as
  read-only and all clones, cache, logs, and artifacts remain under
  `.cartography`.
- Living-context deliverables remain viable: Stage 3 produces Surveyor-ready
  structural artifacts that can later feed `CODEBASE.md`, `onboarding_brief.md`,
  `lineage_graph.json`, `semantic_index`, and `cartography_trace.jsonl`.
- Cost controls are explicit: Stage 3 uses only static analysis and repository
  preparation logic; no LLM or embedding budget is consumed.

### Post-Design Gate

- PASS: The designed repository-preparation boundary stays separate from
  discovery and structural analysis while returning a local root that later
  stages can reuse.
- PASS: Structural extraction remains manifest-scoped and deterministic, with
  typed results and artifact contracts aligned to Stage 1 models.
- PASS: Remote-repository handling remains shallow-clone-first, reusable, and
  non-destructive.
- PASS: The design preserves future agent composition and central graph
  integration without introducing Stage 4+ behaviors early.

## Project Structure

### Documentation (this feature)

```text
specs/004-structural-analysis/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- structural-analysis-contract.md
`-- tasks.md
```

### Source Code (repository root)

```text
src/
|-- agents/
|-- analyzers/
|   |-- repository_manifest.py
|   `-- tree_sitter_analyzer.py
|-- models/
|   |-- artifacts.py
|   |-- evidence.py
|   |-- graph.py
|   |-- manifest.py
|   |-- repository_input.py
|   `-- structural.py
|-- utils/
|   |-- artifacts.py
|   |-- ids.py
|   |-- ignore_policy.py
|   |-- language_router.py
|   `-- repository_preparation.py
|-- cli.py
|-- config.py
`-- orchestrator.py

tests/
|-- contract/
|-- integration/
`-- unit/
```

**Structure Decision**: Continue the single-project `src/` and `tests/`
layout. Stage 3 adds dedicated repository-preparation and structural-analysis
modules under `src/utils/`, `src/models/`, and `src/analyzers/`, preserving
clean seams between preparation, discovery reuse, parsing, artifact
serialization, and orchestration.

## Phase 0: Research

Research will resolve the concrete design choices that affect safety,
performance, and determinism:

- repository input detection and canonicalization for local paths vs Git URLs
- shallow clone and clone-reuse strategy for prepared repositories
- tree-sitter parser packaging and initialization strategy across target
  languages
- structural extraction boundaries for Python, SQL, YAML, JavaScript, and
  TypeScript
- typed evidence and partial-result representation for parse failures and
  unsupported constructs

## Phase 1: Design & Contracts

### Design Deliverables

- Typed repository input and preparation models
- Typed structural record, file result, and artifact payload models
- Repository preparation contract for local path validation and Git URL reuse
- Structural analysis contract for routing, evidence, warnings, and output
  serialization
- Quickstart scenarios covering local-path and Git-URL analysis flows

### Architectural Decisions

- Repository preparation remains separate from discovery and returns a local
  repository root plus preparation metadata.
- Stage 2 manifest generation remains the canonical in-scope file inventory;
  Stage 3 uses manifest eligibility rather than rescanning the repository in a
  separate incompatible way.
- Language routing is centralized in a dedicated router that maps normalized
  manifest records to parser configuration and extraction capability.
- Structural extraction produces typed static-analysis artifacts only; graph
  construction and ranking stay out of scope.

## Complexity Tracking

No constitution violations are required for this design.
