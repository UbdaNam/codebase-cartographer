# Feature Specification: Semanticist Layer

**Feature Branch**: `007-semanticist-layer`
**Created**: 2026-03-14
**Status**: Draft
**Input**: User description: "Build the Semanticist layer for the Brownfield Cartographer. The goal is to add semantic understanding on top of the existing Surveyor and Hydrologist outputs. This layer should explain what modules do in business terms, detect when documentation no longer matches implementation, group modules into inferred business domains, and synthesize the five FDE Day-One answers from the full architectural context. This layer must not simply restate docstrings. It should ground every purpose statement in implementation evidence derived from the code and previously generated structural and lineage artifacts. The system should support these capabilities: 1. Generate a purpose statement for each module - Produce a concise 2-3 sentence description of what the module does and why it exists - Base the description on code behavior and dependencies, not existing comments or docstrings - Store the result back into the module's semantic representation 2. Detect documentation drift - Compare each module's current implementation against its docstring or nearby documentation - Flag likely contradictions, omissions, or outdated descriptions - Record drift findings with confidence and evidence 3. Infer domain boundaries - Group modules into business or architectural domains such as ingestion, transformation, serving, monitoring, orchestration, or shared utilities - The output should help a new engineer understand where business logic is concentrated versus distributed 4. Answer the Five FDE Day-One Questions - What is the primary data ingestion path? - What are the 3-5 most critical output datasets or endpoints? - What is the blast radius if the most critical module fails? - Where is the business logic concentrated versus distributed? - What has changed most frequently in the last 90 days? 5. Preserve trust and auditability - Every semantic result should reference evidence sources such as module path, relevant code excerpts, lineage relationships, graph metrics, or git velocity inputs - The system should clearly distinguish inferred conclusions from directly observed facts This feature should integrate into the existing Brownfield Cartographer pipeline after Hydrologist and produce outputs that can later be consumed by the Archivist for CODEBASE.md and onboarding_brief.md generation."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Understand the System Quickly (Priority: P1)

A new engineer or technical lead reviews a prepared repository and receives grounded explanations of what each important module does, how modules group into business domains, and where the main ingestion, transformation, and delivery paths run through the system.

**Why this priority**: The primary value of the Semanticist layer is reducing time-to-understanding for brownfield systems by turning structural and lineage facts into business-facing explanations.

**Independent Test**: Can be fully tested by running the pipeline on a repository with existing Surveyor and Hydrologist outputs and verifying that each module receives a purpose statement, a domain assignment, and that the five Day-One answers are produced with linked evidence.

**Acceptance Scenarios**:

1. **Given** a repository with module and lineage artifacts, **When** Semanticist completes analysis, **Then** each eligible module has a concise purpose statement grounded in implementation evidence rather than copied documentation.
2. **Given** a repository with multiple architectural areas, **When** Semanticist infers domains, **Then** modules are grouped into understandable business or architectural domains and the output identifies where logic is concentrated versus distributed.
3. **Given** a repository with ingestion paths, outputs, and module criticality signals, **When** Semanticist generates the five Day-One answers, **Then** each answer includes both the conclusion and the evidence used to justify it.

---

### User Story 2 - Detect Documentation Drift (Priority: P2)

A maintainer reviews current code against nearby documentation and quickly sees where descriptions are stale, incomplete, or contradicted by implementation behavior.

**Why this priority**: Trust in semantic outputs depends on the system distinguishing working code from outdated descriptions, especially in brownfield repositories with inconsistent documentation quality.

**Independent Test**: Can be fully tested by analyzing a repository fixture with intentionally outdated docstrings or adjacent documentation and verifying that drift findings are flagged with evidence and confidence.

**Acceptance Scenarios**:

1. **Given** a module whose documentation says it performs one responsibility, **When** implementation evidence shows a materially different responsibility, **Then** the system records a likely contradiction with supporting evidence.
2. **Given** a module with partial or missing documentation, **When** the implementation clearly performs important behavior not described nearby, **Then** the system records an omission finding with evidence and confidence.

---

