# Feature Specification: Archivist Navigator Stage

**Feature Branch**: `[008-archivist-navigator]`
**Created**: 2026-03-15
**Status**: Draft
**Input**: User description: "Build Phase 4 of the Brownfield Cartographer: the Archivist (Living Context Maintainer) and the Navigator query interface. The upstream layers already exist: Surveyor, Hydrologist, and Semanticist. This phase must turn those outputs into living artifacts that can be reused as the codebase evolves, and add a query interface for exploratory and structured investigation."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Produce Living Context Artifacts (Priority: P1)

As an engineer or AI coding agent onboarding to a brownfield repository, I want the system to convert prior architectural, lineage, and semantic analysis into reusable living artifacts so that I can understand the codebase quickly without manually stitching together multiple intermediate outputs.

**Why this priority**: The final living artifacts are the primary product surface of this phase. Without them, the earlier analysis remains fragmented and difficult to reuse in ongoing engineering work.

**Independent Test**: Can be fully tested by running the pipeline on a prepared repository and verifying that `CODEBASE.md`, `onboarding_brief.md`, `lineage_graph.json`, `semantic_index/`, and `cartography_trace.jsonl` are created with the required sections, evidence citations, and trust labels.

**Acceptance Scenarios**:

1. **Given** completed Surveyor, Hydrologist, and Semanticist outputs, **When** Archivist runs successfully, **Then** it produces a `CODEBASE.md` file containing architecture overview, critical path, data sources and sinks, known debt, recent change velocity, and module purpose index sections.
2. **Given** completed upstream analysis outputs, **When** Archivist generates `onboarding_brief.md`, **Then** it answers all five Day-One questions with explicit evidence citations and a clear distinction between observed findings and inferred conclusions.
3. **Given** a successful Archivist run, **When** a consumer inspects the audit trail, **Then** the generated artifacts can be traced back to evidence sources, methods, and confidence labels.

---

### User Story 2 - Query the Codebase Through Navigator (Priority: P2)

As an engineer investigating a repository, I want to ask targeted questions about implementation, lineage, blast radius, and module purpose so that I can explore the codebase through evidence-backed answers instead of ad hoc manual searching.

**Why this priority**: The Navigator interface turns stored codebase intelligence into a practical investigation workflow for humans and downstream AI agents.

**Independent Test**: Can be fully tested by issuing each supported query type against an analyzed repository and verifying that the response includes the requested answer plus source file, line range where available, analysis method, and trust label.

**Acceptance Scenarios**:

1. **Given** an analyzed repository, **When** a user asks where a concept is implemented, **Then** Navigator returns relevant implementation locations with evidence citations and method labels.
2. **Given** a known dataset or table, **When** a user asks to trace lineage in a chosen direction, **Then** Navigator returns the relevant upstream or downstream relationships with evidence-backed reasoning.
3. **Given** a module path, **When** a user asks for blast radius or explanation, **Then** Navigator returns the affected context or module explanation with explicit citations and trust labeling.

---

### User Story 3 - Refresh Living Context Incrementally (Priority: P3)

As a maintainer rerunning Cartographer after repository changes, I want the final stage to refresh only changed files and dependent artifacts so that the system remains useful as an ongoing codebase intelligence tool rather than a one-time full-scan report.

**Why this priority**: Incremental refresh is what makes the living-context artifacts practical over time for large repositories.

**Independent Test**: Can be fully tested by running the final stage twice on the same repository, introducing a limited set of changes between runs, and verifying that unaffected artifacts are reused while impacted artifacts are refreshed and recorded as such.

**Acceptance Scenarios**:

1. **Given** a prior successful run and new commits affecting part of the repository, **When** the final stage runs again, **Then** it refreshes changed or dependent artifacts instead of rerunning the whole repository unnecessarily.
2. **Given** no relevant repository changes since the previous run, **When** the final stage runs again, **Then** it reuses eligible final artifacts and records the reuse decision.
3. **Given** a change invalidates previous evidence or citations, **When** incremental refresh occurs, **Then** stale final-stage content is replaced with updated evidence-backed output.

---

### Edge Cases

