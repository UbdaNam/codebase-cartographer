# Feature Specification: Brownfield Cartographer Stage 1 Typed Contracts

**Feature Branch**: `002-define-typed-contracts`
**Created**: 2026-03-11
**Status**: Draft
**Input**: User description: "Build Stage 1 typed contracts for Brownfield
Cartographer, a LangGraph-oriented multi-agent codebase intelligence system for
large brownfield repositories. This stage should define the shared schemas and
state models that all later stages depend on. The goal is to create stable,
deterministic, evidence-aware contracts for code structure, lineage, graph
storage, analysis state, and future query execution. Stage 1 must include:
typed Pydantic schemas for graph nodes, graph edges, graph containers, and
analysis artifacts; explicit enums for node kinds, edge kinds, support status,
analysis method, and skip reasons; shared run and pipeline state for the
analysis flow; a separate typed state for the future LangGraph Navigator query
agent; evidence and citation models that preserve source path, line
information, method, and confidence; deterministic serialization contracts for
later .cartography outputs; tests validating schema behavior, enum usage,
stable IDs, and serialization consistency. The models must support future
agents including Surveyor, Hydrologist, Semanticist, Archivist, and Navigator.
The contracts must be designed for mixed-language repositories, partial
analysis results, graceful degradation, and evidence-backed outputs. This
stage should not yet implement AST parsing, SQL lineage extraction, graph
algorithms, LangGraph workflows, or LLM summarization. It should only define
the contracts that make those later stages consistent and production-minded."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Share Stable Analysis Contracts (Priority: P1)

As a Cartographer developer, I want one typed contract layer for graph records,
analysis artifacts, and run state so every later stage can exchange data
without inventing incompatible schemas.

**Why this priority**: Shared contracts are the foundation for all later
agents, storage, and orchestration work; without them, downstream stages will
drift and become hard to compose.

**Independent Test**: A developer can instantiate the core schemas, serialize
them deterministically, and confirm that graph structures, analysis artifacts,
and pipeline state round-trip consistently without relying on future analysis
engines.

**Acceptance Scenarios**:

1. **Given** a developer creating a graph node, edge, and container,
   **When** they validate and serialize those records, **Then** the contracts
   enforce stable structure, enum usage, and reproducible output ordering.
2. **Given** a developer creating an analysis artifact and shared run state,
   **When** those models are validated, **Then** they produce predictable
   schema behavior that later stages can rely on without custom adapters.

---

### User Story 2 - Preserve Evidence and Partial Results (Priority: P2)

As an operator or downstream agent author, I want evidence and citation models
that preserve source location, method, confidence, and partial-result context
so later outputs remain trustworthy even when analysis is incomplete.

**Why this priority**: Evidence-aware contracts are required for reliable
lineage, semantic, and onboarding outputs, especially in mixed-language
brownfield repositories where partial results are normal.

**Independent Test**: A developer can construct evidence-backed records for
supported, partial, skipped, and degraded outcomes and confirm that the schema
captures source metadata and analysis method without ambiguity.

**Acceptance Scenarios**:

1. **Given** a partially analyzed repository artifact, **When** evidence and
   citation records are created, **Then** source path, line information,
   method, confidence, and degradation context are preserved in typed form.
2. **Given** a skipped or unsupported input, **When** its contract record is
   serialized, **Then** the output captures support status and skip reason
   without pretending complete analysis occurred.

---

### User Story 3 - Prepare Navigator and Multi-Agent State (Priority: P3)

As a future agent developer, I want separate typed state for pipeline execution
and future Navigator query handling so LangGraph-oriented flows can be added
later without redefining state shape midstream.

**Why this priority**: Query execution and multi-agent orchestration depend on
stable state contracts that must be defined before workflow logic is layered on
top.

**Independent Test**: A developer can create shared pipeline state and future
Navigator query state objects and confirm they capture agent-facing fields,
query context, and execution metadata without implementing LangGraph workflows.

**Acceptance Scenarios**:

1. **Given** a future analysis pipeline run, **When** shared pipeline state is
   initialized, **Then** the state can represent stage progress, artifact
   references, and partial outcomes in typed form.
2. **Given** a future Navigator query session, **When** query state is
   instantiated, **Then** it preserves query intent, evidence references, and
   response-tracking fields without requiring a live workflow engine.

### Edge Cases

- What happens when a contract record represents a skipped, unsupported, or
  partially analyzed input? The schema must preserve status and reason without
  implying complete analysis.
- What happens when evidence exists without exact line ranges? The contracts
  must support optional line metadata while still preserving source identity and
  method.
- What happens when mixed-language records share common graph structures? The
  contracts must separate language-specific attributes from common identifiers
  and evidence fields.
- What happens when later stages serialize the same logical object multiple
  times? The contracts must support stable IDs and deterministic output shapes.
- What happens when a future query references artifacts that were only
  partially produced? The query-state contracts must preserve partial-result
  context instead of failing shape validation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST define typed schemas for graph nodes, graph
  edges, graph containers, and analysis artifacts that later stages can share
  without incompatible data shapes.
- **FR-002**: The system MUST define explicit enums for node kinds, edge kinds,
  support status, analysis method, and skip reasons.