### User Story 3 - Feed Downstream Knowledge Products (Priority: P3)

A downstream agent or reviewer consumes semantic outputs to generate higher-level repository narratives such as onboarding briefs and codebase summaries without re-deriving the underlying evidence.

**Why this priority**: The Semanticist layer must create durable, audit-ready outputs that later stages can trust and reuse directly.

**Independent Test**: Can be fully tested by verifying that semantic outputs are written to project-controlled artifacts, include stable identifiers, and expose enough evidence for later stages to consume without reparsing the repository.

**Acceptance Scenarios**:

1. **Given** completed Semanticist analysis, **When** a downstream stage reads the semantic outputs, **Then** it can retrieve module purposes, domain assignments, drift findings, and Day-One answers from deterministic artifacts.
2. **Given** a semantic result, **When** a reviewer inspects it, **Then** the result clearly distinguishes directly observed facts from inferred conclusions and links back to its evidence sources.

---

### Edge Cases

- What happens when a module has little executable logic but many imports or re-exports?
- How does the system behave when no reliable documentation exists near a module?
- What happens when documentation exists but conflicts with lineage, dependency, or velocity evidence?
- How does the system handle excluded, secret-bearing, vendored, binary, or oversized files that were filtered out in earlier stages?
- How does the system behave when a file type is partially supported, unsupported, or unparseable in earlier stages, leaving incomplete evidence for semantic analysis?
- What partial outputs remain available when purpose generation succeeds but drift detection or domain inference cannot be completed for some modules?
- How does the system behave when repositories contain both tightly coupled shared utilities and weakly related business areas that do not map cleanly to a single domain?
- What happens when the repository has no clear output datasets or endpoints, making some Day-One answers necessarily low-confidence or not applicable?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST run after Hydrologist and consume persisted manifest, structural, module graph, and lineage graph artifacts for the same prepared repository and run context.
- **FR-002**: System MUST produce a semantic representation for each eligible module that includes a concise 2-3 sentence purpose statement describing what the module does and why it exists.
- **FR-003**: System MUST ground each purpose statement in implementation evidence derived from code behavior, dependency relationships, structural facts, lineage relationships, graph metrics, or recent change signals rather than restating comments or docstrings.
- **FR-004**: System MUST record evidence references for every semantic result, including the source artifact or repository location used to support the result.
- **FR-005**: System MUST compare each module's current implementation against its docstring or nearby documentation and record likely documentation drift findings for contradictions, omissions, or outdated descriptions.
- **FR-006**: System MUST assign each eligible module to an inferred business or architectural domain, including support for domains such as ingestion, transformation, serving, monitoring, orchestration, and shared utilities when supported by evidence.
- **FR-007**: System MUST summarize where business logic is concentrated versus distributed across the repository using inferred domain and dependency context.
- **FR-008**: System MUST answer the five FDE Day-One questions for the analyzed repository and attach evidence and confidence to each answer.
- **FR-009**: System MUST distinguish directly observed facts from inferred conclusions in persisted outputs so reviewers can audit how each conclusion was reached.
- **FR-010**: System MUST preserve deterministic identifiers, stable ordering, and reproducible outputs for unchanged inputs.
- **FR-011**: System MUST persist semantic artifacts in project-controlled output locations so downstream stages can consume them without rescanning the repository.
- **FR-012**: System MUST preserve partial results when some modules lack sufficient evidence, and MUST record warnings or partial-result flags rather than fabricating certainty.
- **FR-013**: System MUST define analysis-root boundaries, excluded inputs, and secret-handling constraints inherited from earlier stages and MUST avoid analyzing excluded content.
- **FR-014**: System MUST define file-type routing expectations for semantic analysis, including how Python, SQL, YAML, JavaScript/TypeScript, JSON, notebooks, and unsupported files contribute or do not contribute evidence.
- **FR-015**: System MUST define evidence expectations for semantic outputs, including source metadata, graph-derived signals, change-history inputs, and any inferred conclusions produced from those inputs.
- **FR-016**: System MUST write only to non-destructive, project-controlled artifact, cache, or log locations and MUST not modify analyzed repositories.
- **FR-017**: System MUST provide outputs that can be consumed by Archivist for `CODEBASE.md` and `onboarding_brief.md` generation without requiring manual reinterpretation of semantic findings.
- **FR-018**: System MUST support automated validation that purpose statements are not copied verbatim from existing docstrings or adjacent documentation beyond short quoted evidence snippets.
- **FR-019**: System MUST record semantic confidence at the result level so low-evidence conclusions can be reviewed differently from high-evidence conclusions.
- **FR-020**: System MUST complete semantic analysis for repositories within the same operational constraints as prior stages, degrading gracefully when model, parsing, or evidence limits are reached.

