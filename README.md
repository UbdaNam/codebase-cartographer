# codebase-cartographer

Production-minded codebase intelligence for large brownfield repositories.

The project is being shaped as a LangGraph-oriented multi-agent system with
Surveyor, Hydrologist, Semanticist, Archivist, and a later Navigator query
agent. It is intended to build a living, queryable map of repository
architecture, lineage, and semantic structure for rapid FDE onboarding while
remaining safe, deterministic, incremental, and cost-bounded.

## Stage 0 Foundation

Stage 0 establishes:
- typed application settings
- centralized safe-scanning and ignore policy
- deterministic repository manifest generation
- `.cartography/` artifact and run metadata conventions
- placeholder `analyze` and `query` CLI commands
- future-ready boundaries for agents, analyzers, graph, index, and llm layers

Stage 0 explicitly does not implement:
- AST parsing
- lineage extraction
- graph execution
- embeddings or LLM calls

## Developer Setup

```powershell
uv venv
uv sync
uv run pytest
```

## CLI

```powershell
uv run python -m src.cli analyze --repo .
uv run python -m src.cli query "What is this repository?"
```

The `analyze` command now performs Stage 6 analysis. It accepts either a local
repository path or a Git URL and writes deterministic inventory, structural,
architectural, lineage, and semantic artifacts under `.cartography/`.

## Stage 1 Typed Contracts

Stage 1 adds:
- stable enums for graph, support-status, method, confidence, and skip-reason semantics
- reusable evidence and citation models
- deterministic graph and artifact payload contracts
- shared run, pipeline, and future Navigator state models

Stage 1 remains contract-only and does not introduce analyzers, graph
algorithms, LangGraph workflows, or LLM execution.

## Stage 2 Repository Inventory

Stage 2 adds:
- single-pass repository discovery
- centralized mixed-language classification for Python, SQL, YAML,
  JavaScript, TypeScript, JSON, notebooks, and shell files
- structured skip reasons and parse-eligibility signaling
- deterministic inventory manifest and summary artifacts for later analyzers

Stage 2 remains inventory-only and does not introduce AST parsing, lineage
extraction, graph algorithms, or agent execution.

## Stage 3 Structural Analysis

Stage 3 adds:
- repository input resolution for local paths and Git-style URLs
- prepared repository reuse under `.cartography/repos/`
- centralized language routing for parser-backed structural extraction
- deterministic `structural_index.json`, `ast_index.json`, and
  `structural_summary.json` artifacts
- Surveyor-ready static-analysis records with file and line evidence where
  available

Stage 3 remains structural-only and does not introduce module graph ranking,
git velocity analysis, SQL lineage extraction, graph algorithms, LangGraph
workflows, embeddings, or LLM execution.

## Stage 4 Surveyor Agent

Stage 4 adds:
- a `SurveyorAgent` that consumes manifest and structural artifacts
- deterministic module graph construction for supported code modules
- recent git-change velocity signals with graceful degradation when history is
  unavailable
- PageRank hub ranking and strongly connected component detection
- conservative dead code candidate heuristics
- deterministic `module_graph.json` and `survey_summary.json` artifacts

Stage 4 remains architectural-only and does not introduce SQL lineage,
Hydrologist logic, semantic indexing, LangGraph workflows, embeddings, or LLM
execution.

## Stage 5 Hydrologist Agent

Stage 5 adds:
- a `HydrologistAgent` that consumes manifest, structural, and module-graph
  artifacts
- deterministic lineage extraction across SQL, Python, and config inputs with
  graceful degradation
- typed `lineage_graph.json` and `lineage_summary.json` artifacts
- stable `CONSUMES`, `PRODUCES`, and `CONFIGURES` relationships for downstream
  graph consumers

Stage 5 remains lineage-only and does not introduce semantic purpose
statements, documentation-drift analysis, clustering, or Day-One synthesis.

## Stage 6 Semanticist Agent

Stage 6 adds:
- a `SemanticistAgent` that consumes Surveyor and Hydrologist outputs together
  with structural evidence
- grounded module-purpose profiles with implementation evidence bundles
- documentation drift detection with confidence and linked evidence
- inferred business-domain clustering with deterministic fallback behavior
- evidence-backed Day-One answers for onboarding and downstream Archivist flows
- deterministic semantic artifacts:
  - `module_semantics.json`
  - `documentation_drift.json`
  - `domain_map.json`
  - `day_one_answers.json`

Stage 6 keeps LLM-backed work optional behind provider and budget abstractions,
falls back to static heuristics when providers are unavailable, and preserves
stable artifact shapes for later stages.
