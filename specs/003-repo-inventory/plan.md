# Implementation Plan: Brownfield Cartographer Stage 2 Repository Inventory

**Branch**: `003-repo-inventory` | **Date**: 2026-03-11 | **Spec**: [spec.md](c:/Abdu/codebase-cartographer/specs/003-repo-inventory/spec.md)
**Input**: Feature specification from `/specs/003-repo-inventory/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See
`.specify/templates/plan-template.md` for the execution workflow.

## Summary

Strengthen the existing Stage 0 manifest foundation into the production-minded
repository inventory subsystem for Brownfield Cartographer. The plan introduces
a single-pass discovery pipeline, centralized mixed-language classification,
typed inventory outputs and summaries, and Stage 2 analyze-flow integration so
later Surveyor and Hydrologist stages can consume deterministic inventory
artifacts directly.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Pydantic v2, pydantic-settings, Typer, pytest  
**Storage**: Project-controlled filesystem artifacts under `.cartography/`  
**Testing**: pytest with fixture repositories for mixed-language discovery,
skip enforcement, deterministic manifest behavior, and analyzer-facing
inventory outputs  
**Target Platform**: Local developer environments on Windows, macOS, and Linux
for repository discovery and deterministic inventory generation  
**Project Type**: CLI application with typed inventory models, analyzers, and
orchestration support  
**Performance Goals**: One repository walk per inventory run, no unnecessary
content reads for obviously skipped files, stable manifest ordering, and
bounded metadata collection suitable for large polyglot repositories  
**Constraints**: No AST parsing, SQL AST lineage extraction, graph algorithms,
LangGraph workflows, or LLM summarization; traversal must remain inside the
analysis root; secret-bearing contents must never be persisted into logs or
artifacts; repeated full-tree scans must be avoided  
**Scale/Scope**: Very large mixed-language brownfield repositories, including
repositories with the size and messiness of Apache Airflow examples and larger;
Stage 2 covers discovery, classification, manifest generation, summary
serialization, and analyze-path integration only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Research Gate Review

- PASS: Multi-agent architecture is explicit because Stage 2 produces the
  shared repository inventory surface consumed later by Surveyor, Hydrologist,
  Semanticist, Archivist, and Navigator-backed workflows.
- PASS: Repository-scale performance is central because the design requires a
  single discovery pass, bounded metadata collection, skip-first evaluation,
  and future-ready incremental metadata.
- PASS: Scanning boundaries are explicit because analysis-root containment,
  exclusion rules, secret handling, size thresholds, and structured skip
  reasons are required before content parsing.
- PASS: Multi-language routing is explicit because Python, SQL, YAML,
  JavaScript, TypeScript, JSON configuration, notebooks, and shell files
  receive deterministic normalized language labels and support-status outcomes.
- PASS: Evidence and trustworthiness are preserved because Stage 2 outputs are
  inventory-derived, deterministic, path-grounded artifacts rather than graph
  or LLM inferences.
- PASS: Graceful degradation is built in through structured skipped,
  unsupported, and partially supported outcomes rather than brittle failure.
- PASS: Testing and developer quality are addressed by pytest fixture coverage
  for mixed-language discovery, skip enforcement, large-repo-like conditions,
  and stable output behavior.
- PASS: Operation remains non-destructive because target repositories stay
  read-only and all outputs remain within `.cartography`.
- PASS: Living-context deliverables remain viable because the repository
  inventory becomes the stable input layer for future module graphs, lineage
  graphs, and onboarding artifacts.
- PASS: Cost discipline is satisfied because no model-backed execution is in
  scope and discovery relies on static filesystem and metadata operations only.

### Post-Design Gate Review

- PASS: Research resolves the Stage 2 design choices without unresolved
  clarifications.
- PASS: Data model defines inventory records, summaries, and classification
  decisions with deterministic and analyzer-ready fields.
- PASS: Contracts define the Stage 2 public inventory surface for CLI and
  orchestrator consumers without overreaching into parsing or graph logic.
- PASS: Quickstart validates discovery, classification, deterministic
  serialization, and Stage 2 analyze-flow behavior while preserving the narrow
  scope of this stage.

## Project Structure

### Documentation (this feature)

```text
specs/003-repo-inventory/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- inventory-contract.md
|-- checklists/
|   `-- requirements.md
`-- spec.md
```

### Source Code (repository root)

```text
src/
|-- analyzers/
|   `-- repository_manifest.py
|-- models/
|   |-- manifest.py
|   |-- artifacts.py
|   `-- state.py
|-- utils/
|   |-- file_classification.py
|   |-- ignore_policy.py
|   `-- artifacts.py
|-- cli.py
|-- config.py
`-- orchestrator.py

tests/
|-- fixtures/
|   |-- sample_repo/
|   |-- secret_repo/
|   `-- inventory_polyglot_repo/
|-- integration/
|   |-- test_safe_scan_manifest.py
|   `-- test_stage0_run_summary.py
`-- unit/
    |-- test_file_classification.py
    |-- test_ignore_policy.py
    `-- test_repository_manifest.py
```

**Structure Decision**: Build Stage 2 on top of the existing Stage 0
foundation instead of introducing a new subsystem tree. Discovery, path
filtering, and classification stay separated across `src/analyzers/` and
`src/utils/`, while typed inventory records remain under `src/models/` so later
analyzers and orchestrators can consume a stable shared manifest surface.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | The Stage 2 design satisfies the constitution without exceptions. |
