# Feature Specification: Brownfield Cartographer Stage 2 Repository Inventory

**Feature Branch**: `003-repo-inventory`
**Created**: 2026-03-11
**Status**: Draft
**Input**: User description: "Build Stage 2 file discovery and language
classification for Brownfield Cartographer, a LangGraph-oriented multi-agent
codebase intelligence system for large brownfield repositories. This stage
should turn the foundational repo-scanning setup into a production-minded
repository inventory subsystem that is safe, deterministic, and ready for later
analyzers. Stage 2 must include: a single-pass repository discovery workflow
that walks the target repo once and builds a deterministic manifest;
centralized file classification that identifies language, support status, and
analysis eligibility; explicit mixed-language support for Python, SQL, YAML,
JavaScript, TypeScript, JSON config, notebooks, and shell files at minimum;
structured handling for supported, partially supported, skipped, and
unsupported files; safe exclusion of secret-bearing, generated, vendored,
binary, archived, oversized, lockfile, minified, and irrelevant files before
content parsing; manifest records that are future-ready for tree-sitter
parsing, SQL lineage extraction, config parsing, and incremental re-analysis;
summary statistics and serialization for repository inventory outputs inside
.cartography; tests using fixture repositories that simulate mixed-language and
large-repo conditions. This stage should be designed for very large polyglot
repositories and should avoid repeated filesystem walks or unnecessary file
reads. It should preserve deterministic output ordering and stable
classification behavior across runs. This stage should not yet implement AST
parsing, SQL AST lineage extraction, graph algorithms, LangGraph workflows, or
LLM summarization. It should focus only on robust discovery, classification,
manifest generation, and inventory serialization."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Produce A Deterministic Repo Inventory (Priority: P1)

As a Cartographer developer, I want a single repository inventory pass that
produces a deterministic manifest so later analyzers can start from one stable
source of truth instead of re-walking the filesystem.

**Why this priority**: Later Surveyor, Hydrologist, and config analyzers depend
on a reliable inventory surface. If discovery is unstable or repeated, every
later stage inherits wasted work and inconsistent inputs.

**Independent Test**: A developer can run discovery against the same unchanged
repository twice and confirm that the manifest records, ordering, and summary
totals are identical.

**Acceptance Scenarios**:

1. **Given** an unchanged repository under an analysis root, **When** inventory
   generation runs, **Then** it emits one deterministic manifest containing all
   discovered in-scope files in stable order.
2. **Given** a repository with nested directories and mixed file classes,
   **When** discovery completes, **Then** the output includes per-file inventory
   records and summary statistics without requiring later stages to walk the
   repository again.

---

### User Story 2 - Classify Mixed-Language Files Consistently (Priority: P2)

As a future analyzer author, I want each discovered file to have stable
language, support-status, and analysis-eligibility classification so later
stages can route work correctly across mixed-language brownfield repositories.

**Why this priority**: The system's value depends on understanding which files
are analyzable, partially analyzable, unsupported, or safely skipped before any
parser or lineage logic is introduced.

**Independent Test**: A developer can inventory a fixture repository containing
Python, SQL, YAML, JavaScript, TypeScript, JSON config, notebooks, shell files,
and excluded inputs and confirm that every sample file is classified
consistently across repeated runs.

**Acceptance Scenarios**:

1. **Given** a repository containing the required supported and partially
   supported file classes, **When** classification runs, **Then** each file is
   assigned a deterministic language label, support status, and analysis
   eligibility result.
2. **Given** files that are unsupported but still visible during discovery,
   **When** the manifest is produced, **Then** those files remain represented as
   unsupported rather than being silently dropped.

---

### User Story 3 - Enforce Safe Inventory Boundaries At Scale (Priority: P3)

As an operator running the Cartographer on a large brownfield repository, I
want secret-bearing, irrelevant, generated, and oversized files excluded before
content parsing so inventory stays safe, bounded, and useful under real-world
conditions.

**Why this priority**: Brownfield repositories include noise, secrets, vendored
trees, and machine-generated assets. Safe exclusion and structured skip reasons
are required to keep later analysis trustworthy and cost-bounded.

**Independent Test**: A developer can run inventory on a fixture repository
with excluded directories, minified assets, lockfiles, binaries, archives, and
oversized files and confirm that the system logs deterministic skip outcomes
without crashing or reading disallowed inputs as source files.

**Acceptance Scenarios**:

1. **Given** secret-bearing, generated, vendored, binary, archived, or
   oversized files under the analysis root, **When** inventory runs, **Then**
   those files are excluded from parse-eligible inputs with structured reasons.
2. **Given** a very large repository snapshot, **When** discovery and
   classification run, **Then** the system completes using one filesystem walk
   and returns partial-but-valid inventory output even when some files are
   skipped or unsupported.

### Edge Cases

- What happens when a file matches both a supported extension and an exclusion
  rule such as secret-sensitive naming or size limits? Exclusion must win and
  the manifest must record the skip reason deterministically.
- What happens when a notebook, shell file, or config file is recognized but is
  not yet fully analyzable by later stages? The inventory must represent it as
  partially supported or unsupported without ambiguity.
- What happens when repository traversal encounters symlinks, escaped paths, or
  paths outside the analysis root? The system must not traverse beyond the
  analysis root and must record a bounded outcome.
- What happens when a repository contains many irrelevant or excluded files? The
  summary must still reflect total candidates, skipped categories, and
  parse-eligible files without failing the inventory run.
