# Quickstart: Semanticist Agent

## Scenario 1: Run the full pipeline and inspect semantic artifacts

1. Run `python -m src.cli analyze --repo <path-or-url>` on a repository that
   already supports the Stage 0-5 pipeline inputs.
2. Confirm the run now produces these additional artifacts under
   `.cartography/` for the active run:
   - `module_semantics.json`
   - `documentation_drift.json`
   - `domain_map.json`
   - `day_one_answers.json`
3. Confirm the run summary exposes paths for those artifacts and includes
   `semantic_stats`.
4. Confirm the semantic outputs reference Surveyor and Hydrologist evidence and
   preserve deterministic ordering across repeated unchanged runs.

## Scenario 2: Degrade gracefully when provider access or budgets are limited

1. Run Semanticist with provider credentials missing, provider access disabled,
   or a deliberately small semantic budget.
2. Confirm the stage still writes semantic artifacts with partial-result flags,
   warning codes, and any heuristic-only outputs that remain safe to emit.
3. Confirm the run does not fail the full pipeline and does not fabricate high
   confidence answers when model-backed work is unavailable.

## Scenario 3: Detect documentation drift and verify auditability

1. Analyze a fixture repository that contains stale docstrings or nearby module
   documentation.
2. Confirm `documentation_drift.json` includes the module path, observed
   documentation text, inferred implementation purpose, drift type, confidence,
   and linked evidence references.
3. Confirm reviewers can inspect each drift finding without needing to re-parse
   the repository manually.

## Scenario 4: Infer domains and answer Day-One questions

1. Analyze a repository with clear ingestion, transformation, serving, or
   orchestration areas plus meaningful lineage and architectural signals.
2. Confirm `domain_map.json` groups modules into 5-8 understandable domains or
   fewer when the repository structure does not support more.
3. Confirm `day_one_answers.json` contains all five required answers with
   explicit evidence references and partial markers where confidence is limited.
