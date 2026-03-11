# Structural Analysis Contract: Brownfield Cartographer Stage 3

## Purpose

Define the public Stage 3 contract for repository preparation, structural
extraction, and Surveyor-ready static-analysis artifacts.

## Repository Preparation Contract

Stage 3 MUST accept:
- a local repository path
- a Git or GitHub repository URL

Stage 3 MUST return:
- a validated local repository root
- deterministic repository identity metadata
- preparation status and reuse information
- structured warnings or errors when preparation degrades or fails

URL-based repository preparation MUST:
- clone into project-controlled locations such as `.cartography/repos/`
- use shallow clone behavior by default
- reuse or refresh equivalent local clones deterministically
- avoid modifying analyzed source files

## Structural Routing Contract

Stage 3 MUST route manifest-eligible files through a centralized
language-routing contract.

Primary structural routing scope:
- Python
- SQL
- YAML
- JavaScript
- TypeScript

Recognized but bounded scope:
- notebooks
- shell

Routing outputs MUST include:
- normalized language
- support status
- parser or extractor capability
- partial-support or unsupported notes where relevant

## Structural Extraction Contract

For supported languages, Stage 3 MUST extract the module-level structural facts
needed by the future Surveyor stage, including:
- imports, includes, or dependency references where meaningful
- classes where meaningful
- functions where meaningful
- signatures or argument lists where practical
- module or file metadata

Extraction results MUST:
- use typed records
- include source-path evidence
- include line metadata where available
- preserve warnings and partial-result indicators
- stay deterministic in ordering and stable identifiers

## Graceful Degradation Contract

Malformed, unsupported, partially supported, or dynamically difficult files
MUST NOT crash the run. Stage 3 MUST instead emit structured file-level
warnings, parse-status markers, and partial outputs where safe.

Manifest-skipped, secret-bearing, vendored, binary, minified, archived,
oversized, and otherwise ineligible files MUST remain outside deep parsing
scope.

## Artifact Contract

Stage 3 MUST persist deterministic structural artifacts under project-controlled
`.cartography` locations. Expected artifact surfaces include:
- `structural_index.json`
- `ast_index.json`
- run-level structural summary output

Artifacts MUST:
- be static-analysis outputs, not graph or LLM outputs
- preserve deterministic ordering
- preserve stable IDs
- avoid raw secret-bearing contents
- remain suitable for later Surveyor and graph stages

## CLI and Orchestrator Contract

The analyze flow MUST:
1. resolve repository input
2. prepare or reuse a local analysis root
3. obtain or reuse manifest-scoped eligible files
4. run structural extraction on eligible files only
5. emit deterministic structural artifacts and a summary

The CLI MUST support both local repository paths and Git repository URLs
without requiring manual repository preparation.
