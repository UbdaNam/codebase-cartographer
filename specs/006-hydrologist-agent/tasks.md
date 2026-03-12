# Tasks: Brownfield Cartographer Stage 5 Hydrologist Agent

**Input**: Design documents from `/specs/006-hydrologist-agent/`
**Prerequisites**: plan.md (required), spec.md (required for user stories),
research.md, data-model.md, contracts/

**Tests**: Automated tests are REQUIRED for every affected stage. Include unit,
integration, contract, or regression coverage as appropriate to the feature.

**Organization**: Tasks are grouped by user story to enable independent
implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the Stage 5 workspace, fixture layout, and dependency
baseline for lineage extraction work.

- [X] T001 Update Stage 5 dependency and optional test extras in pyproject.toml
- [X] T002 [P] Add or refresh Hydrologist fixture repository skeletons under tests/fixtures/hydrologist_sql_repo/
- [X] T003 [P] Add or refresh Hydrologist fixture repository skeletons under tests/fixtures/hydrologist_python_repo/
- [X] T004 [P] Add or refresh Hydrologist fixture repository skeletons under tests/fixtures/hydrologist_partial_repo/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared lineage contracts and helpers that all user stories depend
on.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T005 Create Stage 5 lineage state and result model extensions in src/models/state.py
- [X] T006 [P] Add deterministic lineage graph payload and summary models in src/models/graph.py
- [X] T007 [P] Add dataset and transformation stable-ID helpers in src/utils/ids.py
- [X] T008 [P] Add lineage artifact write/read helpers in src/utils/artifacts.py
- [X] T009 Create shared lineage graph construction helpers in src/graph/lineage.py
- [X] T010 Create Hydrologist input-loading and stage boundary helpers in src/agents/hydrologist.py

**Checkpoint**: Shared lineage schemas, ID helpers, and artifact plumbing are
ready; user story implementation can now begin.

---

## Phase 3: User Story 1 - Generate a Deterministic Lineage Graph (Priority: P1) MVP

**Goal**: Build the core Hydrologist stage that turns deterministic lineage
signals into stable dataset, transformation, and edge artifacts.

**Independent Test**: Run analyze on a fixture repository with deterministic
lineage cues and verify `lineage_graph.json` and `lineage_summary.json` are
stable across repeated unchanged runs.

### Tests for User Story 1

- [X] T011 [P] [US1] Add contract test for lineage artifact schema and ordering in tests/contract/test_hydrologist_artifacts.py
- [X] T012 [P] [US1] Add integration test for deterministic lineage graph generation in tests/integration/test_hydrologist_pipeline.py
- [X] T013 [P] [US1] Add unit test for dataset normalization and stable lineage IDs in tests/unit/test_lineage_normalization.py

### Implementation for User Story 1

- [X] T014 [P] [US1] Add DatasetNode and TransformationNode lineage contract extensions in src/models/graph.py
- [X] T015 [P] [US1] Implement dataset identifier normalization helpers in src/graph/lineage.py
- [X] T016 [US1] Implement directed DataLineageGraph assembly with CONSUMES and PRODUCES edges in src/graph/lineage.py
- [X] T017 [US1] Implement core Hydrologist stage orchestration for graph materialization in src/agents/hydrologist.py
- [X] T018 [US1] Wire deterministic lineage graph and summary serialization in src/utils/artifacts.py
- [X] T019 [US1] Register lineage artifact references and stage stats in src/models/state.py

**Checkpoint**: User Story 1 should produce deterministic lineage artifacts from
pre-normalized lineage signals and be independently testable.

---

## Phase 4: User Story 2 - Trace Lineage Across Multiple Source Styles (Priority: P2)

**Goal**: Extract lineage signals from SQL files, embedded SQL in Python,
Python data-access patterns, and YAML/dbt-style pipeline references.

**Independent Test**: Analyze a mixed-source fixture repository and verify that
SQL, Python, and YAML lineage cues contribute the expected dataset and
transformation relationships.

### Tests for User Story 2

- [X] T020 [P] [US2] Add unit test for SQL lineage extraction and CTE handling in tests/unit/test_hydrologist_sql.py
- [X] T021 [P] [US2] Add unit test for Python data-ingestion and export pattern detection in tests/unit/test_hydrologist_python_patterns.py
- [X] T022 [P] [US2] Add unit test for YAML and dbt-style lineage references in tests/unit/test_hydrologist_yaml.py
- [X] T023 [P] [US2] Add integration test for mixed-source lineage extraction in tests/integration/test_hydrologist_mixed_sources.py

### Implementation for User Story 2

- [X] T024 [P] [US2] Implement standalone SQL and dbt-style SQL lineage extraction using sqlglot in src/agents/hydrologist.py
- [X] T025 [P] [US2] Implement embedded SQL extraction from structural and source-backed Python inputs in src/agents/hydrologist.py
- [X] T026 [P] [US2] Implement static Python data-operation detectors for pandas, Spark, SQLAlchemy, and connector patterns in src/agents/hydrologist.py
- [X] T027 [P] [US2] Implement YAML pipeline and dataset reference extraction in src/agents/hydrologist.py
- [X] T028 [US2] Merge SQL, Python, and YAML lineage signals into shared DatasetNode and TransformationNode creation in src/agents/hydrologist.py
- [X] T029 [US2] Connect multi-source lineage extraction to graph assembly in src/graph/lineage.py

**Checkpoint**: User Stories 1 and 2 should now support deterministic lineage
across the required Stage 5 source styles.

---

## Phase 5: User Story 3 - Degrade Gracefully on Partial or Dynamic Lineage (Priority: P3)

