# Feature Specification: Hydrologist Agent

**Feature Branch**: `006-hydrologist-agent`
**Created**: 2026-03-12
**Status**: Draft
**Input**: User description: "Build Stage 5 Hydrologist agent for Brownfield Cartographer. This stage should extend the system from architectural code analysis to data lineage intelligence. The Hydrologist agent must discover how datasets flow through the codebase by analyzing SQL files, Python data operations, and configuration-driven pipeline definitions. Stage 5 must include: - a Hydrologist agent that consumes the manifest, structural extraction artifacts, and module graph outputs - SQL parsing using sqlglot to identify dataset dependencies and transformation logic - extraction of table references from SELECT, FROM, JOIN, and CTE chains - support for SQL files, embedded SQL strings in Python, and dbt-style models - parsing of YAML configuration files to identify pipeline definitions or dataset references - detection of Python-based data operations such as pandas.read_csv, pandas.read_sql, Spark read/write calls, and SQLAlchemy queries - construction of a directed DataLineageGraph representing datasets and transformations - creation of DatasetNode and TransformationNode entities based on the graph schema defined in Stage 1 - graph edges representing data flow relationships such as CONSUMES and PRODUCES - deterministic serialization of lineage artifacts to .cartography/lineage_graph.json - CLI integration so the analyze command runs the Hydrologist stage after the Surveyor stage - tests validating SQL lineage extraction, Python data flow detection, graph construction, and artifact serialization This stage must work across mixed-language repositories and gracefully handle malformed SQL, dynamic query generation, unsupported pipeline frameworks, and partially inferred lineage. This stage should not yet implement semantic indexing, LLM reasoning, LangGraph Navigator queries, or embedding-based search. It should focus on deterministic lineage extraction and graph construction."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate a Deterministic Lineage Graph (Priority: P1)

As an engineer trying to understand how data moves through a brownfield
repository, I want the Hydrologist stage to extract datasets, transformations,
and data-flow relationships from in-scope SQL, Python, and configuration files
so I can inspect a deterministic lineage graph instead of tracing the flows
manually.

**Why this priority**: Deterministic lineage output is the core value of the
Hydrologist stage and is the foundation for later onboarding, impact analysis,
and query workflows.

**Independent Test**: Can be fully tested by running analysis on a mixed-source
fixture repository containing SQL files, embedded SQL in Python, and
configuration-driven data workflows, then verifying that deterministic dataset,
transformation, and flow artifacts are written under `.cartography`.

**Acceptance Scenarios**:

1. **Given** a repository with in-scope SQL files, Python data operations, and
   pipeline configuration files, **When** the Hydrologist stage runs, **Then**
   it produces a deterministic lineage graph containing dataset and
   transformation records plus directed flow relationships.
2. **Given** the same unchanged repository analyzed twice, **When** the
   Hydrologist stage completes, **Then** the serialized lineage graph remains
   stable across runs aside from run-specific metadata.

---

### User Story 2 - Trace Lineage Across Multiple Source Styles (Priority: P2)

As a maintainer working in a mixed-language data repository, I want the
Hydrologist stage to recognize lineage cues from SQL files, dbt-style models,
embedded SQL strings, Python data APIs, and YAML pipeline definitions so I can
see cross-file dataset dependencies without relying on one framework only.

**Why this priority**: Brownfield data systems are heterogeneous. The stage is
not useful if it only understands one lineage source style.

**Independent Test**: Can be fully tested by running analysis on fixture inputs
covering SQL joins and CTEs, dbt-style model files, YAML pipeline references,
and Python read/write patterns, then verifying that the extracted lineage edges
match the expected dataset and transformation relationships.

**Acceptance Scenarios**:

1. **Given** SQL files or dbt-style models with table references in `FROM`,
   `JOIN`, and CTE chains, **When** the Hydrologist stage runs, **Then** it
   extracts upstream and downstream dataset relationships plus transformation
   context.
2. **Given** Python files containing embedded SQL or common data access calls,
   **When** the Hydrologist stage runs, **Then** it extracts dataset usage and
   transformation signals with evidence pointing back to the relevant source
   locations.
