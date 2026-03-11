# Feature Specification: Brownfield Cartographer Stage 0 Foundation

**Feature Branch**: `001-bootstrap-cartographer-foundation`
**Created**: 2026-03-10
**Status**: Draft
**Input**: User description: "Build the Stage 0 foundation for Brownfield
Cartographer, a LangGraph-oriented multi-agent codebase intelligence system for
brownfield data and software repositories. This stage should create the
empty-repo foundation and architectural scaffolding needed for later
implementation of the Surveyor, Hydrologist, Semanticist, Archivist, and
Navigator agents. The system will eventually ingest a local repository path or
GitHub repository and produce a living, queryable map of architecture, data
flow, and semantic structure for rapid FDE onboarding. This foundation stage
should focus on the project skeleton and operational guardrails rather than
full analysis behavior. Stage 0 must include: project bootstrap for a
Python-based codebase; a clear src layout aligned to future agents, analyzers,
models, graph, and orchestration layers; configuration and settings
management; centralized ignore and safe-scanning boundaries for secret-bearing,
generated, vendored, binary, oversized, and irrelevant files; a repository
manifest concept that future stages can use for single-pass file inventory and
incremental analysis; a basic CLI entrypoint and orchestrator shell suitable
for future analyze and query workflows; logging, run metadata, and output
directory conventions for .cartography artifacts; test scaffolding and initial
tests for config, ignore rules, and manifest behavior; LangGraph-ready
architecture boundaries without implementing the full Navigator yet. This stage
must be designed for very large mixed-language repositories and must explicitly
avoid Python-only assumptions. It must support future language routing across
Python, SQL, YAML, JavaScript/TypeScript, JSON config, and notebooks. This
stage must not yet implement full AST parsing, lineage extraction, semantic
indexing, or LLM-based summarization. It should create the foundation that
makes those later stages clean, fast, and safe."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Start a Safe Foundation (Priority: P1)

As a platform engineer, I want a clean project foundation with explicit
operational guardrails so the team can begin building Brownfield Cartographer
without unsafe repository access, ad hoc structure, or ambiguous output
locations.

**Why this priority**: Without a safe and coherent foundation, every later
stage risks rework, inconsistent behavior, and unsafe scanning defaults.

**Independent Test**: A new contributor can inspect the generated project
layout, configuration entry points, scanning boundaries, and output
conventions, then confirm that the foundation is ready for future feature work
without implementing repository analysis.

**Acceptance Scenarios**:

1. **Given** a fresh checkout of the project, **When** a contributor reviews
   the repository layout and startup entrypoints, **Then** they can identify
   where future agents, analyzers, graph logic, models, and orchestration logic
   belong.
2. **Given** the Stage 0 foundation, **When** a contributor looks for runtime
   outputs and run metadata, **Then** the artifact locations and naming
   conventions are explicit and project-controlled.

---

### User Story 2 - Respect Repository Boundaries at Scale (Priority: P2)

As an operator preparing to scan a brownfield repository, I want centralized
ignore rules, safe-scanning boundaries, and a reusable inventory concept so
future scans stay fast, bounded, and safe even for very large mixed-language
repositories.

**Why this priority**: Repository-scale performance and safety are hard
requirements for brownfield codebase intelligence and must be built into the
foundation.

**Independent Test**: A contributor can review the boundary rules and manifest
concept and confirm that excluded content, path containment, and future
single-pass inventory behavior are defined before analysis logic exists.

**Acceptance Scenarios**:

1. **Given** a repository containing source files, generated assets, secrets,
   vendored content, and large binaries, **When** the Stage 0 rules are
   reviewed, **Then** excluded classes and safe-scanning limits are defined in
   one centralized place.
2. **Given** a very large mixed-language repository, **When** the future
   inventory approach is examined, **Then** it is clear how a single repository
   manifest can support bounded, incremental analysis instead of repeated full
   walks.

---

### User Story 3 - Extend the System Without Rebuilding It (Priority: P3)

As a future Cartographer developer, I want architecture boundaries, tests, and
workflow shells that anticipate later agent and query capabilities so new
stages can be added without restructuring the foundation.

**Why this priority**: The foundation must preserve the path to future agent
implementation, mixed-language routing, and query-driven onboarding outputs.

**Independent Test**: A contributor can map future work to existing seams for
agents, orchestration, manifesting, logging, and tests without needing to
rename major directories or replace core conventions.

**Acceptance Scenarios**:

1. **Given** the Stage 0 foundation, **When** a developer plans the Surveyor,
   Hydrologist, Semanticist, Archivist, or Navigator stages, **Then** there are
   clear extension points for those responsibilities.
2. **Given** later plans for queryable codebase maps, **When** a developer
   reviews the foundation, **Then** the structure preserves a clean path to
   future architecture, lineage, semantic, and onboarding artifacts.

### Edge Cases

- What happens when the target repository contains only excluded or unsupported
  files? The foundation must still support a safe no-op inventory outcome with
  clear run metadata.
- How does the system handle a repository path that tries to traverse outside
  the allowed analysis root? The foundation must define containment rules that
  reject escape attempts.
- What happens when a repository mixes supported, partially supported, skipped,
  and unsupported file types? The foundation must preserve explicit routing and
  status labeling rather than assuming one-language behavior.
