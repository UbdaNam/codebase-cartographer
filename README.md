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

The `analyze` command performs manifest-only Stage 0 analysis and writes
deterministic metadata under `.cartography/`.

## Stage 1 Typed Contracts

Stage 1 adds:
- stable enums for graph, support-status, method, confidence, and skip-reason semantics
- reusable evidence and citation models
- deterministic graph and artifact payload contracts
- shared run, pipeline, and future Navigator state models

Stage 1 remains contract-only and does not introduce analyzers, graph
algorithms, LangGraph workflows, or LLM execution.
