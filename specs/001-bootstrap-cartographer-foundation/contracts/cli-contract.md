# CLI Contract: Brownfield Cartographer Stage 0 Foundation

## Purpose

Define the placeholder command surface exposed by the Stage 0 foundation. These
commands establish stable interfaces for future analyze and query workflows
without implementing full analysis behavior.

## Command: `cartographer analyze`

**Intent**: Initialize a safe run context for a target repository and emit a
minimal run summary.

**Inputs**:
- `repo`: local repository path or future remote repository reference
- `output-dir` (optional): override for the project-controlled artifact root
- `config` (optional): path to configuration overrides

**Behavioral Contract**:
- MUST validate the target path or reference before any scan begins
- MUST create or resolve the `.cartography/` artifact area
- MUST initialize run metadata and a deterministic run ID
- MUST apply centralized scanning policy before any file content read
- MUST return a minimal summary even when analysis is intentionally stubbed in
  Stage 0
- MUST NOT modify the analyzed repository

**Outputs**:
- human-readable command summary
- structured run metadata written under `.cartography/`
- non-zero exit code only for invalid invocation or unrecoverable setup failure

## Command: `cartographer query`

**Intent**: Reserve the future query interface while remaining a Stage 0 stub.

**Inputs**:
- `question`: user question or query text
- `run-id` (optional): target prior run

**Behavioral Contract**:
- MUST be present as a visible CLI entrypoint
- MUST explain that query execution is not yet implemented in Stage 0
- MUST NOT imply semantic, graph, or model-backed answers exist yet

**Outputs**:
- clear stub response describing current limitation
- stable exit behavior suitable for future extension

## Structured Output Expectations

- run summaries and metadata MUST be deterministic and machine-readable
- skip reasons MUST use stable reason codes
- file classifications MUST use the approved support-status set:
  `supported`, `partial`, `skipped`, `unsupported`
