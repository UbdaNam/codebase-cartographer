# Implementation Plan: Brownfield Cartographer Stage 6 Semanticist Agent

**Branch**: `007-semanticist-layer` | **Date**: 2026-03-14 | **Spec**: [spec.md](C:/Abdu/codebase-cartographer/specs/007-semanticist-layer/spec.md)
**Input**: Feature specification from `/specs/007-semanticist-layer/spec.md`

## Summary

Stage 6 adds the Semanticist agent as the semantic-intelligence layer over the
existing manifest, structural, Surveyor, and Hydrologist artifacts. The
implementation will build evidence bundles per module, generate grounded module
purpose statements, detect documentation drift, infer business-domain
boundaries, and synthesize the five FDE Day-One answers into deterministic
semantic artifacts that downstream Archivist flows can consume directly.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Pydantic v2, pydantic-settings, Typer, pytest, NetworkX, tree-sitter artifacts from Stage 3, sqlglot lineage artifacts from Stage 5, `httpx` for provider transport, optional OpenRouter-backed chat and embedding models
**Storage**: Project-controlled filesystem artifacts under `.cartography/`, including manifest, structural outputs, module graph artifacts, lineage graph artifacts, semantic artifacts, run summaries, cache, and logs
**Testing**: pytest
**Target Platform**: Local CLI execution and CI-like environments with filesystem access, optional network access for model providers, and graceful offline degradation
**Project Type**: CLI application with staged agents, analyzers, typed contracts, graph artifacts, and bounded model-assisted semantic analysis
**Performance Goals**: Reuse prior stage artifacts without rewalking the repository, bound raw-source loading to semantic-eligible modules, support chunked summarization for large modules, keep artifact ordering deterministic across unchanged runs, and meter model usage so bulk module analysis stays within explicit per-run budgets
**Constraints**: Target repositories remain read-only; secret-bearing content must never be persisted; semantic outputs must distinguish direct evidence from inferred conclusions; documentation text must not be copied verbatim except short evidence snippets; model-backed work must have a static fallback; and failures in purpose generation, drift detection, clustering, or synthesis must degrade to partial artifacts rather than fail the run
**Scale/Scope**: Very large mixed-language brownfield repositories with hundreds to thousands of modules, where Semanticist focuses on module-level business understanding, documentation drift, domain inference, and repository-level Day-One answers using Stage 0-5 artifacts plus bounded raw-source access

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Research Gate

- Multi-agent architecture is explicit: Stage 6 introduces `src/agents/semanticist.py`
  and related semantic contracts without collapsing Surveyor, Hydrologist,
  Archivist, or future Navigator responsibilities.
- Repository-scale performance is addressed: Semanticist consumes persisted
  artifacts first, loads raw module source lazily, chunks only oversized
  modules, and meters all model-backed work.
- Scanning boundaries are defined: earlier-stage exclusions remain authoritative,
  source loading stays inside the prepared repository root, and secret-bearing
  or excluded files never become semantic inputs.
- Multi-language routing is explicit: Python, SQL, YAML, JavaScript/TypeScript,
  JSON, notebooks, and other file types contribute only through approved prior
  artifacts or direct module-source evidence routes; unsupported inputs remain
  explicit and do not silently widen the scope.
- Evidence model is defined: outputs separate direct observations from graph
  inference and LLM inference, preserve source references, and require
  deterministic artifact ordering and stable IDs.
- Degradation behavior is safe: provider outages, token-budget exhaustion,
  missing embeddings, weak documentation signals, and partial upstream artifacts
  yield structured warnings and partial outputs instead of run failure.
- Quality strategy is sufficient: pytest coverage is planned for evidence bundle
  construction, purpose grounding, drift classification, clustering,
  synthesizer contracts, provider budgeting, serialization, and integration
  across full pipeline outputs.
- Operation remains non-destructive: Semanticist reads prepared repositories and
  prior artifacts but writes only to project-controlled `.cartography` paths.
- Living-context deliverables remain viable: semantic artifacts are structured
  for direct Archivist consumption and preserve the path toward `CODEBASE.md`,
  `onboarding_brief.md`, semantic indexing, and trace artifacts.
