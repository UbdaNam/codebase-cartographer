# Quickstart: Brownfield Cartographer Stage 0 Foundation

## Prerequisites

- Python 3.11 or newer
- `uv`

## Setup

```powershell
uv venv
uv sync
```

## Run the placeholder CLI

```powershell
uv run python -m src.cli analyze --repo .
uv run python -m src.cli query "What is this repository?"
```

Expected Stage 0 behavior:
- initialize `.cartography/` artifact directories
- create minimal run metadata
- write a deterministic manifest under `.cartography/runs/<run-id>/manifest.json`
- apply safe-scanning boundaries before any file reads
- return placeholder summaries rather than deep analysis results
- return a stub response for `query`

## Run tests

```powershell
uv run pytest
```

## Validate Stage 0 scope

Confirm the foundation provides:
- typed settings and centralized scan policy
- deterministic manifest and run metadata contracts
- placeholder analyze and query entrypoints
- isolated tests for ignore rules, manifest determinism, and artifact setup

Confirm Stage 0 does not provide:
- AST parsing
- lineage extraction
- graph execution
- embeddings or LLM calls