- **FR-003**: The system MUST define shared run and pipeline state for the
  analysis flow.
- **FR-004**: The system MUST define a separate typed state for the future
  Navigator query agent.
- **FR-005**: The system MUST define evidence and citation models that preserve
  source path, line information when available, method, and confidence.
- **FR-006**: The system MUST support mixed-language repository records without
  assuming Python-only analysis contracts.
- **FR-007**: The system MUST represent supported, partial, skipped, and
  unsupported analysis outcomes using deterministic typed contracts.
- **FR-008**: The system MUST support graceful degradation by allowing partial
  analysis artifacts and incomplete evidence contexts to be represented
  explicitly.
- **FR-009**: The system MUST provide deterministic serialization contracts for
  later `.cartography` outputs.
- **FR-010**: The system MUST support future agents including Surveyor,
  Hydrologist, Semanticist, Archivist, and Navigator without requiring
  stage-specific schema rewrites.
- **FR-011**: The system MUST include automated tests validating schema
  behavior, enum usage, stable IDs, and serialization consistency.
- **FR-012**: The system MUST exclude AST parsing, SQL lineage extraction,
  graph algorithms, LangGraph workflow execution, and LLM summarization from
  Stage 1 scope.
- **FR-013**: Specification MUST define analysis-root boundaries, excluded
  inputs, and secret-handling constraints relevant to later artifact contracts.
- **FR-014**: Specification MUST define file-type routing expectations,
  including fully supported, partially supported, skipped, and unsupported
  classes where contract fields depend on support status.
- **FR-015**: Specification MUST state evidence expectations, including source
  metadata, deterministic artifacts, and distinction between static analysis,
  graph inference, and future LLM-derived outputs.
- **FR-016**: Specification MUST define non-destructive output locations for
  serialized contracts and later `.cartography` artifacts.
- **FR-017**: Specification MUST state automated test expectations and stable
  contract behavior under production-minded repository scale.

### Key Entities *(include if feature involves data)*

- **Graph Node**: A typed record representing a code, data, config, or other
  repository entity with stable identity, kind, metadata, and evidence.
- **Graph Edge**: A typed relationship record connecting graph nodes with a
  specific edge kind, direction, and evidence context.
- **Graph Container**: A deterministic wrapper for graph nodes, edges, and
  related metadata intended for later `.cartography` output.
- **Analysis Artifact**: A typed record describing a produced analysis object,
  its method, support status, evidence, and serialization metadata.
- **Pipeline State**: Shared typed state for multi-stage analysis execution,
  artifact references, progress tracking, and degraded outcomes.
- **Navigator Query State**: Future typed state describing query intent,
  referenced evidence, intermediate context, and response tracking.
- **Evidence Record**: Source-aware citation data carrying path, optional line
  information, method, confidence, and supporting notes.

## Repository and Language Scope *(mandatory for code intelligence work)*

- **Analysis Root**: Contracts apply to records derived from a local repository
  path or a repository materialized from a remote source, always constrained to
  an explicit analysis root.
- **Excluded Inputs**: Secret-bearing, generated, vendored, binary, archived,
  oversized, and otherwise excluded inputs remain outside direct source parsing,
  but contract records must still be able to represent skipped outcomes and
  reasons.
- **Language Routing**: Contracts must support Python, SQL, YAML,
  JavaScript/TypeScript, JSON configuration, notebooks, and future
  mixed-language records using shared support-status semantics.
- **Evidence Model**: Contracts must distinguish evidence derived from static
  analysis, graph inference, and future LLM inference while preserving source
  metadata and confidence.
- **Output Locations**: Serialized contracts are intended for later
  project-controlled `.cartography` outputs and must remain deterministic and
  non-destructive.
- **Model Budget**: No LLM or embedding execution is in scope for Stage 1; only
  the future-facing contract fields are defined.

## Assumptions

- Stage 0 foundation behavior already exists and provides the baseline package,
  artifact, and safe-scanning structure that Stage 1 contracts can build on.
- Contract models will be implemented with typed Pydantic schemas and enums, but
  the specification remains focused on behavior and consistency rather than code
  structure.
- Later stages will need to serialize contract records into `.cartography`
  artifacts without changing field meaning or identity semantics.
- Mixed-language repositories and degraded outcomes are normal, so the contract
  layer must treat partial results as first-class outputs.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can instantiate and serialize the core graph,
  artifact, evidence, and state contracts with deterministic output across
  repeated runs using the same inputs.
- **SC-002**: All required enums and typed contract families validate mixed
  supported, partial, skipped, and unsupported analysis outcomes without custom
  per-stage schema patches.
- **SC-003**: Automated tests cover schema validation, enum usage, stable IDs,
  and serialization consistency with all tests passing in a clean environment.
- **SC-004**: Reviewers can verify that future Surveyor, Hydrologist,
  Semanticist, Archivist, and Navigator stages can share the contract layer
  without redefining evidence, graph, or state fundamentals.
- **SC-005**: Reviewers can confirm that Stage 1 adds no AST parsing, SQL
  lineage extraction, graph algorithm execution, LangGraph workflow execution,
  or LLM summarization while still preparing contracts for those later stages.
