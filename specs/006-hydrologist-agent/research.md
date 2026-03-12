# Research: Hydrologist Agent

## Decision: Reuse manifest, structural, and Surveyor artifacts as the sole scope boundary for lineage extraction

**Rationale**: Stage 5 must build on prior deterministic artifacts instead of
adding independent repository scans. This keeps stage boundaries clean, avoids
repeated filesystem walks, and ensures lineage only comes from files already
vetted by safe-scanning and routing rules.

**Alternatives considered**:
- Re-scan the repository independently for SQL, Python, and YAML files:
  rejected because it duplicates Stage 2 responsibilities and risks scope drift.
- Let Hydrologist inspect any file regardless of manifest eligibility: rejected
  because it weakens security boundaries and deterministic routing.

## Decision: Normalize dataset identifiers from deterministic source cues before graph construction

**Rationale**: Dataset names can appear as table identifiers, dbt-style model
names, file-based references, or static API arguments. A canonical
normalization step is required so the lineage graph does not create duplicate
nodes for the same logical dataset.

**Alternatives considered**:
- Preserve raw source strings as dataset node IDs: rejected because minor naming
  variations would fragment the lineage graph.
- Resolve identifiers through runtime or warehouse lookups: rejected because it
  would break read-only, deterministic, offline-capable analysis boundaries.

## Decision: Use bounded static SQL parsing and static Python/YAML signal extraction with partial-result fallbacks

**Rationale**: SQL parsing can recover strong lineage signals, while Python and
YAML often provide weaker or framework-specific hints. Static extraction keeps
cost low and trust boundaries clear, and partial fallbacks prevent malformed or
dynamic inputs from blocking the stage.

**Alternatives considered**:
- Treat malformed SQL or dynamic query assembly as hard failures: rejected
  because brownfield lineage work must degrade gracefully.
- Infer missing lineage through LLM or semantic reasoning: rejected because
  Stage 5 explicitly excludes model-backed inference.

## Decision: Build a directed NetworkX lineage graph with explicit dataset and transformation nodes

**Rationale**: The stage needs deterministic lineage edges and later graph
consumers will depend on a stable node-edge representation. A directed graph
makes `CONSUMES` and `PRODUCES` semantics explicit and supports later expansion
without changing the core lineage contract.

**Alternatives considered**:
- Store lineage as flat relationship lists only: rejected because graph-based
  downstream stages would need to reconstruct structure repeatedly.
- Collapse transformations into dataset-to-dataset edges only: rejected because
  it loses the intermediate execution units needed for traceability and later
  reasoning.

## Decision: Keep evidence boundaries explicit and conservative for ambiguous lineage

**Rationale**: Some lineage signals will be direct, such as parsed SQL table
references, while others will be partial, such as static detection of Python
API usage or weak YAML references. Explicit evidence and confidence boundaries
prevent overclaiming certainty.

**Alternatives considered**:
- Treat all extracted lineage as equally strong: rejected because it obscures
  trust boundaries and undermines reproducibility.
- Drop weak signals entirely: rejected because partial lineage is still useful
  when it is labeled correctly.
