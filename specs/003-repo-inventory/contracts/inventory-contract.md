# Inventory Contract: Brownfield Cartographer Stage 2 Repository Inventory

## Purpose

Define the Stage 2 public inventory surface consumed by the CLI, orchestrator,
and later analyzers.

## Inventory Workflow Contract

Stage 2 MUST expose a repository inventory workflow that:
- walks the analysis root once
- applies safety and exclusion rules before parse eligibility is granted
- produces deterministic per-file inventory records
- emits stable summary statistics and persisted inventory artifacts

This workflow is the canonical repository input layer for later Surveyor and
Hydrologist stages.

## Classification Contract

Stage 2 classification outputs MUST provide:
- a normalized language label
- an explicit support status
- parse-eligibility signaling
- the source of the classification decision
- optional notes for future analyzers when support is partial or bounded

Required routing coverage:
- Python
- SQL
- YAML
- JavaScript
- TypeScript
- JSON configuration
- Jupyter notebooks
- Shell

## Safety Contract

Stage 2 safety enforcement MUST:
- keep traversal within the analysis root
- exclude secret-bearing, generated, vendored, binary, archived, minified,
  oversized, lockfile, and otherwise irrelevant files before parse eligibility
- record structured skip reasons for excluded files
- avoid persisting sensitive file contents into inventory artifacts or logs

## Manifest Contract

Stage 2 manifest outputs MUST provide:
- deterministic ordering
- analysis-root-relative paths
- stable file identity
- file metadata for future analyzers
- support-status and skip-reason outcomes
- bounded digest or digest-strategy information

Manifest records MUST remain usable by later structural parsing, SQL lineage,
config analysis, and incremental re-analysis stages.

Expected per-record fields include:
- root-relative path
- deterministic file identity
- extension
- normalized language label
- support status
- parse-eligibility flag
- structured skip reason when excluded
- bounded metadata and notes for downstream analyzers

## Output Contract

Stage 2 MUST persist:
- a detailed manifest artifact
- a summary artifact

Both outputs MUST be written to project-controlled `.cartography` locations and
serialize deterministically for diffing and orchestrator reuse.

## Stage 2 Non-Goals

- tree-sitter parsing
- SQL AST lineage extraction
- graph construction or analysis
- LangGraph workflow execution
- LLM or embedding inference