- What happens when required upstream artifacts are missing, stale, or inconsistent with one another?
- How does the system behave when a Navigator query cannot be answered confidently from available evidence?
- What happens when evidence exists but line ranges are unavailable or out of date due to repository changes?
- What happens when excluded, secret-bearing, vendored, binary, or oversized files are encountered during refresh decisions?
- How does the system behave when a file type is partially supported, unsupported, or unparseable in upstream stages?
- What partial outputs remain available when one final-stage subcomponent degrades while the rest of the pipeline is still valid?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST create a `CODEBASE.md` living context artifact for each successful final-stage run.
- **FR-002**: `CODEBASE.md` MUST include architecture overview, critical path, data sources and sinks, known debt, recent change velocity, and module purpose index sections.
- **FR-003**: System MUST create an `onboarding_brief.md` artifact that answers the five FDE Day-One questions.
- **FR-004**: Every answer in `onboarding_brief.md` MUST include evidence citations and MUST distinguish directly observed findings from inferred conclusions.
- **FR-005**: System MUST preserve a durable `lineage_graph.json` artifact for downstream tooling reuse as part of the final-stage outputs.
- **FR-006**: System MUST create and maintain a `semantic_index/` artifact that supports retrieval of relevant architectural context from module purpose statements.
- **FR-007**: System MUST create a `cartography_trace.jsonl` audit artifact that records analysis actions, evidence sources, methods used, and confidence levels.
- **FR-008**: System MUST provide a query interface supporting these capabilities: finding implementations, tracing lineage, estimating blast radius, and explaining modules.
- **FR-009**: Every query response MUST cite source file, line range when available, analysis method, and whether the answer is based on direct analysis or inferred interpretation.
- **FR-010**: Query responses MUST prefer directly observed evidence when available and MUST explicitly identify inferred conclusions.
- **FR-011**: The final stage MUST consume and reconcile Surveyor, Hydrologist, and Semanticist outputs rather than recomputing their core analyses from raw repository content.
- **FR-012**: The final stage MUST support incremental refresh by identifying changed inputs and dependent outputs when a previous run exists.
- **FR-013**: The final stage MUST avoid unnecessary full reprocessing when existing final artifacts remain valid for unchanged repository areas.
- **FR-014**: The system MUST record whether a final artifact or answer was freshly generated, reused, or partially degraded.
- **FR-015**: When evidence is insufficient for an artifact section or query answer, the system MUST return a bounded partial result rather than fabricated certainty.
- **FR-016**: Specification MUST define analysis-root boundaries, excluded inputs, and any secret-handling constraints.
- **FR-017**: Specification MUST define file-type routing expectations, including fully supported, partially supported, skipped, and unsupported classes when relevant.
- **FR-018**: Specification MUST state evidence expectations, including source metadata, deterministic artifacts, and the distinction between static, graph-derived, and LLM-derived outputs.
- **FR-019**: Specification MUST define non-destructive output locations and any cache, log, index, or artifact directories created by the feature.
- **FR-020**: Specification MUST state automated test expectations and any performance or cost budgets relevant to the feature.

### Key Entities *(include if feature involves data)*

- **Living Context Artifact**: A reusable human- and agent-facing output that summarizes the repository with evidence-backed architecture, lineage, risk, and module-purpose context.
- **Navigator Query**: A structured user request for implementation, lineage, blast-radius, or module-understanding information.
- **Trace Record**: A structured audit entry describing an analysis action, the evidence used, the method applied, the confidence assigned, and whether the result was reused or newly produced.
- **Semantic Index Entry**: A searchable representation of a module purpose statement and its associated evidence and domain context.
- **Incremental Refresh State**: The tracked repository-change and artifact-dependency state used to decide what must be refreshed or reused.

## Repository and Language Scope *(mandatory for code intelligence work)*

- **Analysis Root**: The selected repository root or configured subpath already prepared for Cartographer analysis.
- **Excluded Inputs**: Secret-bearing, vendored, generated, binary, oversized, and otherwise excluded files remain out of scope unless explicitly allowed by existing stage policies.
- **Language Routing**: The final stage reuses upstream routing decisions for Python, SQL, YAML, JavaScript/TypeScript, JSON, notebooks, and other repository content, including support-status distinctions for partial or unsupported inputs.
- **Evidence Model**: Outputs may combine direct static observations, graph-derived relationships, reuse decisions, and bounded inferred reasoning, with each result labeled by method, evidence references, and confidence.
- **Output Locations**: All artifacts, indexes, traces, caches, and refreshed outputs remain inside project-controlled `.cartography/` directories and run-specific artifact folders.
- **Model Budget**: Any model-backed synthesis or semantic search support must remain bounded by configured per-run budgets, and non-model partial results remain available when provider access or budget is unavailable.

## Assumptions

- Surveyor, Hydrologist, and Semanticist outputs already exist and are consumable for the same analysis root.
- Evidence citations may reference repository paths and line ranges taken from existing artifacts or refreshed source validation when necessary to keep citations current.
- Incremental refresh is driven by repository changes since the last successful run and may reuse upstream artifacts when they remain valid for unchanged inputs.
- The query interface is intended for both human operators and downstream AI agents, but all answers follow the same trust, evidence, and non-destructive rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For a successful run, 100% of required final-stage artifacts are created in project-controlled output locations and are readable without manual cleanup.
- **SC-002**: At least 95% of supported onboarding brief sections and query responses include one or more valid evidence citations with source path, line range when available, method label, and observation-versus-inference status.
- **SC-003**: In a representative onboarding exercise, a new engineer can answer the five Day-One questions within 10 minutes using `CODEBASE.md` and `onboarding_brief.md` without needing to inspect more than five raw source files.
- **SC-004**: On a rerun with changes limited to a small subset of files, the system reuses unaffected final artifacts and records those reuse decisions for 100% of reused outputs.
- **SC-005**: When evidence is insufficient or an upstream dependency partially fails, the system still emits available final-stage artifacts and records the limitation for 100% of degraded results.