3. **Given** YAML pipeline definitions with dataset references, **When** the
   Hydrologist stage runs, **Then** it adds those references into the lineage
   graph as deterministic dataset or transformation relationships where the
   signal is strong enough.

---

### User Story 3 - Degrade Gracefully on Partial or Dynamic Lineage (Priority: P3)

As an engineer analyzing a messy production repository, I want the Hydrologist
stage to preserve partial lineage outputs when SQL is malformed, queries are
built dynamically, or pipeline frameworks are only partially supported so the
system remains useful without overstating certainty.

**Why this priority**: Brownfield lineage extraction is inherently incomplete.
Production-minded behavior requires partial, evidence-backed outputs rather than
all-or-nothing execution.

**Independent Test**: Can be fully tested by running analysis on malformed SQL,
dynamic query construction, and unsupported pipeline fixtures, then verifying
that the stage emits partial lineage results, confidence limits, and structured
warnings without failing the run.

**Acceptance Scenarios**:

1. **Given** malformed SQL or unsupported pipeline conventions, **When** the
   Hydrologist stage runs, **Then** it records structured warnings and preserves
   any valid lineage signals that can still be extracted.
2. **Given** dynamic query generation or ambiguous Python data flows, **When**
   the Hydrologist stage runs, **Then** it marks inferred lineage as partial or
   lower-confidence instead of presenting it as complete fact.

### Edge Cases

- How does the stage behave when SQL files parse partially but include enough
  valid table references to extract some lineage?
- What happens when embedded SQL is constructed dynamically and only fragments
  can be analyzed statically?
- How are dbt-style models, YAML pipeline definitions, or Python data APIs
  handled when the repository uses unsupported or custom conventions?
- How does the stage prevent secret-bearing, generated, vendored, binary,
  archived, oversized, or already skipped files from contributing lineage?
- What partial outputs remain available when SQL lineage succeeds but Python or
  YAML lineage extraction is unavailable?
- How are dataset identities normalized when the same logical dataset appears
  in different source forms or naming conventions?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST run a Hydrologist stage that consumes the existing
  manifest, structural extraction outputs, module graph outputs, and analysis
  state for an analyzed repository.
- **FR-002**: System MUST parse eligible SQL inputs to extract dataset
  references and transformation context from `SELECT`, `FROM`, `JOIN`, and CTE
  structures where parsing succeeds.
- **FR-003**: System MUST support lineage extraction from standalone SQL files,
  embedded SQL strings in Python, and dbt-style model files within the analysis
  root.
- **FR-004**: System MUST inspect eligible YAML configuration files for
  pipeline definitions or dataset references that can contribute deterministic
  lineage signals.
- **FR-005**: System MUST detect common Python-based data operations such as
  pandas read/write calls, Spark read/write calls, SQLAlchemy query execution,
  and equivalent in-scope data access patterns when they can be identified
  statically.
- **FR-006**: System MUST construct a directed lineage graph with dataset and
  transformation entities plus `CONSUMES` and `PRODUCES` style flow
  relationships aligned with the shared graph contracts.
- **FR-007**: System MUST create or update `DatasetNode` and
  `TransformationNode` records using deterministic identifiers and
  evidence-backed metadata.
- **FR-008**: System MUST serialize lineage artifacts deterministically under
  `.cartography`, including `lineage_graph.json` and any supporting lineage
  summary outputs required for orchestrator consumption.
- **FR-009**: System MUST integrate the Hydrologist stage into orchestrated
  analysis so the CLI analyze flow runs it after the Surveyor stage.
- **FR-010**: System MUST preserve partial lineage outputs and structured
  warnings when SQL is malformed, lineage is dynamically constructed,
  frameworks are unsupported, or only partial evidence is available.
- **FR-011**: Specification MUST define analysis-root boundaries, excluded
  inputs, and secret-handling constraints for lineage extraction, including
  that secret file contents are never persisted into logs or artifacts.
- **FR-012**: Specification MUST define file-type routing expectations,
  including supported SQL, Python, and YAML inputs, partially supported inputs
  such as notebooks or shell files, and skipped or unsupported classes.
- **FR-013**: Specification MUST state evidence expectations, including source
  path and line metadata where available, deterministic artifacts, and the
  distinction between static lineage evidence and lower-confidence inferred
  relationships.
