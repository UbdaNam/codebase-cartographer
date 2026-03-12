# Quickstart: Hydrologist Agent

## Scenario 1: Run Hydrologist on a repository with SQL, Python, and YAML lineage sources

1. Run `python -m src.cli analyze --repo <path-or-url>` against a repository
   that already passes Stage 2 discovery, Stage 3 structural extraction, and
   Stage 4 Surveyor analysis.
2. Confirm the run produces:
   - `lineage_graph.json`
   - `lineage_summary.json`
   - dataset, transformation, and edge counts in the CLI output
3. Re-run the same analysis against the unchanged repository and confirm the
   serialized lineage graph and summary ordering are stable.

## Scenario 2: Handle malformed SQL and dynamic Python lineage cues

1. Analyze a fixture repository containing malformed SQL plus Python code that
   builds some queries dynamically.
2. Confirm the run still produces lineage artifacts and a summary.
3. Confirm partial lineage signals are labeled appropriately and that structured
   warnings are included in the lineage summary.

## Scenario 3: Extract lineage from dbt-style or YAML-defined pipelines

1. Analyze a fixture repository containing dbt-style SQL models and YAML files
   with dataset or pipeline references.
2. Confirm deterministic dataset and transformation records are added to the
   lineage graph where the source cues are strong enough.
3. Confirm unsupported or ambiguous pipeline conventions do not cause run
   failure and instead appear as partial warnings or skipped lineage inputs.