### Key Entities *(include if feature involves data)*

- **Semantic Module Profile**: The semantic representation for one module, including its module identity, purpose statement, inferred domain, evidence references, confidence, and any linked drift findings.
- **Documentation Drift Finding**: A structured record describing a likely contradiction, omission, or outdated statement between current implementation and nearby documentation, along with evidence and confidence.
- **Domain Boundary**: A grouped business or architectural area that clusters related modules and explains whether logic is concentrated or distributed across the repository.
- **Day-One Answer**: A repository-level answer to one of the five FDE questions, including the conclusion, confidence, and supporting evidence references.
- **Evidence Reference**: A pointer to supporting facts such as module paths, graph relationships, lineage records, recent change signals, or small code/document excerpts used to justify a semantic conclusion.
- **Semantic Artifact Set**: The persisted outputs that contain module semantics, domain summaries, drift findings, and Day-One answers for downstream consumption.

## Repository and Language Scope *(mandatory for code intelligence work)*

- **Analysis Root**: The prepared repository selected by earlier Brownfield Cartographer stages, analyzed from its normalized repository root.
- **Excluded Inputs**: Secret-bearing, vendored, generated, binary, oversized, cached, and otherwise ignored paths inherited from repository preparation, manifest, and structural analysis policies.
- **Language Routing**: Python, SQL, YAML, JavaScript/TypeScript, JSON, and other supported repository inputs contribute semantic evidence only through persisted earlier-stage facts and approved semantic processing; unsupported or skipped file types contribute no direct semantic claims beyond existing stage warnings.
- **Evidence Model**: Direct observations come from persisted manifest, structural, module graph, lineage, and git-history evidence; inferred outputs include module purposes, domain boundaries, drift conclusions, and Day-One answers, each with explicit evidence links and confidence.
- **Output Locations**: Semantic artifacts, summaries, logs, and derived data MUST be written under project-controlled `.cartography/` paths and versioned stage directories as appropriate for downstream consumption.
- **Model Budget**: Semantic inference may use bounded language-model or embedding assistance where needed, but outputs MUST remain auditable, deterministic in structure, and recoverable with partial results when inference budgets are exhausted.

## Assumptions

- Existing Surveyor and Hydrologist artifacts are present, valid, and correspond to the same prepared repository and run context used by Semanticist.
- Semanticist is responsible for producing durable semantic artifacts for later stages, not for generating final narrative deliverables such as onboarding documents directly.
- Nearby documentation includes docstrings, README fragments, module-adjacent markdown, or similar repository-local descriptive text when available.
- The five Day-One answers may be low-confidence or explicitly partial when the repository does not expose enough evidence to support a stronger conclusion.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At least 95% of eligible modules in a supported repository receive a purpose statement with at least one linked evidence reference.
- **SC-002**: Reviewers can trace 100% of persisted semantic conclusions back to supporting evidence without opening implementation internals beyond the recorded references.
- **SC-003**: In validation repositories with seeded documentation mismatches, at least 85% of known contradictions or omissions are flagged for reviewer inspection.
- **SC-004**: For supported repositories with clear architectural and lineage signals, all five Day-One questions are answered or explicitly marked partial with confidence and evidence in a single semantic artifact set.
- **SC-005**: Re-running Semanticist on an unchanged repository produces the same semantic identifiers and ordering for at least 99% of persisted records.