- Cost controls are explicit: model usage is isolated behind provider and budget
  abstractions, bulk module purpose generation uses a lower-cost tier, stronger
  models are reserved for final synthesis, and static fallbacks remain
  available.

### Post-Design Gate

- PASS: Semanticist remains a distinct stage over Stage 0-5 artifacts with
  clearly bounded responsibilities and explicit downstream contracts.
- PASS: The design preserves deterministic serialization, stable IDs, evidence
  labeling, and structured partial-result behavior for all semantic artifacts.
- PASS: Repository-scale behavior is maintained by reusing persisted artifacts,
  lazily reading module source, chunking only large modules, and tracking model
  budgets explicitly.
- PASS: The design keeps analyzed repositories read-only, honors exclusion and
  secret-handling rules, and writes only to project-controlled artifact paths.
- PASS: Model-backed work is bounded, metered, and backed by fallback paths for
  purpose generation, drift detection, clustering, and Day-One synthesis.

## Project Structure

### Documentation (this feature)

```text
specs/007-semanticist-layer/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- semanticist-contract.md
`-- tasks.md
```

### Source Code (repository root)

```text
src/
|-- agents/
|   |-- hydrologist.py
|   |-- semanticist.py
|   `-- surveyor.py
|-- analyzers/
|   |-- repository_manifest.py
|   `-- tree_sitter_analyzer.py
|-- graph/
|   |-- lineage.py
|   `-- survey.py
|-- llm/
|   |-- __init__.py
|   |-- budget.py
|   |-- openrouter.py
|   `-- provider.py
|-- models/
|   |-- evidence.py
|   |-- graph.py
|   |-- manifest.py
|   |-- semantic.py
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
layout. Stage 6 adds a Semanticist agent under `src/agents/`, semantic models
under `src/models/`, provider and budgeting seams under `src/llm/`, and
artifact/orchestrator extensions that preserve the existing staged pipeline.

## Phase 0: Research

Research resolves the design choices that affect trust, cost, and deterministic
semantic behavior:

- provider abstraction and transport strategy for OpenRouter-backed chat and
  embedding usage
- evidence-bundle composition that grounds purpose statements in implementation
  rather than docstrings
- documentation drift detection strategy that stays auditable and degrades
  safely without provider access
- domain clustering strategy that prefers embeddings when available but remains
  operational with graph- and path-based fallbacks
- Day-One synthesis strategy that combines Surveyor, Hydrologist, and
  Semanticist outputs with explicit evidence citations and budget controls

## Phase 1: Design & Contracts

### Design Deliverables

- Typed semantic models for module semantics, drift findings, domain maps,
  Day-One answers, and model-usage accounting
- Semanticist artifact contract covering inputs, outputs, evidence boundaries,
  warning semantics, and deterministic serialization
- Quickstart scenarios covering normal runs, budget exhaustion, offline or
  provider-failure degradation, and downstream artifact consumption
- Provider and budget abstractions that isolate model-backed work from the core
  semantic pipeline

### Architectural Decisions

- Semanticist consumes manifest, structural, module-graph, and lineage-graph
  artifacts from prior stages and loads raw module source lazily from the
  prepared repository only for semantic-eligible modules.
- Purpose statements are built from compact evidence bundles that explicitly
  exclude docstrings and nearby documentation from the primary behavior prompt,
  reserving documentation only for drift comparison.
- Documentation drift is assessed with a rule-first comparison layer plus a
  budgeted adjudication path, so deterministic signals exist even when LLM
  calls fail or are disabled.
- Domain clustering uses provider-backed embeddings when configured, but falls
  back to deterministic graph/path similarity and NetworkX-based grouping to
  avoid hard dependency on heavy ML libraries.
- Day-One answers are synthesized from structured semantic, architectural, and
  lineage artifacts with explicit evidence citations and confidence, then
  persisted as deterministic JSON artifacts ready for Archivist.

## Complexity Tracking

No constitution violations are required for this design.
