---

description: "Task list for Brownfield Cartographer Stage 1 typed contracts"
---

# Tasks: Brownfield Cartographer Stage 1 Typed Contracts

**Input**: Design documents from `/specs/002-define-typed-contracts/`
**Prerequisites**: plan.md (required), spec.md (required for user stories),
research.md, data-model.md, contracts/

**Tests**: Automated tests are REQUIRED for every affected stage. Include unit,
integration, contract, or regression coverage as appropriate to the feature.

**Organization**: Tasks are grouped by user story to enable independent
implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths below assume the Stage 1 `src/models/` contract structure from plan.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the Stage 1 modeling file layout and project metadata

- [x] T001 Create the Stage 1 contract module files in `src/models/enums.py`, `src/models/evidence.py`, `src/models/graph.py`, `src/models/artifacts.py`, `src/models/state.py`, and `src/utils/ids.py`
- [x] T002 Confirm `pyproject.toml` includes the Stage 1 dependency and test baseline for Python 3.11+, Pydantic v2, and pytest
- [x] T003 [P] Add Stage 1 package exports in `src/models/__init__.py`
- [x] T004 [P] Update high-level Stage 1 overview text in `README.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core contract primitives that all Stage 1 user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Define stable string enums for node kinds, edge kinds, support status, analysis method, skip reasons, and confidence bands in `src/models/enums.py`
- [x] T006 [P] Implement canonicalization and deterministic ID helpers in `src/utils/ids.py`
- [x] T007 [P] Implement reusable evidence and citation base models in `src/models/evidence.py`
- [x] T008 Implement shared serialization helpers and artifact metadata contracts in `src/models/artifacts.py`
- [x] T009 [P] Add foundational enum and ID tests in `tests/unit/test_enums.py` and `tests/unit/test_ids.py`

**Checkpoint**: Foundational contract primitives are ready for story-specific
modeling work

---

## Phase 3: User Story 1 - Share Stable Analysis Contracts (Priority: P1) MVP

**Goal**: Deliver the core graph, artifact, and pipeline-state contracts that
later stages can share deterministically

**Independent Test**: A developer can instantiate core graph, artifact, and
pipeline state models, serialize them repeatedly, and confirm stable enum
values, stable IDs, and deterministic output structure

### Tests for User Story 1

> **NOTE**: Write these tests FIRST and ensure they FAIL before implementation

- [x] T010 [P] [US1] Add graph-model validation tests in `tests/unit/test_graph_models.py`
- [x] T011 [P] [US1] Add pipeline-state validation tests in `tests/unit/test_state_models.py`
- [x] T012 [P] [US1] Add serialization stability tests for graph payloads and analysis artifacts in `tests/integration/test_serialization_contracts.py`

### Implementation for User Story 1

- [x] T013 [P] [US1] Implement base graph node, module node, dataset node, and transformation node schemas in `src/models/graph.py`
- [x] T014 [US1] Implement graph edge schemas and graph container payload models in `src/models/graph.py`
- [x] T015 [US1] Implement analysis artifact contracts and deterministic serialization payload models in `src/models/artifacts.py`
- [x] T016 [US1] Implement `RunContext` and `AnalysisState` models in `src/models/state.py`
- [x] T017 [US1] Export Stage 1 contract families from `src/models/__init__.py`

**Checkpoint**: User Story 1 should be fully functional and independently
testable as the Stage 1 MVP

---

## Phase 4: User Story 2 - Preserve Evidence and Partial Results (Priority: P2)

**Goal**: Deliver reusable evidence-aware contracts and explicit support for
partial, skipped, and degraded analysis outcomes

**Independent Test**: A developer can create evidence-backed graph and artifact
records with optional line data, mixed support statuses, and degraded contexts
without validation failures or unstable serialization

### Tests for User Story 2

- [x] T018 [P] [US2] Add evidence-model tests for optional line numbers and citation behavior in `tests/unit/test_evidence.py`
- [x] T019 [P] [US2] Add partial-data and support-status coverage tests in `tests/unit/test_graph_models.py`
- [x] T020 [P] [US2] Add regression tests for degraded artifact serialization in `tests/integration/test_serialization_contracts.py`

### Implementation for User Story 2

- [x] T021 [P] [US2] Implement evidence and citation detail models in `src/models/evidence.py`
- [x] T022 [US2] Add support-status, confidence, and skip-reason fields to graph and artifact contracts in `src/models/graph.py` and `src/models/artifacts.py`
- [x] T023 [US2] Add partial-result and skipped-summary support to `AnalysisState` in `src/models/state.py`
- [x] T024 [US2] Document evidence and degraded-output contract expectations in `specs/002-define-typed-contracts/contracts/model-contracts.md`

**Checkpoint**: User Story 2 should be independently testable with evidence,
partial-result, and degraded-output scenarios

---

## Phase 5: User Story 3 - Prepare Navigator and Multi-Agent State (Priority: P3)

**Goal**: Deliver typed state for future Navigator query execution and preserve
clean shared seams for later multi-agent workflows

**Independent Test**: A developer can instantiate future query state with query
text, artifact references, evidence context, tool history, and citations
without requiring LangGraph workflow execution

### Tests for User Story 3

- [x] T025 [P] [US3] Add Navigator-state validation tests in `tests/unit/test_state_models.py`
- [x] T026 [P] [US3] Add contract-compatibility tests covering shared agent-facing state defaults in `tests/integration/test_serialization_contracts.py`

### Implementation for User Story 3

- [x] T027 [P] [US3] Implement `NavigatorState` and related query-response fields in `src/models/state.py`
- [x] T028 [US3] Add shared agent-facing metadata and future workflow-facing fields to `RunContext` and `AnalysisState` in `src/models/state.py`
- [x] T029 [US3] Update Stage 1 quickstart guidance for query-state and contract validation in `specs/002-define-typed-contracts/quickstart.md`

**Checkpoint**: All user stories should now be independently functional and the
Stage 1 contract layer should be ready for later stages

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup across all Stage 1 contracts

- [x] T030 [P] Run the full pytest suite for Stage 1 contract coverage in `tests/unit/` and `tests/integration/`
- [x] T031 [P] Validate deterministic JSON serialization examples against `specs/002-define-typed-contracts/quickstart.md`
- [x] T032 Verify stable ID behavior and contract exports across `src/models/` and `src/utils/ids.py`
- [x] T033 [P] Clean up docstrings, typing, and field descriptions in `src/models/enums.py`, `src/models/evidence.py`, `src/models/graph.py`, `src/models/artifacts.py`, and `src/models/state.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion; recommended MVP
- **User Story 2 (Phase 4)**: Depends on Foundational completion and builds on shared evidence, enum, and artifact primitives
- **User Story 3 (Phase 5)**: Depends on Foundational completion and can follow once shared state contracts are stable
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: No dependency on other user stories; establishes the core contract layer
- **User Story 2 (P2)**: Independent in value, but extends the core contract layer with evidence and degraded-result behavior
- **User Story 3 (P3)**: Independent in value, but safest after shared run and artifact contracts exist

