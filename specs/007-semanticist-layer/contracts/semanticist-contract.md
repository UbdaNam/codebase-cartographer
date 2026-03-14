# Contract: Semanticist Agent

## Purpose

Define the Stage 6 input and output contract for the Semanticist agent so
orchestration, tests, and downstream Archivist workflows can rely on
deterministic semantic artifacts.

## Inputs

- **Manifest artifact**: The deterministic repository manifest from Stage 2,
  including file identity, routing, support status, and safe-scan boundaries.
- **Structural artifact set**: Stage 3 structural outputs containing symbol
  facts, statement markers, evidence metadata, and partial-result warnings.
- **Surveyor artifact set**: Stage 4 module graph and summary outputs providing
  module identity, imports, velocity, complexity, entry-point, and dead-code
  context.
- **Hydrologist artifact set**: Stage 5 lineage graph and summary outputs
  providing dataset, transformation, and configuration relationships.
- **Prepared repository source files**: Raw module contents loaded lazily from
  the prepared repository only for semantic-eligible modules and only within the
  configured analysis root.
- **Configuration values**:
  - semantic artifact paths
  - provider settings and model tiers
  - budget limits
  - chunking thresholds
  - clustering settings
  - degradation and warning policies

## Outputs

- **Module semantics artifact**: Deterministic serialized semantic profiles for
  eligible modules, including purpose statements, evidence references, domain
  assignments, confidence, and warning markers.
- **Documentation drift artifact**: Deterministic serialized drift findings,
  including observed documentation, inferred implementation purpose, drift type,
  confidence, and evidence references.
- **Domain map artifact**: Deterministic serialized domain clusters and module
  assignments, including cluster labels, summaries, and assignment confidence.
- **Day-One answers artifact**: Deterministic serialized answers to the five
  FDE questions, each with evidence references, confidence, and partial markers.
- **Run-summary updates**:
  - artifact references
  - stage statistics
  - provider usage and budget status
  - warning and partial-result markers

## Artifact Files

- `.cartography/<run>/module_semantics.json`
- `.cartography/<run>/documentation_drift.json`
- `.cartography/<run>/domain_map.json`
- `.cartography/<run>/day_one_answers.json`

Optional mirrored latest-run paths may be maintained under `.cartography/`
provided they preserve deterministic content and remain project-controlled.

## Behavioral Guarantees

- Semanticist consumes prior staged artifacts and does not bypass manifest
  eligibility or repository-preparation boundaries.
- Semanticist loads raw source lazily and only for modules selected for
  semantic analysis.
- Purpose statements are grounded in implementation evidence rather than copied
  from documentation.
- Outputs explicitly distinguish directly observed facts, graph-derived
  inferences, and LLM-backed inferences.
- Artifact ordering, identifiers, and list serialization remain deterministic
  for unchanged inputs.
- Provider outages, budget exhaustion, missing embeddings, and weak evidence
  yield partial outputs and structured warnings instead of blocking artifact
  creation.

## Evidence Boundaries

- **Direct observations** include manifest metadata, structural facts, module
  graph properties, lineage relationships, git-history signals, and bounded
  source excerpts.
- **Graph inference** includes architectural centrality, dependency-based
  concentration, blast-radius reasoning, and domain grouping based on graph
  relationships.
- **LLM inference** includes purpose wording, ambiguous drift adjudication,
  cluster labeling, and final Day-One synthesis when provider-backed reasoning
  is invoked.
- Each persisted semantic result must reference its supporting evidence and
  identify whether the result is observed, graph-derived, or model-inferred.

## Error and Partial-Result Contract

- Semanticist emits structured warnings for:
  - missing or partial upstream artifacts
  - module source too large for one prompt window
  - provider request failure or timeout
  - budget exhaustion
  - documentation unavailable or too weak for drift comparison
  - clustering fallback activation
  - incomplete Day-One synthesis
- Semanticist may emit partial artifacts as long as deterministic ordering,
  root containment, evidence labeling, and non-destructive behavior are
  preserved.
- Semanticist must never persist excluded-file contents, secret-bearing content,
  or unbounded raw source excerpts into semantic artifacts.