**Goal**: Preserve useful partial lineage outputs and structured warnings when
inputs are malformed, dynamic, ambiguous, or unsupported.

**Independent Test**: Analyze malformed and weak-signal fixtures and verify
that the stage emits partial artifacts plus structured warnings without
run-wide failure.

### Tests for User Story 3

- [X] T030 [P] [US3] Add unit test for malformed SQL and partial lineage warnings in tests/unit/test_hydrologist_partial_sql.py
- [X] T031 [P] [US3] Add unit test for ambiguous Python lineage and weak-signal confidence handling in tests/unit/test_hydrologist_partial_python.py
- [X] T032 [P] [US3] Add integration test for partial lineage artifact emission in tests/integration/test_hydrologist_partial_pipeline.py

### Implementation for User Story 3

- [X] T033 [P] [US3] Implement structured warning and partial-result signaling for malformed SQL, unsupported YAML, and dynamic Python cues in src/agents/hydrologist.py
- [X] T034 [P] [US3] Implement conservative confidence and support-status propagation for weak lineage signals in src/models/graph.py
- [X] T035 [US3] Preserve partial lineage graph outputs and warning summaries during degraded runs in src/graph/lineage.py
- [X] T036 [US3] Register degraded Hydrologist execution paths and warning summaries in src/models/state.py

**Checkpoint**: All three user stories should now be independently functional
with deterministic outputs and graceful degradation behavior.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finish orchestration, CLI exposure, docs, and full-stage
validation across all user stories.

- [X] T037 [P] Integrate Hydrologist stage sequencing into src/orchestrator.py
- [X] T038 [P] Expose Hydrologist lineage summary reporting in src/cli.py
- [X] T039 Update Stage 5 docs and artifact expectations in README.md
- [X] T040 [P] Add regression coverage for deterministic lineage artifact ordering in tests/integration/test_hydrologist_determinism.py
- [X] T041 Validate quickstart scenarios and update specs/006-hydrologist-agent/quickstart.md
- [X] T042 Run the full pytest suite and fix any remaining Stage 5 regressions touching tests/

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational completion; establishes the MVP lineage graph path.
- **User Story 2 (Phase 4)**: Depends on Foundational completion and integrates with US1 graph materialization.
- **User Story 3 (Phase 5)**: Depends on Foundational completion and hardens the US1/US2 lineage pipeline.
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational; no dependency on later stories.
- **User Story 2 (P2)**: Depends on the US1 graph and serialization path but remains independently testable once integrated.
- **User Story 3 (P3)**: Depends on the US1/US2 extraction flow so degraded execution can be exercised realistically.

### Within Each User Story

- Tests MUST be written and fail before implementation.
- Shared models and normalization helpers before graph assembly.
- Signal extraction before graph insertion.
- Artifact serialization before CLI and orchestration exposure.
- Story-specific behavior complete before moving to the next priority.

### Parallel Opportunities

- Setup fixture tasks marked [P] can run in parallel.
- Foundational schema and helper tasks marked [P] can run in parallel once file ownership does not overlap.
- All tests for a user story marked [P] can run in parallel.
- SQL, Python, and YAML extraction tasks for US2 can run in parallel.
- Degradation-specific warning and confidence tasks for US3 can run in parallel.
- Orchestrator and CLI integration can run in parallel during Polish.

---

## Parallel Example: User Story 2

```bash
# Launch all User Story 2 tests together:
Task: "Add unit test for SQL lineage extraction and CTE handling in tests/unit/test_hydrologist_sql.py"
Task: "Add unit test for Python data-ingestion and export pattern detection in tests/unit/test_hydrologist_python_patterns.py"
Task: "Add unit test for YAML and dbt-style lineage references in tests/unit/test_hydrologist_yaml.py"
Task: "Add integration test for mixed-source lineage extraction in tests/integration/test_hydrologist_mixed_sources.py"

# Launch source-specific extraction work together:
Task: "Implement standalone SQL and dbt-style SQL lineage extraction using sqlglot in src/agents/hydrologist.py"
Task: "Implement embedded SQL extraction from structural and source-backed Python inputs in src/agents/hydrologist.py"
Task: "Implement static Python data-operation detectors for pandas, Spark, SQLAlchemy, and connector patterns in src/agents/hydrologist.py"
Task: "Implement YAML pipeline and dataset reference extraction in src/agents/hydrologist.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Stop and validate deterministic lineage graph generation independently.
5. Demo or checkpoint before widening extraction coverage.

### Incremental Delivery

1. Complete Setup + Foundational to establish lineage graph contracts and helpers.
2. Add User Story 1 to deliver deterministic lineage graph artifacts.
3. Add User Story 2 to widen extraction coverage across SQL, Python, and YAML sources.
4. Add User Story 3 to harden degraded execution and partial-result behavior.
5. Finish with orchestrator, CLI, docs, and full validation.

### Parallel Team Strategy

1. Team completes Setup + Foundational together.
2. One developer owns US1 graph contracts and serialization.
3. A second developer owns US2 SQL and Python extraction.
4. A third developer owns US2 YAML extraction and US3 degradation hardening.
5. Integration happens in Polish once shared graph contracts are stable.

---

## Notes

- [P] tasks = different files, no dependencies.
- [Story] labels map every story-phase task to a specific user story.
- Each user story remains independently testable.
- Keep all artifacts, caches, and logs inside project-controlled directories.
- Do not widen Stage 5 into semantic analysis, embeddings, LangGraph query logic, or LLM-backed summarization.
- Preserve deterministic ordering, stable IDs, evidence metadata, and structured warnings throughout implementation.