### Within Each User Story

- Tests MUST be written and fail before implementation
- Enums and ID helpers before graph and artifact schemas
- Evidence models before graph and state fields that reference them
- State models after shared evidence and artifact contracts exist
- Story documentation after implementation behavior stabilizes

### Parallel Opportunities

- Setup tasks `T003` and `T004` can run in parallel after `T001` and `T002`
- Foundational tasks `T006`, `T007`, and `T009` can run in parallel after `T005`
- User Story 1 test tasks `T010` to `T012` can run in parallel
- User Story 2 test tasks `T018` to `T020` can run in parallel
- User Story 3 tasks `T025` and `T027` can run in parallel once shared state primitives exist
- Polish tasks `T030`, `T031`, and `T033` can run in parallel once implementation is complete

---

## Parallel Example: User Story 1

```bash
Task: "Add graph-model validation tests in tests/unit/test_graph_models.py"
Task: "Add pipeline-state validation tests in tests/unit/test_state_models.py"
Task: "Add serialization stability tests for graph payloads and analysis artifacts in tests/integration/test_serialization_contracts.py"
```

## Parallel Example: User Story 2

```bash
Task: "Add evidence-model tests for optional line numbers and citation behavior in tests/unit/test_evidence.py"
Task: "Add partial-data and support-status coverage tests in tests/unit/test_graph_models.py"
Task: "Add regression tests for degraded artifact serialization in tests/integration/test_serialization_contracts.py"
```

## Parallel Example: User Story 3

```bash
Task: "Add Navigator-state validation tests in tests/unit/test_state_models.py"
Task: "Implement NavigatorState and related query-response fields in src/models/state.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate deterministic graph/artifact/state serialization
5. Stop and review the Stage 1 MVP before adding degraded-result and Navigator work

### Incremental Delivery

1. Complete Setup + Foundational to stabilize enums, IDs, and evidence primitives
2. Add User Story 1 for the shared contract MVP
3. Add User Story 2 for evidence-aware and partial-result behavior
4. Add User Story 3 for future Navigator and multi-agent state
5. Finish with Phase 6 validation and cleanup

### Parallel Team Strategy

1. One contributor handles enum, ID, and evidence primitives (`T005` to `T009`)
2. One contributor handles graph and artifact models (`T010` to `T024`)
3. One contributor handles pipeline and Navigator state (`T011`, `T016`, `T023`, `T025` to `T029`)
4. Merge on the Phase 6 validation tasks once story phases are complete

---

## Notes

- All tasks use the required checklist format with checkbox, task ID, labels,
  and explicit file paths where applicable
- User Story 1 is the recommended MVP scope
- The task list intentionally excludes parsing, graph algorithms, LangGraph
  workflow execution, and agent implementation
- Each user story remains independently testable and focused on contracts only
