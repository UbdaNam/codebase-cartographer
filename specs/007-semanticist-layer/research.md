# Research: Semanticist Agent

## Decision: Introduce a lightweight provider abstraction with OpenRouter-backed chat and embedding clients, using `httpx` as the only new transport dependency

**Rationale**: The feature explicitly requires budgeted model-backed semantic
analysis while keeping dependencies minimal. A thin provider layer over `httpx`
provides retries, timeouts, JSON transport, and pluggable model selection
without pulling in heavyweight orchestration SDKs that would be hard to test
deterministically.

**Alternatives considered**:
- Use raw `urllib` from the standard library: rejected because production-grade
  timeout, retry, and response-handling ergonomics would become harder to keep
  clean and testable.
- Adopt a full agent/LLM framework: rejected because the existing codebase is
  strongly typed and stage-oriented, and the added abstraction cost is not
  justified for one bounded semantic stage.

## Decision: Keep purpose generation grounded in compact evidence bundles assembled from prior artifacts plus targeted source excerpts, and exclude documentation from the primary purpose prompt

**Rationale**: The requirement explicitly forbids docstring restatement.
Evidence bundles should therefore be built from module path, imports, exported
symbols, structural facts, graph metrics, lineage links, git velocity, and only
the minimal code excerpts needed to explain real behavior. Nearby
documentation remains a separate input for drift detection, not the first-pass
purpose statement prompt.

**Alternatives considered**:
- Feed full module source into the model: rejected because it is too expensive,
  harder to audit, and makes deterministic chunking and cost control more
  difficult.
- Include docstrings in purpose generation prompts: rejected because it weakens
  the guarantee that purpose statements are implementation-grounded.

## Decision: Use a rule-first documentation drift pipeline with model-backed adjudication only when evidence is ambiguous

**Rationale**: Drift detection must remain trustable and auditable. Static
signals such as empty documentation, missing documented responsibilities,
contradictions with lineage or dependency behavior, and stale claimed outputs
can be evaluated deterministically first. A higher-cost model is only needed
when the deterministic layer cannot confidently classify the mismatch.

**Alternatives considered**:
- Let an LLM fully decide all drift findings: rejected because this would blur
  observed versus inferred evidence and create unnecessary cost.
- Use only lexical overlap heuristics: rejected because omissions and semantic
  contradictions often require stronger comparative reasoning.

## Decision: Support embedding-based domain clustering when configured, but keep a deterministic fallback based on graph similarity, lineage affinity, imports, and path prefixes

**Rationale**: The feature calls for embedding-driven domain grouping, but the
system must still work on any repository and degrade gracefully if embeddings or
network access are unavailable. A fallback based on module graph edges,
lineage relationships, import neighborhoods, and stable path tokens preserves
domain inference without adding heavyweight local ML dependencies.

**Alternatives considered**:
- Require embeddings for every run: rejected because offline and budget-limited
  environments would fail entirely.
- Add a local clustering library such as scikit-learn: rejected because it is a
  large dependency for a feature that can reuse NetworkX and simple vector math.

## Decision: Reserve the stronger model tier for Day-One synthesis and difficult drift adjudication, while bulk module purpose generation uses a lower-cost model tier

**Rationale**: Module-level purpose generation may run hundreds or thousands of
times in large repositories, so it must use the cheaper tier. Day-One synthesis
and hard drift judgments happen at repository scope and benefit from a stronger
model because they require cross-artifact reasoning and precise evidence
citations.

**Alternatives considered**:
- Use one premium model for all semantic work: rejected because cost and
  latency would scale poorly on large repositories.
- Use only a cheap model for all semantic work: rejected because final
  repository-level synthesis needs better reasoning quality.

## Decision: Track model usage with a ContextWindowBudget ledger that records estimated prompt size, completion size, request count, and per-stage budget consumption

**Rationale**: The constitution requires explicit cost discipline. A dedicated
budget component provides stable accounting, early refusal when budgets are
exhausted, and deterministic fallback behavior while keeping the core semantic
pipeline testable.

**Alternatives considered**:
- Trust provider-side billing only: rejected because local planning and graceful
  degradation need pre-call estimates and structured usage state.
- Track only request counts: rejected because semantic costs depend heavily on
  evidence-bundle size and response budgets, not just request totals.

## Decision: Persist four durable semantic artifacts and keep them independent but cross-linked

**Rationale**: The feature explicitly requires `.cartography/module_semantics.json`,
`.cartography/documentation_drift.json`, `.cartography/domain_map.json`, and
`.cartography/day_one_answers.json`. Keeping them separate matches the intended
downstream consumption model while allowing deterministic contract tests for
each artifact.

**Alternatives considered**:
- Collapse all semantics into one monolithic JSON file: rejected because it
  would make downstream consumption and targeted regression testing harder.
- Store semantic results only inside `module_graph.json`: rejected because it
  would overload Surveyor's architectural artifact and blur stage ownership.
