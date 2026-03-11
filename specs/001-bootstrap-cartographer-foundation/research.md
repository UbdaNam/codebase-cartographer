# Phase 0 Research: Brownfield Cartographer Stage 0 Foundation

## Decision: Use Python 3.11+ with uv for the Stage 0 foundation

**Rationale**: Python 3.11+ provides mature typing support, good developer
ergonomics, and compatibility with the planned CLI, configuration, and testing
tooling. `uv` keeps environment and dependency management fast and
deterministic, which matches the repository-scale and reproducibility goals.

**Alternatives considered**:
- Python 3.10: viable, but less aligned with the stated technical direction.
- Poetry or pip-tools: workable, but slower and less streamlined for the
  requested bootstrap workflow.

## Decision: Use a modular single-project `src/` layout with interface-first boundaries

**Rationale**: A single-project layout keeps Stage 0 simple while preserving
clear seams between orchestration, analyzers, models, graph concerns, index
concerns, and future agent responsibilities. It supports isolated testing and
prevents early coupling between orchestration and scanning logic.

**Alternatives considered**:
- Monolithic module tree: rejected because it would blur future agent and
  analyzer boundaries.
- Multi-package workspace: rejected for Stage 0 because it adds packaging
  overhead before the domain boundaries are exercised.

## Decision: Use Typer for the initial CLI surface

**Rationale**: Typer provides a clean path to documented command interfaces for
placeholder `analyze` and `query` workflows while remaining lightweight enough
for a Stage 0 foundation.

**Alternatives considered**:
- argparse: lighter, but less ergonomic for a growing multi-command CLI.
- Click: viable, but Typer gives simpler typed-command ergonomics for this
  foundation.

## Decision: Use Pydantic for typed settings and typed records where validation matters

**Rationale**: Stage 0 requires centralized, strongly typed configuration with
easy future overrides via environment variables or config files. Pydantic
provides validation, serialization, and predictable defaults for settings and
selected runtime records.

**Alternatives considered**:
- Pure dataclasses everywhere: simpler, but weaker for settings validation and
  override ergonomics.
- Custom config parsing: rejected because it duplicates validation logic and
  increases maintenance cost.

## Decision: Use dataclasses or Pydantic models for manifest and run metadata records

**Rationale**: Manifest records and run metadata need deterministic structure,
clear serialization, and easy testability. Typed record models support stable
output ordering and future incremental extensions.

**Alternatives considered**:
- Untyped dictionaries: rejected because they make contracts less reliable and
  harder to evolve safely.
- ORM-backed storage: out of scope for Stage 0 and unnecessary for filesystem
  artifact persistence.

## Decision: Centralize safe-scanning logic in a dedicated ignore policy service

**Rationale**: The constitution requires secret-bearing, generated, vendored,
binary, archived, minified, lockfile, cache, virtualenv, git, and oversized
files to be excluded before contents are read. A dedicated policy service makes
these rules deterministic, testable, and reusable across future manifesting and
analysis stages.

**Alternatives considered**:
- Ad hoc ignore checks inside each workflow: rejected because it duplicates
  rules and risks inconsistent skip behavior.
- Tool-specific ignore files only: rejected because Stage 0 needs structured
  skip reasons and internal policy guarantees.

## Decision: Build a single-pass manifest abstraction with deterministic output ordering

**Rationale**: Large brownfield repositories require an inventory layer that
avoids repeated repo walks. A single-pass manifest with support status,
relative paths, file metadata, and future hash strategy hooks supports both
bounded Stage 0 execution and later incremental analysis.

**Alternatives considered**:
- Full scan per analyzer: rejected because it violates the performance
  principles.
- Database-backed index in Stage 0: rejected because it adds unnecessary
  operational weight before the manifest contract is stabilized.

## Decision: Store all Stage 0 outputs under `.cartography/`

**Rationale**: Project-controlled artifact placement is required for
non-destructive operation. A dedicated `.cartography/` tree keeps run metadata,
future cache material, and logs separate from analyzed repositories.

**Alternatives considered**:
- Writing beside the analyzed repository: rejected because it violates
  non-destructive boundaries.
- Scattered temp directories: rejected because they make runs harder to audit
  and reproduce.

## Decision: Keep Stage 0 explicitly narrow and exclude deep analysis subsystems

**Rationale**: The goal is to create safe, fast scaffolding for later work, not
to partially implement parsing, lineage, graph orchestration, embeddings, or
LLM behaviors. Holding the boundary now reduces architectural churn later.

**Alternatives considered**:
- Starting tree-sitter or lineage extraction immediately: rejected because it
  would distract from the foundational contracts and guardrails.
- Adding LangGraph flows in Stage 0: rejected because the architecture should
  be ready for them without committing to premature workflow logic.
