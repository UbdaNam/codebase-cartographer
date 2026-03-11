# Feature Specification: Surveyor Agent

**Feature Branch**: `005-surveyor-agent`
**Created**: 2026-03-11
**Status**: Draft
**Input**: User description: "Build Stage 4 Surveyor agent for Brownfield
Cartographer. This stage should turn the structural extraction outputs into
architectural intelligence for large brownfield repositories. The Surveyor
agent should analyze module structure, import relationships, and repository
change history to produce a deterministic module graph and high-level
architecture signals. Stage 4 must include: - a Surveyor agent that consumes
the existing manifest, structural extraction outputs, and analysis state -
module-level structural analysis that materializes or updates ModuleNode
records for relevant source files - import graph construction for supported
code modules using a NetworkX directed graph - git velocity analysis that
computes recent change frequency per file over a configurable time window -
identification of high-velocity files and the high-velocity core using a
Pareto-style threshold - graph analytics including PageRank for architectural
hubs and strongly connected components for circular dependencies - initial dead
code candidate heuristics based on graph structure, visibility, and recent
usage signals - deterministic serialization of the module graph and survey
summary artifacts under .cartography - orchestrator and CLI integration so
analyze can run the Surveyor stage after structural extraction - tests for
graph construction, git velocity behavior, PageRank output, SCC detection, and
deterministic serialization This stage should work on large mixed-language
repositories and should gracefully handle missing git metadata, unresolved
imports, partial structural extraction, and dynamically difficult modules.
This stage should not yet implement SQL lineage extraction, YAML/dbt/Airflow
lineage semantics, semantic indexing, LangGraph workflows, or LLM
summarization. It should focus on the Surveyor's architectural map, module
graph, git velocity signals, and dead code candidate detection."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate an Architectural Module Map (Priority: P1)

As an engineer onboarding to a brownfield repository, I want analysis to turn
file inventory and structural extraction results into a deterministic module
graph so I can quickly see which modules exist, how they depend on each other,
and which parts of the codebase are structurally central.

**Why this priority**: The module graph is the core output that makes the
Surveyor stage useful and unlocks later graph, ranking, and query workflows.

**Independent Test**: Can be fully tested by running analysis on a supported
repository with structural outputs and verifying that module records,
dependency links, hub signals, and circular dependency groups are written to
project-controlled artifacts in a stable order.

**Acceptance Scenarios**:

1. **Given** a repository with supported modules and structural extraction
   outputs, **When** the Surveyor stage runs, **Then** it produces a
   deterministic module graph with module records and import relationships for
   in-scope files.
2. **Given** the same unchanged repository analyzed twice, **When** the
   Surveyor stage completes, **Then** the serialized module graph and survey
   summary remain stable across runs aside from run-specific metadata.

---

### User Story 2 - Surface Change and Risk Signals (Priority: P2)

As a maintainer triaging a large brownfield repository, I want the Surveyor
stage to highlight high-velocity modules, architectural hubs, circular
dependencies, and initial dead code candidates so I can focus review and
stabilization efforts on the parts of the system that matter most.

**Why this priority**: These signals convert raw structural data into practical
architectural intelligence and create immediate value for maintenance and
onboarding.

**Independent Test**: Can be fully tested by running analysis on repositories
with recent history and known dependency shapes, then verifying that velocity
signals, hub rankings, circular groups, and candidate dead code lists are
present in the summary outputs with deterministic ordering.

**Acceptance Scenarios**:

1. **Given** a repository with available recent change history, **When** the
   Surveyor stage runs, **Then** it calculates per-file recent change counts
   and identifies a high-velocity core using a defined threshold rule.
2. **Given** a repository with dependency cycles or isolated modules, **When**
   the Surveyor stage runs, **Then** it emits circular dependency groups,
   architectural hub rankings, and dead code candidate signals with supporting
   evidence.

---

### User Story 3 - Degrade Gracefully on Incomplete Inputs (Priority: P3)

As an engineer analyzing a messy mixed-language repository, I want the
Surveyor stage to continue producing partial architectural outputs when git
history is missing, imports are unresolved, or structural extraction is
partial, so analysis remains useful instead of failing outright.

**Why this priority**: Brownfield repositories are often incomplete, dynamic,
and inconsistent; resilient partial outputs are required for production use.

**Independent Test**: Can be fully tested by analyzing repositories with
missing git metadata, unresolved imports, and partial structural records, then
verifying that the stage emits structured warnings and partial artifacts
without crashing.

**Acceptance Scenarios**:

1. **Given** a repository without usable git metadata, **When** the Surveyor
   stage runs, **Then** it still emits the module graph and summary while
   recording that velocity analysis is partial or unavailable.
2. **Given** unresolved imports or partial structural extraction results,
   **When** the Surveyor stage runs, **Then** it preserves valid module and
   graph outputs, marks unresolved relationships explicitly, and records
   structured warnings instead of terminating the run.

### Edge Cases

- How does the stage behave when structural extraction exists for only a subset
  of supported files?
- What happens when repository history is shallow, unavailable, or contains too
  little data to calculate a meaningful recent velocity signal?
- What happens when imports are unresolved, ambiguous, or point outside the
  analysis root?
- How are generated, vendored, secret-bearing, binary, archived, oversized, or
  otherwise excluded files prevented from becoming modules or graph edges?
- How does the stage behave when a strongly connected component contains only
  partially supported modules?
- What partial outputs remain available when graph analytics succeeds but git
  velocity or dead code heuristics cannot be completed?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST run a Surveyor stage that consumes the existing
  manifest, structural extraction outputs, and analysis state for an analyzed
  repository.
