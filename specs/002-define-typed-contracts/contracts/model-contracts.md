# Model Contracts: Brownfield Cartographer Stage 1 Typed Contracts

## Purpose

Define the public shared-contract surface produced by Stage 1. These contracts
are intended for later analyzers, graph builders, storage layers, and future
Navigator query flows.

## Contract Families

### Enumerations

Stage 1 exposes stable, human-readable enums for:
- `NodeKind`
- `EdgeKind`
- `SupportStatus`
- `AnalysisMethod`
- `SkipReason`
- `ConfidenceBand`

### Evidence and Citation Contracts

Evidence-aware contracts MUST preserve:
- analysis-root-relative source path
- optional line start and line end
- language
- analysis method
- confidence
- optional excerpt or symbol name
- explicit redaction signaling when excerpt text is withheld

These contracts MUST be reusable by graph nodes, graph edges, analysis
artifacts, and query-state citations.

### Graph Contracts

Stage 1 graph contracts MUST provide:
- typed node records
- typed edge records
- deterministic graph payload containers
- stable IDs derived from canonical fields

Required node families:
- `ModuleNode`
- `DatasetNode`
- `TransformationNode`

Optional lean extension families may exist only if they do not dilute the
shared contract surface.

### State Contracts

Stage 1 state contracts MUST provide:
- `RunContext`
- `AnalysisState`
- `NavigatorState`

`AnalysisState` supports pipeline execution and partial outcomes.
`NavigatorState` supports future LangGraph-ready query execution without
requiring a workflow engine today.
Contracts MUST support skipped-input summaries, artifact references, and
tool-history tracking without introducing live workflow logic.

## Serialization Expectations

- Contracts MUST serialize deterministically for later `.cartography` outputs
- Enum values MUST remain stable and human-readable in JSON payloads
- IDs MUST be deterministic from canonical fields rather than runtime
  randomness
- Partial and degraded results MUST be representable without invalid payloads
- Artifact payloads and graph payloads MUST sort nested metadata and record
  collections predictably so diffs stay readable

## Stage 1 Non-Goals

- AST parsing
- SQL lineage extraction
- graph algorithm execution
- LangGraph workflow execution
- LLM or embedding summarization
