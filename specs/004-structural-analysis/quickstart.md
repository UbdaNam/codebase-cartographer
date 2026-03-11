# Quickstart: Brownfield Cartographer Stage 3 Repository Input Resolution and Structural Analysis

## Prerequisites

- Python 3.11 or newer
- Stage 0, Stage 1, and Stage 2 foundations already present
- tree-sitter language dependencies available in the development environment
- fixture repositories for local path, Git URL, mixed-language parsing, and
  malformed-file scenarios

## Expected Stage 3 Deliverables

- repository input resolution for local paths and Git URLs
- prepared local repository reuse under `.cartography/repos/`
- centralized language routing for structural analysis
- deterministic structural artifacts for Surveyor-ready module facts
- pytest coverage for preparation, clone reuse, parsing, degradation, and
  artifact determinism

## Validation Workflow

```powershell
uv run pytest
uv run python -m src.cli analyze --repo .
uv run python -m src.cli analyze --repo https://example.com/org/repo.git
```

Expected Stage 3 behavior:
- local repository inputs resolve directly to a validated analysis root
- Git URL inputs prepare or reuse a project-controlled local working copy
- manifest eligibility remains authoritative for structural parsing scope
- supported files produce deterministic structural records with evidence
- malformed or partially supported files produce structured degraded outcomes
- structural artifacts are written deterministically under `.cartography`

## Confirm Stage 3 Scope

Stage 3 provides:
- repository preparation
- local-path and Git-URL input resolution
- centralized structural language routing
- tree-sitter-based module-level structural extraction
- deterministic structural artifact serialization

Stage 3 does not provide:
- module graph ranking
- git velocity analysis
- dead code detection
- SQL lineage extraction
- data lineage graph traversal
- NetworkX graph algorithms
- LangGraph workflows
- embeddings or LLM execution
