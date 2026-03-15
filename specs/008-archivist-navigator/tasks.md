# Tasks: Archivist Navigator Stage

**Input**: Design documents from `/specs/008-archivist-navigator/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Automated tests are REQUIRED for every affected stage. Include unit, integration, contract, and regression coverage for Archivist artifacts, LangGraph Navigator flows, trace logging, and incremental refresh behavior.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story while honoring the requested Archivist/Navigator phase breakdown.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Phase A — Archivist Foundations)

**Purpose**: Establish final-stage modules, schemas, utilities, and metadata seams shared by all later work.

- [X] T001 Create Archivist agent scaffold in `src/agents/archivist.py`
- [X] T002 [P] Create Navigator agent scaffold in `src/agents/navigator.py`
- [X] T003 [P] Define Archivist artifact schemas for `CODEBASE.md`, `onboarding_brief.md`, `lineage_graph.json`, `semantic_index`, and `cartography_trace.jsonl` in `src/models/archivist.py`
- [X] T004 [P] Define shared evidence and citation formatting utilities in `src/utils/citations.py`
- [X] T005 [P] Add run metadata and incremental baseline models in `src/models/run_metadata.py`
- [X] T006 Add final-stage configuration entries for artifact paths, LangGraph settings, and incremental refresh options in `src/config.py`

---

## Phase 2: Foundational (Phase B/C Shared Infrastructure)

**Purpose**: Build shared infrastructure for living artifacts, traceability, and deterministic reuse before user story work begins.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T007 Define append-only trace event schema with confidence and method-type fields in `src/models/trace.py`
- [X] T008 [P] Implement artifact path helpers for final-stage outputs in `src/utils/artifacts.py`
- [X] T009 [P] Implement append-only `cartography_trace.jsonl` writer utilities in `src/utils/trace.py`
- [X] T010 [P] Implement semantic index storage primitives and metadata persistence in `src/index/semantic_index.py`
- [X] T011 [P] Add contract coverage for Archivist artifact schemas in `tests/contract/test_archivist_artifacts.py`
- [X] T012 [P] Add contract coverage for Navigator LangGraph request/response contracts in `tests/contract/test_navigator_contracts.py`

**Checkpoint**: Final-stage foundations are ready; living artifact generation, Navigator flows, and incremental refresh can proceed.

---

## Phase 3: User Story 1 - Produce Living Context Artifacts (Priority: P1) MVP

**Goal**: Generate the final living-context artifacts from Surveyor, Hydrologist, and Semanticist outputs with preserved evidence and trust metadata.

**Independent Test**: Run the pipeline on a fixture repository and verify that `CODEBASE.md`, `onboarding_brief.md`, `lineage_graph.json`, `semantic_index/`, and `cartography_trace.jsonl` are created under `.cartography/` with the required sections, citations, and trust labels.

### Tests for User Story 1

- [X] T013 [P] [US1] Add unit tests for `generate_CODEBASE_md()` section rendering in `tests/unit/test_archivist_codebase_md.py`
- [X] T014 [P] [US1] Add unit tests for onboarding brief evidence formatting in `tests/unit/test_archivist_onboarding_brief.py`
- [X] T015 [P] [US1] Add unit tests for semantic index build/update behavior in `tests/unit/test_semantic_index.py`
- [X] T016 [P] [US1] Add integration coverage for final artifact generation in `tests/integration/test_archivist_pipeline.py`

### Implementation for User Story 1

- [X] T017 [P] [US1] Implement `generate_CODEBASE_md()` with required sections in `src/agents/archivist.py`
- [X] T018 [P] [US1] Implement `onboarding_brief.md` generation from Semanticist Day-One answers in `src/agents/archivist.py`
- [X] T019 [P] [US1] Implement final `lineage_graph.json` serialization and metadata preservation in `src/agents/archivist.py`
- [X] T020 [P] [US1] Implement semantic index build/update pipeline from module purpose statements in `src/index/semantic_index.py`
- [X] T021 [US1] Implement observed-vs-inferred labeling rules for final artifacts in `src/utils/citations.py`
- [X] T022 [US1] Ensure generated artifacts preserve evidence references in `src/agents/archivist.py`
- [X] T023 [US1] Wire Archivist artifact writing and mirrored latest-run handling in `src/utils/artifacts.py`
- [X] T024 [US1] Update `src/orchestrator.py` to include Archivist after Semanticist for analyze flows

**Checkpoint**: User Story 1 is complete when the final pipeline emits all required living artifacts with deterministic structure and trust metadata.

---

## Phase 4: User Story 2 - Query the Codebase Through Navigator (Priority: P2)

**Goal**: Deliver a retrieval-first LangGraph Navigator with exactly four required tools and evidence-backed responses.

**Independent Test**: Run Navigator queries against an analyzed fixture repository and verify that `find_implementation`, `trace_lineage`, `blast_radius`, and `explain_module` all return structured responses with file path, line range where available, analysis method, and explicit trust labels.

### Tests for User Story 2

- [X] T025 [P] [US2] Add unit tests for LangGraph Navigator state transitions in `tests/unit/test_navigator_langgraph.py`
- [X] T026 [P] [US2] Add unit tests for Navigator citation and trust attachment in `tests/unit/test_navigator_citations.py`
- [X] T027 [P] [US2] Add integration coverage for Navigator queries with file/line/method citations in `tests/integration/test_navigator_queries.py`

### Implementation for User Story 2

- [X] T028 [P] [US2] Define LangGraph Navigator state model in `src/models/navigator.py`
- [X] T029 [P] [US2] Implement `classify_query` and `retrieve_relevant_artifacts` nodes in `src/agents/navigator.py`
- [X] T030 [P] [US2] Implement `select_tool`, `execute_tool`, `synthesize_response`, and `attach_citations_and_trust_metadata` nodes in `src/agents/navigator.py`
- [X] T031 [P] [US2] Implement `find_implementation(concept)` in `src/agents/navigator.py`
- [X] T032 [P] [US2] Implement `trace_lineage(dataset, direction)` in `src/agents/navigator.py`
- [X] T033 [P] [US2] Implement `blast_radius(module_path)` in `src/agents/navigator.py`
- [X] T034 [P] [US2] Implement `explain_module(path)` in `src/agents/navigator.py`
- [X] T035 [US2] Wire retrieval-first LangGraph assembly and tool routing in `src/agents/navigator.py`
- [X] T036 [US2] Update `src/cli.py` with query subcommand routing into the LangGraph Navigator

**Checkpoint**: User Story 2 is complete when the query interface answers all four required query types through the LangGraph Navigator with explicit evidence and trust metadata.

---

## Phase 5: User Story 3 - Refresh Living Context Incrementally (Priority: P3)

**Goal**: Refresh only changed files and dependent final artifacts using git baseline metadata and selective invalidation.

**Independent Test**: Run the final stage twice on a fixture repository with limited changes between runs and verify that unaffected artifacts are reused, affected outputs are refreshed, and the reuse decisions appear in run metadata and trace output.

### Tests for User Story 3

- [X] T037 [P] [US3] Add unit tests for incremental baseline detection and invalidation logic in `tests/unit/test_archivist_incremental.py`
- [X] T038 [P] [US3] Add unit tests for trace logging append and reuse-status behavior in `tests/unit/test_trace_logging.py`
- [X] T039 [P] [US3] Add integration coverage for incremental final-stage refresh in `tests/integration/test_archivist_incremental_pipeline.py`

### Implementation for User Story 3

- [X] T040 [P] [US3] Persist last analyzed commit metadata and source coverage in `src/models/run_metadata.py`
- [X] T041 [P] [US3] Implement changed-file detection from git diff/log in `src/utils/incremental.py`
- [X] T042 [P] [US3] Implement selective downstream artifact refresh decisions in `src/agents/archivist.py`
- [X] T043 [US3] Regenerate only affected final artifacts and semantic index segments in `src/agents/archivist.py`
- [X] T044 [US3] Wire incremental baseline loading and saving in `src/utils/artifacts.py`
- [X] T045 [US3] Update `src/orchestrator.py` to reuse final-stage artifacts when upstream inputs are unchanged

**Checkpoint**: User Story 3 is complete when reruns refresh only affected final-stage outputs and capture reuse versus regeneration deterministically.

---

## Phase 6: Polish & Cross-Cutting Concerns (Phase F/H)

**Purpose**: Finish pipeline integration, documentation, and regression validation across all stories.

- [X] T046 [P] Add full final pipeline integration coverage for Archivist after Semanticist in `tests/integration/test_final_pipeline.py`
- [X] T047 [P] Add regression coverage for deterministic final artifact ordering and query outputs in `tests/integration/test_archivist_determinism.py`
- [X] T048 Update `src/models/state.py` with Archivist and Navigator run-summary fields
- [X] T049 Update `README.md` for analyze and query workflows
- [X] T050 Validate final output placement, evidence preservation, and partial-result behavior in `src/utils/artifacts.py`
- [X] T051 Run quickstart validation from `specs/008-archivist-navigator/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories
- **User Stories (Phase 3+)**: All depend on Foundational completion
- **Polish (Phase 6)**: Depends on the desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational; no dependency on other stories
- **User Story 2 (P2)**: Starts after Foundational and depends on generated Archivist artifacts from US1 for realistic query execution
- **User Story 3 (P3)**: Starts after Foundational and depends on Archivist artifact generation paths from US1

