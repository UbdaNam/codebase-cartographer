# codebase-cartographer Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-10

## Active Technologies
- Python 3.11+ + Pydantic v2, pytest (002-define-typed-contracts)
- Project-controlled filesystem artifacts under `.cartography/` (002-define-typed-contracts)
- Python 3.11+ + Pydantic v2, pydantic-settings, Typer, pytest (003-repo-inventory)

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
- 003-repo-inventory: Added Python 3.11+ + Pydantic v2, pydantic-settings, Typer, pytest
- 002-define-typed-contracts: Added Python 3.11+ + Pydantic v2, pytest

- 001-bootstrap-cartographer-foundation: Added Python 3.11+ + uv, Typer, Pydantic, pytest

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
