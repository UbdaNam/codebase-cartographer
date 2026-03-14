# Tasks: Brownfield Cartographer Stage 6 Semanticist Agent

**Input**: Design documents from `/specs/007-semanticist-layer/`
**Prerequisites**: plan.md (required), spec.md (required for user stories),
research.md, data-model.md, contracts/

**Tests**: Automated tests are REQUIRED for every affected stage. Include unit,
integration, contract, or regression coverage as appropriate to the feature.

**Organization**: Tasks are grouped by user story to enable independent
implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the Stage 6 workspace, provider baseline, and fixture
repositories for Semanticist implementation.

- [X] T001 Update Stage 6 dependencies for provider transport and semantic execution in pyproject.toml
- [X] T002 [P] Add Semanticist fixture repository for grounded purpose, domains, and Day-One synthesis in tests/fixtures/semanticist_repo/
- [X] T003 [P] Add Semanticist partial/offline fixture repository for degraded execution cases in tests/fixtures/semanticist_partial_repo/
- [X] T004 [P] Add Semanticist provider environment examples and setup notes in .env.example

---

## Phase 2: Foundational (Phase A - Foundations)

**Purpose**: Shared semantic contracts, provider seams, and artifact plumbing
that block all user stories.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T005 Create Semanticist artifact, profile, drift, domain, Day-One, and ledger models in src/models/semantic.py
- [X] T006 [P] Extend run context and run summary contracts for Semanticist artifact references and stats in src/models/state.py
- [X] T007 [P] Add Semanticist settings and artifact path helpers in src/config.py
- [X] T008 [P] Add Semanticist artifact writers and deterministic serialization helpers in src/utils/artifacts.py
- [X] T009 [P] Implement LLM provider interface for chat and embeddings in src/llm/provider.py
- [X] T010 [P] Implement OpenRouter-backed provider client and model tier routing in src/llm/openrouter.py
- [X] T011 [P] Implement ContextWindowBudget usage ledger and refusal thresholds in src/llm/budget.py
- [X] T012 Create Semanticist stage boundary and input-loading scaffolding in src/agents/semanticist.py

**Checkpoint**: Semantic contracts, provider seams, budgets, and artifact
plumbing are ready; user story implementation can now begin.

---

## Phase 3: User Story 1 - Understand the System Quickly (Priority: P1) MVP

**Goal**: Generate grounded module purpose statements, inferred domains, and
evidence-backed Day-One answers that let a new engineer understand the system
quickly.

**Independent Test**: Run analyze on `tests/fixtures/semanticist_repo/` and
verify `module_semantics.json`, `domain_map.json`, and `day_one_answers.json`
are produced with evidence references, stable ordering, and no purpose text
copied directly from documentation.

### Tests for User Story 1

- [X] T013 [P] [US1] Add contract test for Semanticist module, domain, and Day-One artifact schemas in tests/contract/test_semanticist_artifacts.py
- [X] T014 [P] [US1] Add unit test for evidence bundle construction and bounded source excerpt selection in tests/unit/test_semantic_evidence.py
- [X] T015 [P] [US1] Add integration test for Semanticist purpose, domain, and Day-One generation in tests/integration/test_semanticist_pipeline.py

### Implementation for User Story 1

- [X] T016 [P] [US1] Implement evidence bundle generation from manifest, structural, module graph, lineage graph, and source excerpts in src/analyzers/semantic_evidence.py
- [X] T017 [P] [US1] Implement grounded purpose and Day-One prompt builders in src/llm/prompts.py
- [X] T018 [US1] Implement per-module purpose extraction and module semantics artifact assembly in src/agents/semanticist.py
- [X] T019 [P] [US1] Implement embedding-aware domain clustering with deterministic graph and path fallback in src/analyzers/domain_clustering.py
- [X] T020 [P] [US1] Implement five-question Day-One synthesis with explicit evidence citations in src/analyzers/day_one_synthesis.py
- [X] T021 [US1] Persist module semantics, domain map, and Day-One answers artifacts in src/utils/artifacts.py
- [X] T022 [US1] Connect clustered domains and synthesized answers back to Semanticist profiles and ledger stats in src/models/semantic.py and src/agents/semanticist.py

**Checkpoint**: User Story 1 should produce grounded semantic understanding
artifacts that are independently testable and demoable.

---

## Phase 4: User Story 2 - Detect Documentation Drift (Priority: P2)

