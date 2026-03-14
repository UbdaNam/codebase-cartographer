# Quickstart: Archivist and Navigator

## Scenario 1: Run the full pipeline and inspect final living artifacts

1. Run `python -m src.cli analyze --repo <path-or-url>` on a repository that
   already supports Surveyor, Hydrologist, and Semanticist.
2. Confirm the active run under `.cartography/` now contains:
   - `CODEBASE.md`
   - `onboarding_brief.md`
   - `lineage_graph.json`
   - `semantic_index/`
   - `cartography_trace.jsonl`
3. Confirm `CODEBASE.md` includes architecture overview, critical path, data
   sources and sinks, known debt, recent change velocity, and module purpose
   index.
4. Confirm `onboarding_brief.md` answers all five Day-One questions and labels
   observed facts versus inferred conclusions.

## Scenario 2: Query the repository through Navigator

1. Run `python -m src.cli query "<question-or-target>"` or the equivalent typed
   query invocation once Navigator is integrated.
2. Issue each required query mode at least once:
   - `find_implementation`
   - `trace_lineage`
   - `blast_radius`
   - `explain_module`
3. Confirm every response includes source file, line range when available,
   analysis method, and explicit static-analysis-versus-inference labeling.

## Scenario 3: Verify incremental refresh behavior

1. Run the full pipeline on a repository and retain the resulting baseline
   metadata.
2. Change a small subset of files or create a small new commit.
3. Run the pipeline again.
4. Confirm unchanged final-stage artifacts or index segments are reused,
   affected outputs are regenerated, and reuse versus regeneration is visible
   in `cartography_trace.jsonl`.

## Scenario 4: Degrade gracefully when providers are disabled

1. Run the pipeline with provider access disabled or budgets exhausted.
2. Confirm Archivist still emits final artifacts from deterministic evidence and
   labels any missing synthesis or embeddings as partial.
3. Confirm Navigator still answers from stored artifacts and graph/index
   fallbacks without fabricating unsupported confidence.
