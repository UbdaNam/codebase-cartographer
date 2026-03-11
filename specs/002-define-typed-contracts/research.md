# Phase 0 Research: Brownfield Cartographer Stage 1 Typed Contracts

## Decision: Use Python 3.11+ with Pydantic v2 for contract models

**Rationale**: Python 3.11+ aligns with the existing foundation and supports
modern typing features. Pydantic v2 provides strong validation, stable
serialization, and ergonomic model composition for the shared contracts layer.

**Alternatives considered**:
- Dataclasses only: lighter, but weaker for validation and consistent
  serialization rules.
- Marshmallow or custom serializers: workable, but add extra abstraction
  without improving the project’s typed-contract needs.

## Decision: Keep Stage 1 modeling focused under `src/models/` with only tiny support helpers

**Rationale**: Centralizing contract definitions under `src/models/` keeps the
schema layer coherent and easy to evolve. A minimal supporting helper for
deterministic IDs is sufficient without expanding into analyzer or orchestration
logic.

**Alternatives considered**:
- Splitting models across many domain folders immediately: rejected because it
  adds structure before the shared contract surface stabilizes.
- Putting ID logic into every model file: rejected because it would duplicate
  stable ID behavior.

## Decision: Represent node kinds, edge kinds, support status, methods, skip reasons, and confidence as explicit enums

**Rationale**: Stable, human-readable enums make JSON payloads predictable and
reduce drift across future stages. They also improve validation and testability
for mixed-language and partial-result cases.

**Alternatives considered**:
- Free-form strings: rejected because they invite schema drift and inconsistent
  serialization.
- Integer-backed enums: rejected because they are less readable in persisted
  artifacts.

## Decision: Separate shared pipeline state from future Navigator query state

**Rationale**: Analysis execution state and query execution state evolve at
different speeds and have different responsibilities. Separating them now keeps
future LangGraph integration cleaner without requiring workflow logic today.

**Alternatives considered**:
- One monolithic state object: rejected because it would mix pipeline and query
  concerns too early.
- Deferring Navigator state entirely: rejected because Stage 1 explicitly needs
  a future-ready query contract.

## Decision: Make evidence and citation records reusable across all graph and artifact models

**Rationale**: Evidence awareness is a core trust requirement. Reusable
evidence models ensure every node, edge, artifact, and query response can carry
source path, optional line info, method, confidence, and supporting context in
the same shape.

**Alternatives considered**:
- Per-model evidence fields with different shapes: rejected because it weakens
  trust and complicates later reporting.
- Evidence stored only in external artifacts: rejected because downstream
  models need first-class access to it.

## Decision: Use deterministic ID helpers derived from canonical fields

**Rationale**: Stable IDs based on normalized paths, canonical names, and edge
  endpoints make diffs readable and support reproducible `.cartography`
  artifacts without runtime randomness.

**Alternatives considered**:
- UUIDs at runtime: rejected because they break reproducibility.
- Human-entered IDs: rejected because they are error-prone and inconsistent.

## Decision: Design contracts to explicitly support partial and degraded analysis

**Rationale**: Brownfield repositories often produce incomplete or unresolved
results. Contracts must represent skipped files, unresolved references,
optional line numbers, and partial support states without validation failure.

**Alternatives considered**:
- Strict “complete data only” schemas: rejected because they do not match
  real-world repository analysis conditions.
- Untyped extension bags for incomplete data: rejected because they hide
  degradation semantics instead of modeling them.

## Decision: Keep Stage 1 narrow and exclude analyzers, graph engines, and workflow logic

**Rationale**: The purpose of Stage 1 is to standardize shared contracts, not
to start partial implementations of parsing, lineage, graph algorithms, or
LangGraph orchestration. This keeps the stage production-minded and testable.

**Alternatives considered**:
- Adding early graph wrappers or analyzers: rejected because it would mix
  contract design with execution concerns.
- Implementing Navigator workflow stubs: rejected because the state contract is
  sufficient for now.
