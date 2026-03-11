<!--
Sync Impact Report
- Version change: template-unset -> 1.0.0
- Modified principles:
  - Principle slot 1 -> I. Architecture-First Multi-Agent Design
  - Principle slot 2 -> II. Large-Repository Performance
  - Principle slot 3 -> III. Security and Safe Scanning Boundaries
  - Principle slot 4 -> IV. Mandatory Multi-Language Support
  - Principle slot 5 -> V. Evidence and Trustworthiness
  - added VI. Graceful Degradation
  - added VII. Testing and Developer Quality
  - added VIII. Non-Destructive Operation
  - added IX. Living-Context Deliverables
  - added X. Cost Discipline
- Added sections:
  - Operational Boundaries
  - Delivery Workflow and Quality Gates
- Removed sections: none
- Templates requiring updates:
  - updated: .specify/templates/plan-template.md
  - updated: .specify/templates/spec-template.md
  - updated: .specify/templates/tasks-template.md
  - updated: .specify/templates/agent-file-template.md
  - updated: README.md
- Follow-up TODOs:
  - TODO(RATIFICATION_DATE): Initial ratification date is not recorded in repo history.
-->
# codebase-cartographer Constitution

## Core Principles

### I. Architecture-First Multi-Agent Design
The system MUST be designed as a multi-agent architecture centered on Surveyor,
Hydrologist, Semanticist, Archivist, and a later Navigator query agent. Shared
contracts, typed schemas, and deterministic artifacts MUST be preferred over ad
hoc scripts or implicit data exchange. All new stages and interfaces MUST
preserve a clean path to a central knowledge graph and LangGraph-based
orchestration. Rationale: architecture drift at early stages makes later agent
coordination, replayability, and graph integration expensive to recover.

### II. Large-Repository Performance
The system MUST treat large-repository performance as a hard requirement for
very large brownfield repositories, including repositories with the size and
messiness of Apache Airflow examples and larger. File discovery MUST avoid
repeated repository walks, and expensive work MUST be staged, bounded, and
cache-friendly. Incremental analysis MUST be treated as a first-class
architectural concern from the beginning, even before full incremental
execution is implemented. Rationale: repeated full-repo scans and unbounded
pipelines collapse under realistic enterprise repository scale.

### III. Security and Safe Scanning Boundaries
Secret-bearing, generated, vendored, binary, and irrelevant files MUST be
excluded by default from analysis. The system MUST NOT parse `.env`, `.env.*`,
`.git/`, `node_modules/`, `venv/`, `.venv/`, `dist/`, `build/`,
`__pycache__/`, lockfiles, minified assets, binaries, archives, images, or
oversized files as source inputs. The system MUST never persist secret file
contents into generated artifacts or logs, and repository traversal MUST NOT
escape the configured analysis root. Rationale: safe defaults are mandatory for
production scanning and limit both data leakage and accidental filesystem
reach.

### IV. Mandatory Multi-Language Support
The system MUST be built for mixed-language brownfield repositories and MUST
NOT assume Python-only inputs. The architecture MUST explicitly support Python,
SQL, YAML, JavaScript/TypeScript, JSON configuration, and notebooks, with a
testable distinction between fully supported, partially supported, skipped, and
unsupported file types. Language routing MUST be explicit, deterministic, and
covered by automated tests. Rationale: real production repositories mix code,
configuration, orchestration, and analytical assets that require different
handling rules.

### V. Evidence and Trustworthiness
Outputs MUST clearly distinguish static analysis, graph inference, and LLM
inference. Findings MUST be evidence-backed wherever possible and include
source path and line metadata when available. Deterministic serialization,
stable IDs, and reproducible output ordering are required for all durable
artifacts. Rationale: consumers need to know what is proven, what is inferred,
and whether an artifact can be diffed and trusted across runs.