### Within Each User Story

- Tests must be written and fail before implementation
- Shared schemas and utilities before orchestration wiring
- Retrieval before synthesis
- Incremental baseline detection before selective refresh integration

### Parallel Opportunities

- Setup tasks marked `[P]` can run in parallel
- Foundational trace/index/contract tasks marked `[P]` can run in parallel
- All tests within each user story marked `[P]` can run in parallel
- The four required Navigator tools can be implemented in parallel once state and routing nodes exist

---

## Parallel Example: User Story 1

```bash
# Launch User Story 1 tests together:
Task: "Add unit tests for generate_CODEBASE_md() section rendering in tests/unit/test_archivist_codebase_md.py"
Task: "Add unit tests for onboarding brief evidence formatting in tests/unit/test_archivist_onboarding_brief.py"
Task: "Add unit tests for semantic index build/update behavior in tests/unit/test_semantic_index.py"
Task: "Add integration coverage for final artifact generation in tests/integration/test_archivist_pipeline.py"

# Launch independent implementation tasks together:
Task: "Implement generate_CODEBASE_md() with required sections in src/agents/archivist.py"
Task: "Implement onboarding_brief.md generation from Semanticist Day-One answers in src/agents/archivist.py"
Task: "Implement final lineage_graph.json serialization and metadata preservation in src/agents/archivist.py"
Task: "Implement semantic index build/update pipeline from module purpose statements in src/index/semantic_index.py"
```

