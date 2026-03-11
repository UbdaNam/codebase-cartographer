# Research: Brownfield Cartographer Stage 3 Repository Input Resolution and Structural Analysis

## Decision: Use a dedicated repository-preparation layer that canonicalizes inputs into a local analysis root

**Rationale**: Repository input resolution is a separate concern from discovery
and parsing. Isolating it allows the CLI and orchestrator to accept either a
local path or a Git URL while keeping downstream analyzers filesystem-based and
deterministic.

**Alternatives considered**:
- Let the orchestrator handle local paths and URLs inline.
  Rejected because it mixes preparation concerns with execution flow.
- Require users to clone repositories manually before analysis.
  Rejected because it breaks the Stage 3 user value and prevents deterministic
  reuse behavior.

## Decision: Prepare URL-based repositories under `.cartography/repos/` with shallow clone by default

**Rationale**: Project-controlled prepared repositories satisfy the
non-destructive constitution requirement and keep remote inputs reusable and
bounded. Shallow clone behavior reduces startup cost for large repositories and
can later be extended with refresh logic.

**Alternatives considered**:
- Clone into temporary directories outside the project artifact area.
  Rejected because it weakens determinism and artifact traceability.
- Always do a full clone.
  Rejected because it is unnecessarily expensive for large repositories.

## Decision: Reuse prepared repositories using a canonical repository identity and deterministic local path mapping

**Rationale**: Reuse avoids recloning and preserves a stable location for later
incremental strategies. Canonical identity also keeps artifact references
predictable.

**Alternatives considered**:
- Always reclone remote repositories.
  Rejected because it wastes time and bandwidth.
- Reuse repositories by last directory name only.
  Rejected because it is too collision-prone and ambiguous.

## Decision: Keep Stage 2 manifest eligibility authoritative for structural analysis scope

**Rationale**: Stage 2 already owns safe scanning, routing status, and
parse-eligibility decisions. Reusing that manifest avoids repeated full-tree
scans and prevents Stage 3 from drifting into a second discovery pipeline.

**Alternatives considered**:
- Let Stage 3 rescan the repository and decide scope independently.
  Rejected because it violates the performance and consistency principles.
- Parse every file regardless of manifest eligibility.
  Rejected because it breaks safety and bounded-work guarantees.

## Decision: Introduce a centralized LanguageRouter for parser configuration and extraction capability

**Rationale**: A single router keeps language normalization, parser selection,
and support-status handling deterministic across analyzers. It also creates a
clear seam for later Hydrologist or Semanticist expansion.

**Alternatives considered**:
- Hard-code language routing inside the tree-sitter analyzer.
  Rejected because it couples parsing and routing policy too tightly.
- Use file suffix checks ad hoc in each extraction routine.
  Rejected because it becomes inconsistent and hard to test.

## Decision: Produce typed structural records with evidence metadata and structured warnings

**Rationale**: Surveyor-ready outputs need more than raw AST fragments. Typed
records with symbol names, signatures, line metadata, support status, and
warning surfaces create trustworthy static-analysis artifacts that later stages
can consume directly.

**Alternatives considered**:
- Persist only raw AST dumps.
  Rejected because they are not stable user-facing artifacts and are harder for
  later stages to consume deterministically.
- Drop files that parse partially.
  Rejected because brownfield repositories require graceful degradation.

## Decision: Serialize deterministic structural artifacts such as `structural_index.json` and `ast_index.json`

**Rationale**: Deterministic payloads are required by the constitution and are
the cleanest bridge to future Surveyor and graph stages. Separate summary and
detail artifacts keep outputs readable while preserving enough structure for
later reuse.

**Alternatives considered**:
- Emit only logs or console summaries.
  Rejected because later stages need durable machine-readable artifacts.
- Emit one monolithic opaque blob.
  Rejected because it weakens diffability and partial-result inspection.