### VI. Graceful Degradation
The system MUST log and skip unparseable, unsupported, oversized, or
dynamically unresolved inputs instead of crashing the full run. Partial results
MUST be preferred over failure. Errors and skip outcomes MUST be structured,
inspectable, and testable so downstream agents can reason about missing or weak
coverage. Rationale: brownfield repositories are messy; brittle pipelines are
not acceptable.

### VII. Testing and Developer Quality
Every stage MUST include automated tests. New and modified modules MUST be
typed where practical, modular, and documented at the public-interface level.
Interfaces MUST be designed so analyzers, agents, and storage layers can be
tested independently. Rationale: this system spans static analysis,
orchestration, and storage concerns; quality depends on strong seams and
repeatable tests.

### VIII. Non-Destructive Operation
The analyzed target repository MUST be treated as read-only from the
Cartographer's perspective. Generated outputs, caches, logs, and derived
artifacts MUST stay inside project-controlled output directories. No feature
may require modifying target repository contents to complete an analysis run.
Rationale: trust in repository intelligence tooling depends on strict
non-destructive behavior.

### IX. Living-Context Deliverables
The system MUST preserve the path toward a living, queryable map of codebase
architecture, lineage, and semantic structure for rapid FDE onboarding. Early
design choices MUST support future production of `CODEBASE.md`,
`onboarding_brief.md`, `lineage_graph.json`, `semantic_index`, and
`cartography_trace.jsonl`. Rationale: local optimizations that block these
deliverables undermine the product objective.

### X. Cost Discipline
LLM and embedding usage MUST be bounded, measurable, and introduced only
through explicit interfaces and budgets. Static analysis and graph methods MUST
be preferred whenever they can answer a question reliably. Plans and
implementations MUST identify when model-backed work is invoked, how it is
metered, and what fallback exists when budgets are exhausted. Rationale: cost
control and predictable execution are product requirements, not operational
afterthoughts.

## Operational Boundaries

- Analysis roots MUST be explicit and all traversal logic MUST enforce root
  containment.
- Discovery pipelines MUST produce reusable manifests or equivalent cached
  inventories before expensive parsing begins.
- Supported-file policies MUST record whether each file type is fully
  supported, partially supported, skipped, or unsupported, and the reason for
  that status.
- Durable artifacts MUST be written deterministically to project-controlled
  directories and MUST NOT contain raw secret-bearing content.
- When a repository condition prevents complete analysis, the system MUST emit
  structured partial outputs and structured error records rather than failing
  silently.

## Delivery Workflow and Quality Gates

- Plans MUST include a Constitution Check that verifies multi-agent fit,
  repository-scale performance strategy, scanning boundaries, language-routing
  coverage, evidence model, degradation behavior, testing approach,
  non-destructive output handling, living-context deliverables, and cost
  controls.
- Specifications MUST define repository scope, excluded inputs, language/file
  type handling, evidence expectations, measurable performance constraints, and
  any model-usage budget assumptions.
- Tasks MUST include automated tests for each affected stage and explicit work
  for discovery, exclusion enforcement, routing, deterministic artifact
  generation, structured error handling, and output placement when relevant.
- Compliance reviews for plans, tasks, pull requests, and release candidates
  MUST treat this constitution as the governing standard. Deviations MUST be
  documented with rationale, risk, and an approved remediation plan before
  implementation proceeds.

## Governance

This constitution supersedes conflicting local development habits and template
defaults. Amendments MUST be proposed as a documented change to this file with
an explicit rationale, impact assessment, and synchronization of affected
templates or guidance documents before approval. Versioning follows semantic
rules: MAJOR for backward-incompatible governance changes or principle
redefinitions, MINOR for new principles or materially expanded guidance, and
PATCH for clarifications or non-semantic wording fixes. Compliance MUST be
reviewed at plan creation, before implementation, and during pull request or
release review; unresolved violations MUST block approval unless the deviation
is documented and explicitly accepted.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): Initial ratification
date is not recorded in repo history. | **Last Amended**: 2026-03-10
