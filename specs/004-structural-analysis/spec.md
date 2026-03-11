# Feature Specification: Brownfield Cartographer Stage 3 Repository Input Resolution and Structural Analysis

**Feature Branch**: `004-structural-analysis`
**Created**: 2026-03-11
**Status**: Draft
**Input**: User description: "Build Stage 3 repository input resolution and multi-language structural analysis for Brownfield Cartographer."

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Resolve Repository Input For Analysis (Priority: P1)

As an engineer onboarding to a brownfield system, I want to provide either a
local repository path or a Git repository URL and receive a prepared local
analysis root so I can start the analysis flow without manual repository setup.

**Why this priority**: Analysis cannot begin until the system can consistently
resolve input into a safe local repository path. This is the minimum viable
entrypoint for later Surveyor-stage work.

**Independent Test**: Can be fully tested by submitting one local path input
and one Git URL input, then verifying that both produce a valid local analysis
root and reusable preparation metadata without running later extraction stages.

**Acceptance Scenarios**:

1. **Given** a valid local repository path, **When** the user starts analysis,
   **Then** the system MUST validate the path, keep traversal within that root,
   and return that local root for downstream analysis.
2. **Given** a valid Git repository URL, **When** the user starts analysis,
   **Then** the system MUST prepare a safe local working copy and return its
   local root for downstream analysis.
3. **Given** a previously prepared local working copy for the same repository
   input, **When** the user starts analysis again, **Then** the system MUST
   reuse or refresh that prepared copy deterministically rather than creating
   ambiguous duplicate working locations.

---

### User Story 2 - Extract Structural Facts Across Mixed Languages (Priority: P2)

As an engineer exploring a large brownfield repository, I want structural
analysis artifacts that describe imports, public functions, classes, and
signatures across supported languages so I can understand module boundaries
before graph and ranking stages exist.

**Why this priority**: Once repository input is resolved, structural extraction
delivers the first high-value analysis artifact that future Surveyor and graph
stages depend on.

**Independent Test**: Can be fully tested by analyzing a mixed-language fixture
repository and verifying deterministic structural output records with source
paths and line metadata for supported files.

**Acceptance Scenarios**:

1. **Given** an in-scope manifest containing supported source files, **When**
   structural analysis runs, **Then** the system MUST emit deterministic
   per-file structural records for supported files with source-path evidence
   and line metadata where available.
2. **Given** a mixed-language repository containing Python, SQL, YAML,
   JavaScript, and TypeScript files, **When** structural analysis runs,
   **Then** the system MUST apply explicit language routing and extract the
   structural fields supported for each language without assuming Python-only
   behavior.

---

### User Story 3 - Preserve Safe Partial Results Under Brownfield Conditions (Priority: P3)

As an engineer analyzing a messy production repository, I want malformed,
unsupported, partially supported, and dynamically difficult files to degrade
gracefully so I still get usable structural artifacts instead of a failed run.

**Why this priority**: Brownfield repositories are rarely clean. Safe partial
results are required for trustworthy production use and for later agents that
must reason about incomplete coverage.

**Independent Test**: Can be fully tested by analyzing a fixture repository
with malformed, unsupported, and partially supported inputs and verifying that
the run completes with structured partial outputs, warnings, and deterministic
artifact contents.

**Acceptance Scenarios**:

1. **Given** a repository containing unsupported, partially supported, or
   malformed files, **When** structural analysis runs, **Then** the system MUST
   skip or downgrade those files with structured reasons and continue emitting
   partial results for the rest of the repository.
2. **Given** excluded, secret-bearing, vendored, binary, or oversized files,
   **When** structural analysis runs, **Then** the system MUST respect manifest
   eligibility boundaries and MUST NOT persist secret contents into artifacts
   or logs.

---

### Edge Cases

- What happens when a Git repository URL cannot be prepared locally because the
  repository is unreachable, invalid, or previously prepared in a stale state?
- What happens when a local path exists but is not a repository root, is
  outside the allowed analysis root, or resolves through unexpected symlinks?
- How does the system behave when a file type is recognized but only partially
  supported for structural extraction?
- How does the system behave when a supported file is malformed, dynamically
  difficult, or produces incomplete structural results?
- What happens when excluded, secret-bearing, vendored, binary, minified,
  unsupported, or oversized files are present in the manifest?
- What partial outputs remain available when one language extractor fails but
  others succeed?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept either a local repository path or a Git
  repository URL as analysis input.
- **FR-002**: System MUST resolve every accepted repository input into a single
  prepared local repository root for downstream analysis.
- **FR-003**: System MUST validate repository inputs before analysis begins and
  return structured preparation errors for invalid, unreachable, or unsafe
  inputs.
