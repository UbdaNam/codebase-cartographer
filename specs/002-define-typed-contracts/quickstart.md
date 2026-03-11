# Quickstart: Brownfield Cartographer Stage 1 Typed Contracts

## Prerequisites

- Python 3.11 or newer
- existing Stage 0 project foundation

## Expected Stage 1 deliverables

- shared typed models under `src/models/`
- small deterministic ID helper support if needed
- pytest coverage for schema validation, enum serialization, stable IDs, and
  deterministic graph payload serialization

## Validation workflow

```powershell
uv run pytest
```

Expected Stage 1 behavior:
- graph, artifact, evidence, and state models validate cleanly
- enum values serialize to stable human-readable JSON values
- deterministic IDs reproduce the same values from the same canonical inputs
- partial and incomplete data validate where the contracts are designed to
  allow graceful degradation

## Confirm Stage 1 scope

Stage 1 provides:
- typed shared contracts
- deterministic serialization behavior
- mixed-language-safe status and evidence models
- future-ready analysis and query state

Stage 1 does not provide:
- analyzers
- graph engines
- LangGraph nodes or workflows
- AST or SQL parsing logic
- LLM or embedding execution