---

## Parallel Example: User Story 2

```bash
# Launch Navigator tests together:
Task: "Add unit tests for LangGraph Navigator state transitions in tests/unit/test_navigator_langgraph.py"
Task: "Add unit tests for Navigator citation and trust attachment in tests/unit/test_navigator_citations.py"
Task: "Add integration coverage for Navigator queries with file/line/method citations in tests/integration/test_navigator_queries.py"

# Launch required tool implementations together:
Task: "Implement find_implementation(concept) in src/agents/navigator.py"
Task: "Implement trace_lineage(dataset, direction) in src/agents/navigator.py"
Task: "Implement blast_radius(module_path) in src/agents/navigator.py"
Task: "Implement explain_module(path) in src/agents/navigator.py"
```

---

## Parallel Example: User Story 3

```bash
# Launch incremental-mode tests together:
Task: "Add unit tests for incremental baseline detection and invalidation logic in tests/unit/test_archivist_incremental.py"
Task: "Add unit tests for trace logging append and reuse-status behavior in tests/unit/test_trace_logging.py"
Task: "Add integration coverage for incremental final-stage refresh in tests/integration/test_archivist_incremental_pipeline.py"

# Launch independent incremental primitives together:
Task: "Implement changed-file detection from git diff/log in src/utils/incremental.py"
Task: "Persist last analyzed commit metadata and source coverage in src/models/run_metadata.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate final living artifacts independently

### Incremental Delivery

1. Complete Setup + Foundational
2. Deliver Archivist living artifacts (US1)
3. Deliver LangGraph Navigator query capability (US2)
4. Deliver incremental refresh behavior (US3)
5. Finish with cross-cutting regressions and documentation updates

### Parallel Team Strategy

1. One developer completes Setup + Foundational schema and utility work
2. One developer implements Archivist artifact generation and trace preservation
3. One developer implements LangGraph Navigator state flow and required tools
4. One developer implements incremental baseline and refresh logic

---

## Notes

- All tasks follow the required checklist format with explicit file paths.
- Tests are included because the specification and constitution require automated coverage for every affected stage.
- Final artifacts, semantic index files, trace logs, and incremental metadata must remain inside project-controlled `.cartography/` directories.
- Preserve deterministic ordering, stable IDs, explicit trust labels, and retrieval-first behavior across all final-stage outputs and query responses.