- **FR-004**: System MUST reuse or deterministically refresh previously
  prepared local working copies for the same repository input instead of
  creating ambiguous duplicate preparation states.
- **FR-005**: System MUST analyze only files that are marked in-scope and
  parse-eligible by the manifest and prior safety rules.
- **FR-006**: System MUST perform structural extraction across supported
  languages and emit module-level facts needed by the future Surveyor stage,
  including imports, public functions, classes, and signatures where
  available.
- **FR-007**: System MUST produce typed structural records and typed analysis
  state updates that preserve per-file extraction outcomes, warnings, and
  partial-result signals.
- **FR-008**: System MUST attach evidence metadata to structural findings,
  including source path and line information where available, and MUST
  distinguish deterministic static analysis output from later graph or
  model-derived output classes.
- **FR-009**: System MUST serialize structural artifacts deterministically into
  project-controlled `.cartography` output locations for later Surveyor and
  graph stages.
- **FR-010**: System MUST gracefully handle unsupported, partially supported,
  malformed, or dynamically difficult files by recording structured outcomes
  and continuing the run where safe to do so.
- **FR-011**: System MUST define analysis-root boundaries, excluded inputs, and
  secret-handling constraints for repository preparation and structural
  extraction.
- **FR-012**: System MUST define file-type routing expectations, including
  fully supported, partially supported, skipped, and unsupported classes for
  repository input preparation and structural extraction.
- **FR-013**: System MUST preserve non-destructive behavior by treating the
  analyzed repository as read-only and keeping prepared copies, cache, logs,
  and derived artifacts in project-controlled locations.
- **FR-014**: System MUST include automated tests for local path inputs, Git
  URL inputs, clone or reuse behavior, language routing, structural extraction,
  graceful degradation, and deterministic artifact generation.

### Key Entities *(include if feature involves data)*

- **Repository Input**: A user-provided local path or Git repository URL that
  identifies the repository to analyze.
- **Prepared Repository**: The validated local analysis root produced from a
  repository input, including preparation status and reuse metadata.
- **Structural Record**: A typed per-file analysis result describing extracted
  module-level facts, evidence, status, and partial-result details.
- **Structural Artifact**: A deterministic persisted output that groups
  structural records, metadata, and run-level summary information for later
  Surveyor and graph stages.
- **Structural Analysis State**: Shared run state that tracks which manifest
  records were analyzed, which were skipped or downgraded, and what structured
  warnings or partial outcomes were produced.

### Assumptions

- Git repository URLs are prepared into a project-controlled local working
  location before any downstream analysis begins.
- Structural extraction is limited to module-level facts and does not attempt
  ranking, velocity analysis, dead code detection, lineage extraction, or
  semantic summarization in this stage.
- Recognized but partially supported file types may contribute bounded
  structural metadata without being treated as fully supported.
- If line information is unavailable for a valid extracted fact, the system
  still emits the fact with the strongest available evidence metadata rather
  than dropping the entire file result.

## Repository and Language Scope *(mandatory for code intelligence work)*

- **Analysis Root**: The validated local repository root produced from either a
  user-supplied local path or a prepared local working copy for a Git URL.
- **Excluded Inputs**: Secret-bearing, vendored, generated, binary, archived,
  minified, oversized, lockfile, irrelevant, or otherwise manifest-ineligible
  files remain excluded from structural parsing by existing scanning rules.
- **Language Routing**: Python, SQL, YAML, JavaScript, and TypeScript are
  within the primary structural extraction scope; notebooks and shell files are
  recognized but may be only partially supported; other file types remain
  skipped or unsupported unless explicitly routed.
- **Evidence Model**: Stage 3 outputs are deterministic static analysis
  artifacts with source path and line metadata where available; they MUST NOT
  be presented as graph inference or LLM inference outputs.
- **Output Locations**: Prepared repository working locations, structural
  artifacts, cache, and logs MUST remain inside project-controlled directories,
  including `.cartography`.
- **Model Budget**: N/A for this stage. No LLM or embedding budget is consumed
  by repository preparation or structural extraction.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can start analysis from either a valid local repository
  path or a valid Git repository URL and receive a prepared local analysis root
  in one command without manual repository setup.
- **SC-002**: Repeated Stage 3 runs against the same unchanged repository input
  produce the same structural artifact ordering, the same routed file counts,
  and the same extracted record counts.
- **SC-003**: On a mixed-language fixture repository containing Python, SQL,
  YAML, JavaScript, and TypeScript files, structural analysis emits file-level
  results for at least 95% of files that are marked supported by the manifest.
- **SC-004**: When partially supported, unsupported, malformed, or excluded
  files are present, the run still completes and reports structured degraded
  outcomes instead of failing the entire repository analysis.
