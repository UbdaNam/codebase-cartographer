# Quickstart: Brownfield Cartographer Stage 2 Repository Inventory

## Prerequisites

- Python 3.11 or newer
- existing Stage 0 and Stage 1 project foundations
- repository fixture inputs for mixed-language and exclusion validation

## Expected Stage 2 deliverables

- strengthened single-pass repository discovery
- centralized language classification and support-status routing
- deterministic manifest and summary artifacts under `.cartography`
- Stage 2 analyze-flow integration for inventory generation
- pytest coverage for discovery, classification, exclusion behavior, and
  deterministic output

## Validation workflow

```powershell
uv run pytest
uv run python -m src.cli analyze --repo .
```

Expected Stage 2 behavior:
- analyze writes a deterministic repository manifest artifact and summary
- supported, partially supported, skipped, and unsupported files are clearly
  distinguished
- excluded files remain non-parse-eligible and carry structured skip reasons
- repeated runs against the same unchanged repository produce stable ordering
  and stable classification results

## Confirm Stage 2 scope

Stage 2 provides:
- robust repository discovery
- centralized mixed-language routing
- deterministic inventory serialization
- analyzer-ready manifest records and summary statistics

Stage 2 does not provide:
- tree-sitter queries
- SQL AST lineage parsing
- NetworkX graph logic
- LangGraph nodes or workflows
- LLM or embedding execution