- What happens when the same repository snapshot is inventoried repeatedly? The
  manifest ordering and classification results must remain stable across runs.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST walk the target repository once per inventory run
  and produce a deterministic manifest from that single discovery pass.
- **FR-002**: The system MUST centrally classify each discovered file by
  language, support status, and analysis eligibility.
- **FR-003**: The system MUST support explicit classification for Python, SQL,
  YAML, JavaScript, TypeScript, JSON configuration, notebooks, and shell files
  at minimum.
- **FR-004**: The system MUST represent supported, partially supported,
  skipped, and unsupported files as distinct deterministic outcomes.
- **FR-005**: The system MUST exclude secret-bearing, generated, vendored,
  binary, archived, oversized, lockfile, minified, and otherwise irrelevant
  files before they are treated as parse-eligible source inputs.
- **FR-006**: The inventory manifest MUST preserve future-ready metadata needed
  for later structural parsing, SQL lineage extraction, config analysis, and
  incremental re-analysis.
- **FR-007**: The system MUST produce repository inventory summary statistics
  and serialize inventory outputs into project-controlled `.cartography`
  locations.
- **FR-008**: The system MUST avoid repeated filesystem walks and unnecessary
  file reads during discovery and classification.
- **FR-009**: The system MUST preserve deterministic manifest ordering and
  stable classification behavior across repeated runs on the same repository
  snapshot.
- **FR-010**: The system MUST include automated tests covering mixed-language
  discovery, exclusion behavior, deterministic output, summary statistics, and
  large-repository-like fixture conditions.
- **FR-011**: Specification MUST define analysis-root boundaries, excluded
  inputs, and secret-handling constraints relevant to repository inventory.
- **FR-012**: Specification MUST define file-type routing expectations,
  including fully supported, partially supported, skipped, and unsupported
  classes.
- **FR-013**: Specification MUST state evidence expectations for inventory
  outputs, including source path metadata, deterministic artifacts, and clear
  distinction from later graph or LLM-derived outputs.
- **FR-014**: Specification MUST define non-destructive output locations and
  any cache, log, or artifact directories used by inventory generation.
- **FR-015**: Specification MUST state automated test expectations and
  repository-scale performance boundaries for discovery and classification work.
- **FR-016**: The system MUST exclude AST parsing, SQL AST lineage extraction,
  graph algorithms, LangGraph workflows, and LLM summarization from Stage 2
  scope.

### Key Entities *(include if feature involves data)*

- **Inventory Record**: A per-file repository record that captures relative
  path, file size, modified time, classification outcome, and future-ready
  analysis metadata.
- **Repository Manifest**: A deterministic inventory container holding ordered
  file records plus repository-level summary statistics.
- **Classification Decision**: A structured decision describing file language,
  support status, analysis eligibility, and any skip or exclusion reason.
- **Inventory Summary**: Aggregate counts and byte totals describing candidates,
  parse-eligible files, skipped files, unsupported files, and bounded scan
  totals.
- **Inventory Output Artifact**: A project-controlled serialized output derived
  from repository discovery for later analyzers and incremental workflows.

## Repository and Language Scope *(mandatory for code intelligence work)*

- **Analysis Root**: Inventory applies to a local repository path or a
  repository materialized from a remote source, always bounded to an explicit
  analysis root with no traversal beyond that root.
- **Excluded Inputs**: Secret-bearing, generated, vendored, binary, archived,
  lockfile, minified, oversized, cache, build, dependency, and otherwise
  irrelevant files are excluded from parse-eligible inputs but still reflected
  in structured inventory outcomes when encountered.
- **Language Routing**: The inventory must explicitly identify Python, SQL,
  YAML, JavaScript, TypeScript, JSON configuration, notebooks, and shell files,
  and must preserve stable routing semantics for supported, partially
  supported, skipped, and unsupported classes.
- **Evidence Model**: Stage 2 outputs are inventory-derived and file-system
  grounded. They must preserve source path metadata and deterministic
  classification evidence, but they do not yet include graph inference or LLM
  inference.
- **Output Locations**: Inventory outputs are written only to project-controlled
  `.cartography` artifact locations and must remain non-destructive to the
  analyzed repository.
- **Model Budget**: No LLM or embedding execution is in scope for Stage 2.

## Assumptions

- Stage 0 already provides baseline safe-scanning settings, artifact
  directories, and manifest-related foundations that Stage 2 will strengthen
  into a production-minded inventory subsystem.
- Later analyzers will depend on Stage 2 records rather than re-reading the
  repository blindly, so discovery and classification stability are primary
  design goals.
- Mixed-language repositories commonly include unsupported or partially
  supported files, so explicit non-success states are first-class outputs rather
  than exceptional cases.
- Repositories may be large and messy, so bounded work and deterministic
  partial outputs are more valuable than brittle completeness.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Repeated inventory runs against the same unchanged repository
  snapshot produce identical manifest record ordering and identical summary
  totals.
- **SC-002**: Fixture repositories covering the minimum supported language/file
  classes classify every in-scope sample file into the same language and
  support-status outcome across repeated runs.
- **SC-003**: Excluded secret-bearing, generated, vendored, binary, archived,
  minified, lockfile, and oversized sample files never appear as parse-eligible
  inventory inputs in automated tests.
- **SC-004**: Inventory serialization produces project-controlled `.cartography`
  outputs with stable structure and summary statistics that reviewers can
  compare across runs.
- **SC-005**: Automated tests pass for mixed-language discovery, exclusion
  behavior, deterministic manifest generation, and large-repository-like fixture
  scenarios in a clean environment.