- What happens when run outputs already exist from a prior execution? The
  foundation must define deterministic output placement and run metadata
  conventions that avoid ambiguous overwrites.
- How does the system behave when a repository is too large for expensive
  repeated discovery? The foundation must preserve a single-pass manifest
  concept suitable for future incremental reuse.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a clearly organized project foundation
  that defines where future agents, analyzers, models, graph logic, and
  orchestration responsibilities belong.
- **FR-002**: The system MUST provide a startup workflow that gives future
  contributors a consistent entrypoint for analysis-oriented and query-oriented
  commands without requiring full analysis behavior in Stage 0.
- **FR-003**: The system MUST centralize operational configuration so future
  stages use one source of truth for runtime settings, output locations, and
  scanning boundaries.
- **FR-004**: The system MUST define centralized ignore and safe-scanning rules
  that exclude secret-bearing, generated, vendored, binary, oversized, and
  otherwise irrelevant inputs by default.
- **FR-005**: The system MUST define analysis-root containment rules so future
  repository traversal cannot escape the intended scan boundary.
- **FR-006**: The system MUST define a repository manifest concept that can be
  reused by later stages for single-pass discovery and incremental analysis.
- **FR-007**: The system MUST define future language-routing expectations for
  Python, SQL, YAML, JavaScript/TypeScript, JSON configuration, and notebooks
  without assuming one language is the only first-class input.
- **FR-008**: The system MUST define logging, run metadata, and
  project-controlled artifact directory conventions for `.cartography` outputs.
- **FR-009**: The system MUST include test scaffolding and initial automated
  coverage for configuration behavior, ignore boundaries, and manifest-related
  behavior.
- **FR-010**: The system MUST preserve clear extension points for Surveyor,
  Hydrologist, Semanticist, Archivist, and a future Navigator capability
  without implementing their full behavior in this stage.
- **FR-011**: The system MUST explicitly exclude full AST parsing, lineage
  extraction, semantic indexing, and model-based summarization from Stage 0
  scope.
- **FR-012**: The system MUST be suitable for very large brownfield
  repositories by favoring bounded discovery, reusable metadata, and safe
  partial outcomes over repeated or unbounded work.
- **FR-013**: The system MUST keep all derived outputs, caches, and logs inside
  project-controlled directories and MUST treat analyzed repositories as
  read-only targets.

### Key Entities *(include if feature involves data)*

- **Repository Manifest**: A durable inventory record describing candidate
  inputs, their classifications, and metadata needed for future bounded and
  incremental analysis.
- **Scanning Policy**: The centralized definition of included and excluded
  content classes, path-containment expectations, and safety guardrails.
- **Run Record**: The metadata describing an execution attempt, its scope,
  timing, output locations, and outcome status.
- **Agent Boundary**: The declared responsibility seam for a current or future
  agent, analyzer, graph layer, or orchestration component.

## Repository and Language Scope *(mandatory for code intelligence work)*

- **Analysis Root**: A local repository path or a repository materialized from
  a remote source, always constrained to an explicit analysis root.
- **Excluded Inputs**: Secret-bearing files, generated assets, vendored
  content, binaries, archives, images, oversized files, lockfiles, and other
  non-source or unsafe inputs are excluded by default.
- **Language Routing**: The foundation must preserve explicit routing for
  Python, SQL, YAML, JavaScript/TypeScript, JSON configuration, and notebooks,
  plus status labeling for partially supported, skipped, and unsupported file
  types.
- **Evidence Model**: Stage 0 produces structural and operational definitions,
  run metadata, and inventory-oriented records only; it does not yet produce
  deep code findings, lineage evidence, semantic assertions, or model-derived
  summaries.
- **Output Locations**: All logs, run metadata, caches, manifests, and future
  derived artifacts live under project-controlled `.cartography` directories.
- **Model Budget**: No model-backed analysis is in scope for Stage 0.

## Assumptions

- The foundation is intended for internal product builders and future operators,
  not yet for external end users.
- Local repository input is in scope immediately; remote repository support is
  defined at the boundary level but does not require full ingestion behavior in
  Stage 0.
- Contributors need clear structure and guardrails now so later analysis stages
  can be added incrementally instead of via a large redesign.
- The system must optimize for brownfield repositories where mixed languages,
  generated files, and inconsistent repository hygiene are normal.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new contributor can identify the intended home for future
  agents, analyzers, graph logic, orchestration, and outputs within 15 minutes
  of opening the repository.
- **SC-002**: The Stage 0 foundation defines one centralized source of truth
  for scanning boundaries and output conventions, with no conflicting locations
  or duplicate rule sets.
- **SC-003**: Reviewers can verify from the project artifacts alone that
  secret-bearing, generated, vendored, binary, oversized, and irrelevant inputs
  are excluded by default before analysis logic is added.
- **SC-004**: Reviewers can verify that the foundation supports at least the
  six declared language families and distinguishes supported, partially
  supported, skipped, and unsupported inputs.
- **SC-005**: Initial automated tests cover configuration behavior, ignore
  boundaries, and manifest-oriented behavior with all tests passing in a clean
  environment.
- **SC-006**: The documented Stage 0 scope leaves no ambiguity that deep
  parsing, lineage extraction, semantic indexing, and model-based summarization
  are deferred to later stages.