**Goal**: Compare implementation-grounded module purposes against docstrings
and nearby documentation to flag contradictions, omissions, and outdated
descriptions with evidence and confidence.

**Independent Test**: Analyze a fixture repository with stale or incomplete
documentation and verify `documentation_drift.json` records drift type,
confidence, evidence references, and partial markers when certainty is limited.

### Tests for User Story 2

- [X] T023 [P] [US2] Add unit test for documentation snippet extraction and drift rule evaluation in tests/unit/test_documentation_drift.py
- [X] T024 [P] [US2] Add integration test for documentation drift artifact generation in tests/integration/test_semanticist_drift_pipeline.py

### Implementation for User Story 2

- [X] T025 [P] [US2] Implement docstring and nearby documentation snippet extraction in src/analyzers/documentation_drift.py
- [X] T026 [P] [US2] Define documentation drift categories, confidence bands, and evidence fields in src/models/semantic.py
- [X] T027 [US2] Implement implementation-versus-documentation drift comparison workflow in src/analyzers/documentation_drift.py
- [X] T028 [US2] Persist documentation drift artifact output and partial warning propagation in src/utils/artifacts.py and src/agents/semanticist.py

**Checkpoint**: User Stories 1 and 2 should now produce grounded semantics plus
auditable documentation drift findings.

---

## Phase 5: User Story 3 - Feed Downstream Knowledge Products (Priority: P3)

**Goal**: Integrate Semanticist into the pipeline so downstream Archivist flows
can consume semantic artifacts directly with run-summary visibility and trace
logging.

**Independent Test**: Run the full pipeline after Hydrologist and verify
Semanticist artifacts are written, surfaced in run outputs, and stable enough
for downstream consumption without rescanning the repository.

### Tests for User Story 3

- [X] T029 [P] [US3] Add contract test for Semanticist run-summary and downstream artifact references in tests/contract/test_semanticist_run_summary.py
- [X] T030 [P] [US3] Add integration test for orchestrated Semanticist execution after Hydrologist in tests/integration/test_semanticist_orchestrator.py

### Implementation for User Story 3

- [X] T031 [P] [US3] Register Semanticist artifact paths, budget settings, and run-summary fields in src/config.py and src/models/state.py
- [X] T032 [P] [US3] Integrate Semanticist execution after Hydrologist in src/orchestrator.py
- [X] T033 [P] [US3] Expose Semanticist artifact references and summary details in CLI analyze output in src/cli.py
- [X] T034 [US3] Add Semanticist trace logging and stage statistics emission in src/agents/semanticist.py and src/utils/logging.py
- [X] T035 [US3] Make Semanticist artifacts Archivist-ready with stable IDs, evidence labeling, and deterministic serialization in src/models/semantic.py and src/utils/artifacts.py

**Checkpoint**: All three user stories should now be independently functional
and consumable by downstream stages.

---

## Phase 6: Polish & Cross-Cutting Concerns (Phase G - Quality)

**Purpose**: Finish resilience, regression coverage, documentation, and
cross-story validation.

- [X] T036 [P] Add unit tests for budget exhaustion and provider fallback handling in tests/unit/test_semantic_budget.py
- [X] T037 [P] Add unit tests for clustering output shape and deterministic fallback behavior in tests/unit/test_domain_clustering.py
- [X] T038 Add graceful degradation for oversized modules, provider failures, and embedding fallback in src/agents/semanticist.py and src/llm/budget.py
- [X] T039 [P] Update Semanticist usage, provider configuration, and artifact descriptions in README.md
- [X] T040 [P] Validate quickstart scenarios and refresh specs/007-semanticist-layer/quickstart.md
- [X] T041 Run the full pytest suite and fix any remaining Stage 6 regressions touching tests/

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2 / Phase A)**: Depends on Setup completion; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational completion; establishes the MVP semantic understanding path.
- **User Story 2 (Phase 4)**: Depends on User Story 1 because documentation drift compares against implementation-grounded purposes.
- **User Story 3 (Phase 5)**: Depends on User Stories 1 and 2 so downstream integration exposes the full semantic artifact set.
- **Polish (Phase 6 / Phase G)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational; no dependency on later stories.
- **User Story 2 (P2)**: Depends on US1 purpose outputs and evidence bundles but remains independently testable once those exist.
- **User Story 3 (P3)**: Depends on US1 and US2 semantic artifacts so orchestration and downstream consumption can expose the complete feature.

### Within Each User Story