- **FR-014**: Specification MUST define non-destructive output locations for
  lineage artifacts, summaries, logs, cache, and any prepared repository state.
- **FR-015**: Specification MUST state automated test expectations for SQL
  lineage extraction, Python data-flow detection, YAML reference extraction,
  lineage graph construction, artifact serialization, and graceful degradation.
- **FR-016**: System MUST support large mixed-language repositories without
  repeated full-tree scans and without reparsing files already excluded by the
  manifest, structural, or Surveyor stages.

### Key Entities *(include if feature involves data)*

- **HydrologistResult**: The stage-level output that summarizes lineage graph
  construction, lineage warnings, extraction coverage, and artifact locations
  for one analysis run.
- **DatasetNode**: A deterministic representation of a dataset referenced or
  materialized within the repository, including canonical identity, source
  evidence, support status, and confidence limits.
- **TransformationNode**: A deterministic representation of a transformation
  step, query, model, or data-processing unit that consumes and produces
  datasets.
- **LineageEdge**: A directed data-flow relationship such as `CONSUMES` or
  `PRODUCES`, including source and target identifiers plus supporting evidence.
- **LineageSignal**: An extracted lineage fact from SQL, Python, YAML, or
  dbt-style inputs that may be definitive or partial depending on evidence
  quality.

## Repository and Language Scope *(mandatory for code intelligence work)*

- **Analysis Root**: The resolved local repository path returned by earlier
  repository preparation stages. Hydrologist only analyzes in-scope files and
  stage outputs associated with that root.
- **Excluded Inputs**: Secret-bearing files, generated outputs, vendored code,
  binaries, archives, images, media, PDFs, lockfiles, minified assets,
  oversized files, and paths already excluded by the manifest pipeline remain
  outside lineage extraction.
- **Language Routing**: Hydrologist consumes eligible SQL, Python, YAML, and
  dbt-style model inputs for lineage extraction. JavaScript/TypeScript,
  notebooks, and shell files may still appear in manifests or prior artifacts
  but are not required to provide full lineage extraction in this stage unless
  they surface deterministic lineage evidence through supported pathways.
- **Evidence Model**: SQL parsing, Python data-operation detection, and YAML
  reference extraction are static-analysis evidence sources with source path and
  line metadata where available. Any ambiguous lineage recovered from dynamic or
  incomplete sources must remain explicitly labeled as partial or inferential.
  This stage does not introduce LLM-derived lineage.
- **Output Locations**: Hydrologist writes only to project-controlled artifact
  locations under `.cartography`, including `lineage_graph.json`, lineage
  summaries, and run metadata updates. It does not modify analyzed source
  repositories.
- **Model Budget**: N/A. This stage does not introduce LLM or embedding usage.

## Assumptions

- Surveyor outputs and structural extraction artifacts already exist or can be
  produced earlier in the same analyze flow before Hydrologist executes.
- Dataset identities can be normalized from deterministic source cues such as
  table names, file-based models, or static API arguments, even when richer
  semantic resolution is deferred to later stages.
- Dynamic query generation and custom pipeline frameworks will often yield only
  partial lineage in this stage and should not block artifact generation.
- Deterministic artifact validation ignores run-specific identifiers and
  timestamps when comparing repeated outputs.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On an unchanged repository, repeated Hydrologist runs produce the
  same lineage graph contents, lineage summary ordering, and node-edge
  relationships in 100% of validation runs, excluding run-specific metadata.
- **SC-002**: On fixture repositories containing supported SQL, Python, and
  YAML lineage inputs, the Hydrologist stage emits lineage entities and edges
  for at least 95% of eligible deterministic lineage signals.
- **SC-003**: On repositories with malformed SQL, dynamic query construction,
  or partially supported pipeline definitions, the Hydrologist stage completes
  successfully and emits partial artifacts plus structured warnings in 100% of
  defined fixture scenarios.
- **SC-004**: On a mixed-language fixture repository, the CLI analyze flow runs
  Hydrologist after Surveyor and writes deterministic lineage artifacts under
  `.cartography` without requiring manual intervention.
