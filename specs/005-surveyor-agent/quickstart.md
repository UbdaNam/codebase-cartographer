# Quickstart: Surveyor Agent

## Scenario 1: Run Surveyor on a repository with structural artifacts and git history

1. Run the analyze workflow against a repository that already passes Stage 2
   discovery and Stage 3 structural extraction.
2. Confirm the run produces:
   - a deterministic module graph artifact
   - a deterministic survey summary artifact
   - module count, import edge count, top hubs, circular dependency count, and
     high-velocity summary in the CLI output
3. Re-run the same analysis against the unchanged repository and confirm the
   serialized graph and summary ordering are stable.

## Scenario 2: Run Surveyor on a repository without usable git metadata

1. Analyze a repository fixture with structural artifacts but no accessible git
   history.
2. Confirm the run still produces module graph and survey summary artifacts.
3. Confirm velocity-related fields are marked partial or unavailable and that
   structured warnings are included in the summary.

## Scenario 3: Handle unresolved imports and partial structural extraction

1. Analyze a fixture repository containing unresolved imports or intentionally
   partial structural records.
2. Confirm valid module nodes and resolved edges still appear in the graph.
3. Confirm unresolved relationships are retained explicitly and do not cause
   run failure.
4. Confirm dead code candidates remain heuristic and include supporting reason
   signals rather than bare assertions.