- Tests MUST be written and fail before implementation.
- Shared models and artifact plumbing before agent orchestration.
- Evidence bundling before prompting or synthesis.
- Purpose extraction before domain clustering and Day-One answer assembly.
- Purpose outputs before drift comparison.
- Core artifact generation before orchestration and CLI exposure.

### Parallel Opportunities

- Setup fixture tasks marked [P] can run in parallel.
- Foundational provider, config, artifact, and budget tasks marked [P] can run in parallel once file ownership does not overlap.
- All tests for a user story marked [P] can run in parallel.
- Domain clustering and Day-One synthesis work for US1 can run in parallel after the evidence bundle and prompt seams exist.
- Orchestrator and CLI integration tasks for US3 can run in parallel.
- Polish regression and documentation tasks marked [P] can run in parallel.

---

## Parallel Example: User Story 1

```bash
# Launch all User Story 1 tests together:
Task: "Add contract test for Semanticist module, domain, and Day-One artifact schemas in tests/contract/test_semanticist_artifacts.py"
Task: "Add unit test for evidence bundle construction and bounded source excerpt selection in tests/unit/test_semantic_evidence.py"
Task: "Add integration test for Semanticist purpose, domain, and Day-One generation in tests/integration/test_semanticist_pipeline.py"

# Launch independent semantic analyzers together after the shared seams exist:
Task: "Implement evidence bundle generation from manifest, structural, module graph, lineage graph, and source excerpts in src/analyzers/semantic_evidence.py"
Task: "Implement grounded purpose and Day-One prompt builders in src/llm/prompts.py"
Task: "Implement embedding-aware domain clustering with deterministic graph and path fallback in src/analyzers/domain_clustering.py"
Task: "Implement five-question Day-One synthesis with explicit evidence citations in src/analyzers/day_one_synthesis.py"
```

## Parallel Example: User Story 2

```bash
# Launch User Story 2 test coverage together:
Task: "Add unit test for documentation snippet extraction and drift rule evaluation in tests/unit/test_documentation_drift.py"
Task: "Add integration test for documentation drift artifact generation in tests/integration/test_semanticist_drift_pipeline.py"

# Launch independent drift components together:
Task: "Implement docstring and nearby documentation snippet extraction in src/analyzers/documentation_drift.py"
Task: "Define documentation drift categories, confidence bands, and evidence fields in src/models/semantic.py"
```

## Parallel Example: User Story 3

```bash
# Launch User Story 3 tests together:
Task: "Add contract test for Semanticist run-summary and downstream artifact references in tests/contract/test_semanticist_run_summary.py"
Task: "Add integration test for orchestrated Semanticist execution after Hydrologist in tests/integration/test_semanticist_orchestrator.py"

# Launch integration wiring together after artifact contracts are stable:
Task: "Register Semanticist artifact paths, budget settings, and run-summary fields in src/config.py and src/models/state.py"
Task: "Integrate Semanticist execution after Hydrologist in src/orchestrator.py"
Task: "Expose Semanticist artifact references and summary details in CLI analyze output in src/cli.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Stop and validate `module_semantics.json`, `domain_map.json`, and `day_one_answers.json` independently.
5. Demo the semantic understanding layer before widening to drift and downstream integration.

### Incremental Delivery

1. Complete Setup + Foundational to establish Semanticist contracts, providers, budgets, and artifact plumbing.
2. Add User Story 1 to deliver grounded module purposes, domains, and Day-One answers.
3. Add User Story 2 to deliver documentation drift detection on top of grounded purpose outputs.
4. Add User Story 3 to integrate Semanticist into orchestration, CLI output, and downstream consumption.
5. Finish with resilience, README updates, quickstart validation, and full regression coverage.

### Parallel Team Strategy

1. Team completes Setup + Foundational together.
2. One developer owns provider, budget, and artifact plumbing.
3. One developer owns US1 evidence bundling and purpose extraction.
4. One developer owns US1 clustering and Day-One synthesis plus US2 drift analysis.
5. Integration and polish happen once semantic contracts and core artifacts are stable.

---

## Notes

- [P] tasks = different files, no dependencies.
- [Story] labels map every story-phase task to a specific user story.
- Each user story remains independently testable.
- Keep all artifacts, caches, and logs inside project-controlled directories.
- Preserve deterministic ordering, stable IDs, evidence labels, and explicit observation-versus-inference boundaries throughout implementation.
- Use model-backed work only behind the provider and budget abstractions; keep static fallbacks working when providers are unavailable.
