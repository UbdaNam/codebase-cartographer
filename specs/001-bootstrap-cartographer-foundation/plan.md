# Implementation Plan: Brownfield Cartographer Stage 0 Foundation

**Branch**: `001-bootstrap-cartographer-foundation` | **Date**: 2026-03-10 | **Spec**: [spec.md](c:/Abdu/codebase-cartographer/specs/001-bootstrap-cartographer-foundation/spec.md)
**Input**: Feature specification from `/specs/001-bootstrap-cartographer-foundation/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See
`.specify/templates/plan-template.md` for the execution workflow.

## Summary

Create the Stage 0 foundation for Brownfield Cartographer as a modular,
LangGraph-oriented codebase-intelligence project that is safe for large
brownfield repositories. The plan establishes typed configuration, centralized
ignore and safe-scanning policy, a deterministic repository manifest,
placeholder CLI and orchestration entrypoints, structured logging and run
metadata, `.cartography` artifact conventions, and test scaffolding without
implementing deep parsing, lineage, semantic indexing, or model-driven logic.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: uv, Typer, Pydantic, pytest  
**Storage**: Project-controlled filesystem artifacts under `.cartography/`  
**Testing**: pytest with small fixture repositories  
**Target Platform**: Local developer environments for repository analysis
workflows on Windows, macOS, and Linux  
**Project Type**: CLI-driven library/application foundation for multi-agent
codebase intelligence  
**Performance Goals**: Single-pass repository inventory, deterministic manifest
generation, and bounded scanning suitable for very large mixed-language
repositories  
**Constraints**: Read-only treatment of analyzed repositories, centralized skip
policy before file reads, configurable file-size and total-byte limits, stable
serialized outputs, graceful degradation, and no AST, lineage, graph, embedding,
or LLM execution in Stage 0  
**Scale/Scope**: Brownfield repositories with mixed Python, SQL, YAML,
JavaScript/TypeScript, JSON config, and notebook assets; foundation only, not
full analysis behavior

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Research Gate Review

- PASS: Multi-agent architecture is explicit through a modular `src/` layout
  with separate boundaries for future Surveyor, Hydrologist, Semanticist,
  Archivist, Navigator, analyzers, graph, index, and orchestration concerns.
- PASS: Repository-scale performance is addressed through a single-pass
  manifest abstraction, early ignore enforcement, bounded scan settings, and
  future incremental-analysis hooks.
- PASS: Scanning boundaries are defined through centralized ignore policy,
  secret-sensitive filename patterns, max-size limits, total-byte limits, and
  analysis-root containment.
- PASS: Multi-language routing is explicit through a supported-extensions
  registry and deterministic status classification for supported, partial,
  skipped, and unsupported file types.
- PASS: Evidence and trustworthiness are preserved through deterministic
  manifest records, stable run metadata, structured skip reasons, and explicit
  deferral of graph and LLM inference.
- PASS: Graceful degradation is built into structured skip reasons, bounded
  inventory behavior, and minimal run summaries rather than hard failure on
  unsupported inputs.
- PASS: Testing and developer quality are covered by pytest scaffolding,
  strongly typed settings/models, modular seams, and isolated tests for config,
  ignore rules, manifest behavior, and artifact initialization.
- PASS: Non-destructive operation is preserved by read-only repository
  scanning, `.cartography/` output conventions, and no writes to analyzed
  repositories.
- PASS: Living-context deliverables remain viable because the foundation
  preserves future paths to `CODEBASE.md`, `onboarding_brief.md`,
  `lineage_graph.json`, `semantic_index`, and `cartography_trace.jsonl`.
- PASS: Cost discipline is satisfied because Stage 0 excludes embeddings and
  LLM calls entirely and leaves explicit interface boundaries for future model
  use.

### Post-Design Gate Review

- PASS: Research resolves all technical choices without leaving unresolved
  clarifications.
- PASS: Data model captures manifest, scanning policy, run context, and support
  classification entities needed for deterministic Stage 0 behavior.
- PASS: CLI contract documents only placeholder analyze and query interfaces,
  preserving future growth without overcommitting implementation.
- PASS: Quickstart keeps the workflow within Stage 0 scope and reinforces safe
  boundaries, deterministic outputs, and test-first validation.

## Project Structure

### Documentation (this feature)

```text
specs/001-bootstrap-cartographer-foundation/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- cli-contract.md
|-- checklists/
|   `-- requirements.md
`-- spec.md
```

### Source Code (repository root)

```text
src/
|-- cli.py
|-- orchestrator.py
|-- config.py
|-- constants.py
|-- utils/
|-- models/
|-- analyzers/
|-- agents/
|-- graph/
|-- llm/
`-- index/

tests/
|-- unit/
|-- integration/
|-- fixtures/
`-- contract/

.cartography/
|-- runs/
|-- cache/
`-- logs/
```

**Structure Decision**: Use a single-project `src/` and `tests/` layout with
explicit future-agent and future-analysis boundaries. Reserve `.cartography/`
for project-controlled run metadata, cache, and output artifacts.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | The Stage 0 design satisfies the constitution without exceptions. |
