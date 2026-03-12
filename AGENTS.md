# codebase-cartographer Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-10

## Active Technologies
- Python 3.11+ + Pydantic v2, pytest (002-define-typed-contracts)
- Project-controlled filesystem artifacts under `.cartography/` (002-define-typed-contracts)
- Python 3.11+ + Pydantic v2, pydantic-settings, Typer, pytest (003-repo-inventory)
- Python 3.11+ + Pydantic v2, pydantic-settings, Typer, pytest, tree-sitter, git-based repository preparation (004-structural-analysis)
- Project-controlled filesystem artifacts under `.cartography/`, including prepared repositories, run artifacts, cache, and logs (004-structural-analysis)
- Python 3.11+ + Pydantic v2, pydantic-settings, Typer, pytest, NetworkX (005-surveyor-agent)
- Project-controlled filesystem artifacts under `.cartography/`, including manifest, structural outputs, module graph artifacts, survey summaries, cache, and logs (005-surveyor-agent)
- Python 3.11+ + Pydantic v2, pydantic-settings, Typer, pytest, NetworkX, sqlglot (006-hydrologist-agent)
- Project-controlled filesystem artifacts under `.cartography/`, including manifest, structural outputs, module graph artifacts, lineage graph artifacts, summaries, cache, and logs (006-hydrologist-agent)

- Python 3.11+ + uv, Typer, Pydantic, pytest (001-bootstrap-cartographer-foundation)

## Project Structure

```text
src/
tests/
```

## Commands

cd src; pytest; ruff check .

## Constitutional Constraints

- Respect read-only analysis of target repositories.
- Keep outputs, caches, and logs inside project-controlled directories.
- Exclude secret-bearing, generated, vendored, binary, and oversized inputs by
  default.
- Preserve deterministic artifacts, stable IDs, and evidence labeling.
- Prefer static analysis and graph methods before LLM-backed inference.

## Code Style

Python 3.11+: Follow standard conventions

## Recent Changes
- 006-hydrologist-agent: Added Python 3.11+ + Pydantic v2, pydantic-settings, Typer, pytest, NetworkX, sqlglot
- 005-surveyor-agent: Added Python 3.11+ + Pydantic v2, pydantic-settings, Typer, pytest, NetworkX
- 004-structural-analysis: Added Python 3.11+ + Pydantic v2, pydantic-settings, Typer, pytest, tree-sitter, git-based repository preparation


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
