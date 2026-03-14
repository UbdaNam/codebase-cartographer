# Research: Archivist and Navigator

## Decision: Keep Archivist artifact generation deterministic and section-driven, with optional bounded synthesis only after evidence is collected

**Rationale**: The challenge requires trust-preserving living artifacts that are
easy to reuse and regression-test. `CODEBASE.md` and `onboarding_brief.md`
should therefore be assembled from structured section inputs derived from
Surveyor, Hydrologist, and Semanticist outputs, with optional provider-backed
wording only when evidence is already complete and traceable.

**Alternatives considered**:
- Use one large LLM prompt to generate the whole final document set: rejected
  because it weakens auditability, increases cost, and harms deterministic
  testing.
- Avoid any synthesis assistance entirely: rejected because limited wording
  support can improve readability while keeping evidence and trust labels intact.

## Decision: Implement the semantic index as a portable filesystem-backed vector store under `.cartography/semantic_index/`

**Rationale**: The challenge explicitly requires `semantic_index/` as a vector
store of module purpose statements. A filesystem-backed store with stable JSON
records, optional cached embeddings, normalized retrieval tokens, and linked
evidence metadata satisfies the requirement without adding external storage
infrastructure.

**Alternatives considered**:
- Introduce a dedicated vector database: rejected because it adds operational
  complexity and breaks the current filesystem-artifact model.
- Keep only raw module semantics and scan them at query time: rejected because
  Navigator needs faster semantic retrieval and a portable reuse surface.

## Decision: Use append-only JSON Lines for `cartography_trace.jsonl`

**Rationale**: The trace system must capture every major Archivist and
Navigator action along with evidence, method, and confidence. JSON Lines is
portable, incremental-friendly, easy to append to per run, and straightforward
to validate in tests.

**Alternatives considered**:
- One monolithic trace JSON file: rejected because append-only operation and
  per-action auditing are simpler with JSONL.
- Plain-text logs only: rejected because downstream tooling and tests need
  structured machine-readable events.

## Decision: Implement Navigator as a retrieval-first LangGraph agent with exactly four tools and typed state

**Rationale**: The challenge requires LangGraph specifically and prescribes the
core workflow. A typed LangGraph state model tracking query text, selected
tool, retrieved context, evidence references, response draft, and trust
metadata preserves auditability while letting Navigator prefer artifact-based
retrieval before any synthesis.

**Alternatives considered**:
- A plain Python dispatcher without LangGraph: rejected because it violates the
  mandatory challenge requirement.
- A free-form chat agent with tool selection hidden in prompts: rejected
  because explicit typed state and deterministic retrieval-first routing are
  more testable and trustworthy.

## Decision: Model incremental refresh from git baseline metadata plus upstream artifact dependency coverage

**Rationale**: The challenge requires re-analyzing only changed files and
affected downstream artifacts. Persisting the last analyzed commit hash, source
coverage, artifact generation timestamps, and upstream artifact references
enables Archivist to decide what can be reused and what must be regenerated.

**Alternatives considered**:
- Full rerun on every invocation: rejected because it undermines repository
  scale and ongoing-operation goals.
- Per-file timestamp checks only: rejected because downstream artifacts depend
  on upstream artifact state, not just direct file modification times.

## Decision: Reuse the existing provider and budget abstractions for optional embeddings and response synthesis

**Rationale**: Archivist and Navigator need optional model-backed semantic
retrieval and response synthesis, but the constitution requires bounded,
measured usage with static fallbacks. Reusing the existing provider and budget
layer keeps cost handling consistent with Semanticist and avoids another model
integration seam.

**Alternatives considered**:
- Introduce a separate provider path for Navigator: rejected because it
  duplicates transport, metering, and fallback logic.
- Make embeddings and synthesis mandatory: rejected because the pipeline must
  still work when providers are disabled or unavailable.