- **FR-002**: System MUST materialize or update module-level records for
  relevant in-scope source files using the structural extraction outputs as the
  primary evidence source.
- **FR-003**: System MUST build a directed import/dependency graph for
  supported modules and preserve unresolved or partial dependency outcomes
  without failing the stage.
- **FR-004**: System MUST compute recent per-file change frequency over a
  configurable lookback window when usable repository history is available.
- **FR-005**: System MUST identify high-velocity files and a high-velocity core
  using a deterministic threshold rule applied to recent change activity.
- **FR-006**: System MUST compute architectural hub signals and circular
  dependency groupings from the module graph.
- **FR-007**: System MUST produce initial dead code candidate heuristics using
  available graph structure, visibility signals, and recent usage indicators
  without presenting the result as certain fact.
- **FR-008**: System MUST serialize the module graph and survey summary into
  deterministic project-controlled artifacts under `.cartography`.
- **FR-009**: System MUST integrate the Surveyor stage into orchestrated
  analysis so the CLI analyze flow can run it after structural extraction.
- **FR-010**: System MUST record structured warnings and partial-result status
  when git metadata is missing, imports are unresolved, or structural
  extraction is incomplete.
- **FR-011**: Specification MUST define analysis-root boundaries, excluded
  inputs, and secret-handling constraints for Surveyor outputs, including that
  secret file contents are never persisted into logs or artifacts.
- **FR-012**: Specification MUST define file-type routing expectations,
  including which structural outputs are eligible for module graph
  participation, which are partial, and which remain skipped or unsupported.
- **FR-013**: Specification MUST state evidence expectations, including source
  metadata for module and dependency records, deterministic artifacts, and the
  distinction between static structural evidence, graph-derived signals, and
  heuristic dead code inferences.
- **FR-014**: Specification MUST define non-destructive output locations for
  Surveyor artifacts, summaries, logs, cache, and any cloned repository state.
- **FR-015**: Specification MUST state automated test expectations for graph
  construction, change-frequency analysis, hub ranking, circular dependency
  detection, deterministic serialization, and graceful degradation behavior.
- **FR-016**: System MUST support large mixed-language repositories without
  repeated full-tree scans and without reprocessing files already excluded by
  the manifest or structural stages.

### Key Entities *(include if feature involves data)*

- **SurveyResult**: The stage-level output that summarizes module graph
  construction, graph analytics, velocity signals, warnings, and artifact
  locations for one analysis run.
- **ModuleNode**: A module-level architectural record for an in-scope source
  file or logical module, including identity, language, structural evidence,
  dependency context, and derived signals.
- **ModuleDependency**: A directed relationship between two modules, including
  resolved or unresolved dependency status and supporting evidence.
- **VelocitySignal**: A recent-change summary for a file or module over a
  defined lookback window, including counts and inclusion in the high-velocity
  core when applicable.
- **DeadCodeCandidate**: A heuristic result identifying a module that appears
  weakly referenced or unused, including supporting signals and confidence
  limits.

## Repository and Language Scope *(mandatory for code intelligence work)*

- **Analysis Root**: The resolved local repository path returned by earlier
  repository preparation stages. Surveyor only operates on in-scope modules and
  artifacts produced for that root.
- **Excluded Inputs**: Secret-bearing files, generated outputs, vendored code,
  binaries, archives, images, media, PDFs, lockfiles, minified assets,
  oversized files, and paths already excluded by the manifest pipeline remain
  outside Surveyor processing.
- **Language Routing**: Surveyor consumes structural outputs for supported code
  modules in Python, JavaScript, TypeScript, SQL, and YAML where structural
  extraction exists. Partially supported file types such as notebooks and shell
  files may appear in summaries or warnings but do not require complete module
  graph participation in this stage.
- **Evidence Model**: Module and dependency records use static structural
  evidence with source path and line metadata where available. Hub rankings,
  circular dependency groups, and high-velocity core membership are graph- or
  history-derived signals. Dead code candidates are heuristics and must remain
  explicitly labeled as inferential rather than definitive.
- **Output Locations**: Surveyor writes only to project-controlled artifact
  locations under `.cartography`, including module graph artifacts, survey
  summaries, and run metadata updates. It does not modify analyzed source
  repositories.
- **Model Budget**: N/A. This stage does not introduce LLM or embedding usage.

## Assumptions

- Structural extraction artifacts from the previous stage already exist or can
  be produced within the same analyze flow before Surveyor runs.
- Recent change frequency is based on repository history available at analysis
  time; missing or shallow history degrades the signal rather than blocking the
  stage.
- Dead code detection in this stage is heuristic-only and may require later
  confirmation from richer semantic analysis.
- Deterministic artifact comparison ignores run-specific identifiers and
  timestamps when validating stability.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On an unchanged repository, repeated Surveyor runs produce the
  same module graph contents, graph analytics outputs, and survey summary
  ordering in 100% of validation runs, excluding run-specific metadata values.
- **SC-002**: On a mixed-language fixture repository with supported structural
  outputs, the Surveyor stage emits module records and dependency relationships
  for at least 95% of eligible supported modules.
- **SC-003**: On repositories with usable recent history, the Surveyor stage
  produces a complete ranked high-velocity file list and high-velocity core in
  a single run without requiring manual intervention.
- **SC-004**: On repositories with missing git metadata, unresolved imports, or
  partial structural outputs, the Surveyor stage completes successfully and
  emits partial artifacts plus structured warnings in 100% of defined fixture
  scenarios.
