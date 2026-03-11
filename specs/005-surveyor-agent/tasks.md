# Tasks: Brownfield Cartographer Stage 4 Surveyor Agent

**Input**: Design documents from `/specs/005-surveyor-agent/`
**Prerequisites**: plan.md (required), spec.md (required for user stories),
research.md, data-model.md, contracts/

**Tests**: Automated tests are REQUIRED for every affected stage. Include unit,
integration, contract, and regression coverage for graph construction, git
velocity behavior, PageRank, SCC detection, dead code heuristics, graceful
degradation, and deterministic artifacts.

**Organization**: Tasks are grouped by user story to enable independent
implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g. US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project layout under `src/` and `tests/`
- Surveyor agent logic in `src/agents/`
- Graph helpers in `src/graph/`
- Typed model and state updates in `src/models/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish Stage 4 files, dependencies, and test scaffolding

- [X] T001 Create the Stage 4 Surveyor module skeleton in `src/agents/surveyor.py`
- [X] T002 [P] Create the graph-analysis helper module skeleton in `src/graph/survey.py`
- [X] T003 [P] Create Stage 4 test file skeletons in `tests/unit/test_surveyor_agent.py`, `tests/unit/test_git_velocity.py`, `tests/unit/test_survey_graph.py`, `tests/integration/test_surveyor_pipeline.py`, and `tests/contract/test_surveyor_artifacts.py`
- [X] T004 [P] Update dependency and project metadata for Stage 4 requirements in `pyproject.toml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared Surveyor infrastructure that MUST be complete before user
story work can begin

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Extend Stage 1 graph and artifact contracts for Surveyor outputs in `src/models/graph.py`
- [X] T006 [P] Extend run and analysis state to register Surveyor artifacts, stats, and partial-result markers in `src/models/state.py`
- [X] T007 [P] Add deterministic Surveyor artifact helpers for module graph and survey summary outputs in `src/utils/artifacts.py`
- [X] T008 Create normalized module-identity and dependency-key helpers in `src/utils/ids.py`
- [X] T009 Define shared graph-construction and velocity utility interfaces in `src/graph/survey.py`
- [X] T010 [P] Add foundational contract coverage for Surveyor graph payloads and state registration in `tests/contract/test_surveyor_artifacts.py`
- [X] T011 [P] Add foundational unit coverage for module normalization and stable key generation in `tests/unit/test_survey_graph.py`

**Checkpoint**: Surveyor foundations are ready; user story work can now begin

---

## Phase 3: User Story 1 - Generate an Architectural Module Map (Priority: P1) MVP

**Goal**: Turn structural extraction outputs into deterministic module records,
dependency edges, and architectural graph artifacts.

**Independent Test**: Run analysis on a fixture repository with structural
artifacts and verify stable module nodes, import edges, hub rankings, circular
dependency groups, and deterministic `.cartography` artifacts.

### Tests for User Story 1

- [X] T012 [P] [US1] Add unit tests for mapping structural results into module records in `tests/unit/test_surveyor_agent.py`
- [X] T013 [P] [US1] Add unit tests for import-graph construction, PageRank ordering, and SCC detection in `tests/unit/test_survey_graph.py`
- [X] T014 [P] [US1] Add integration coverage for deterministic Surveyor artifact generation in `tests/integration/test_surveyor_pipeline.py`

### Implementation for User Story 1

- [X] T015 [P] [US1] Implement structural-to-module mapping and evidence attachment in `src/agents/surveyor.py`
- [X] T016 [P] [US1] Implement directed import-graph construction from module dependencies in `src/graph/survey.py`
- [X] T017 [US1] Implement PageRank, strongly connected component, and simple degree analytics in `src/graph/survey.py`
- [X] T018 [US1] Implement deterministic module graph and survey summary serialization in `src/agents/surveyor.py`
- [X] T019 [US1] Wire Surveyor artifact registration into analysis state in `src/models/state.py`

**Checkpoint**: User Story 1 should now produce a deterministic architectural
module map and related artifacts independently

---

## Phase 4: User Story 2 - Surface Change and Risk Signals (Priority: P2)

**Goal**: Add recent-change velocity, high-velocity core detection, and
conservative dead code candidate signals to the Surveyor outputs.

**Independent Test**: Run analysis on fixtures with known recent-change and
dependency shapes and verify stable velocity rankings, high-velocity core
membership, and heuristic dead code candidates.

### Tests for User Story 2

- [X] T020 [P] [US2] Add unit tests for git velocity extraction and bounded lookback behavior in `tests/unit/test_git_velocity.py`
- [X] T021 [P] [US2] Add unit tests for high-velocity core calculation and dead code heuristic scoring in `tests/unit/test_surveyor_agent.py`
- [X] T022 [P] [US2] Add integration coverage for Surveyor change-signal summaries in `tests/integration/test_surveyor_pipeline.py`

### Implementation for User Story 2

- [X] T023 [P] [US2] Implement repository-scoped git velocity extraction and graceful-missing-history handling in `src/agents/surveyor.py`
- [X] T024 [P] [US2] Implement deterministic high-velocity core calculation in `src/graph/survey.py`
- [X] T025 [US2] Attach velocity metrics and high-velocity-core membership to module records in `src/agents/surveyor.py`
- [X] T026 [US2] Implement conservative dead code candidate heuristics and confidence labeling in `src/agents/surveyor.py`
- [X] T027 [US2] Extend survey summary serialization for velocity and dead code signals in `src/agents/surveyor.py`

**Checkpoint**: User Stories 1 and 2 should now produce architectural graph
outputs plus change and risk signals independently

---

## Phase 5: User Story 3 - Degrade Gracefully on Incomplete Inputs (Priority: P3)

**Goal**: Preserve useful partial outputs when git metadata, structural
records, or dependency resolution are incomplete.

**Independent Test**: Run analysis on fixtures with missing git metadata,
unresolved imports, and partial structural extraction, then verify partial
artifacts plus structured warnings without run failure.

### Tests for User Story 3

- [X] T028 [P] [US3] Add unit tests for unresolved-import and partial-record handling in `tests/unit/test_surveyor_agent.py`
- [X] T029 [P] [US3] Add integration tests for missing git metadata and partial Surveyor runs in `tests/integration/test_surveyor_pipeline.py`
- [X] T030 [P] [US3] Add contract tests for warning and partial-result serialization in `tests/contract/test_surveyor_artifacts.py`

### Implementation for User Story 3

- [X] T031 [P] [US3] Implement unresolved dependency preservation and warning generation in `src/agents/surveyor.py`
- [X] T032 [P] [US3] Implement partial-result summary and warning aggregation in `src/graph/survey.py`
- [X] T033 [US3] Integrate graceful-degradation handling into Surveyor artifact emission in `src/agents/surveyor.py`
- [X] T034 [US3] Update state registration for partial Surveyor completion and warning summaries in `src/models/state.py`

**Checkpoint**: All three user stories should now work independently, with
partial-result behavior preserved for messy brownfield inputs

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Complete end-to-end integration, CLI exposure, and deterministic
validation across the whole stage

- [X] T035 [P] Update orchestrator sequencing so Surveyor runs after structural extraction in `src/orchestrator.py`
- [X] T036 [P] Update CLI analyze reporting for module count, import edge count, hub summary, circular dependency count, and high-velocity summary in `src/cli.py`
- [X] T037 [P] Add or refresh Surveyor fixture repositories and expected outputs in `tests/fixtures/`
- [X] T038 Run end-to-end Surveyor integration validation and refine deterministic ordering assertions in `tests/integration/test_surveyor_pipeline.py`
- [X] T039 [P] Update Stage 4 documentation and usage notes in `README.md` and `specs/005-surveyor-agent/quickstart.md`
- [X] T040 Validate `.cartography` output placement, deterministic serialization, and non-destructive behavior across Stage 4 artifacts in `tests/contract/test_surveyor_artifacts.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user
  stories
- **User Stories (Phase 3+)**: Depend on Foundational completion
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational and delivers the MVP
- **User Story 2 (P2)**: Starts after Foundational; builds on the module graph
  outputs from US1 but remains independently testable
- **User Story 3 (P3)**: Starts after Foundational; validates resilience over
  US1/US2 behaviors and remains independently testable

### Within Each User Story

- Tests must be written and fail before implementation
- Mapping and model updates before graph analytics attachment
- Core graph or velocity logic before orchestrator and CLI integration
- Story-specific artifact serialization before final integration checks

### Parallel Opportunities

- Setup tasks marked `[P]` can run in parallel
- Foundational tasks marked `[P]` can run in parallel after file ownership is
  clear
- User-story test tasks marked `[P]` can run in parallel
- Graph-helper work and Surveyor-agent work can proceed in parallel when they
  target different files
- Polish tasks for docs, CLI, and fixture refresh can run in parallel once
  core Surveyor logic stabilizes

---

## Parallel Example: User Story 1

```bash
# Launch all User Story 1 tests together:
Task: "Add unit tests for mapping structural results into module records in tests/unit/test_surveyor_agent.py"
Task: "Add unit tests for import-graph construction, PageRank ordering, and SCC detection in tests/unit/test_survey_graph.py"
Task: "Add integration coverage for deterministic Surveyor artifact generation in tests/integration/test_surveyor_pipeline.py"

# Launch User Story 1 implementation work in parallel where files do not overlap:
Task: "Implement structural-to-module mapping and evidence attachment in src/agents/surveyor.py"
Task: "Implement directed import-graph construction from module dependencies in src/graph/survey.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate deterministic module graph outputs independently
5. Stop for review before change and risk signals

### Incremental Delivery

1. Build the Surveyor foundation and deterministic graph pipeline
2. Deliver User Story 1 for architectural module mapping
3. Add User Story 2 for velocity and dead code signals
4. Add User Story 3 for partial-result resilience
5. Finish with CLI, orchestrator, fixtures, and documentation polish

### Parallel Team Strategy

1. One developer completes setup and foundational contract/state work
2. One developer implements graph helpers in `src/graph/survey.py`
3. One developer implements Surveyor orchestration in `src/agents/surveyor.py`
4. Another developer expands tests and fixtures in `tests/`
5. Integrate once the module graph contract is stable

---

## Notes

- `[P]` tasks touch different files and are safe to parallelize
- Keep Stage 4 limited to Surveyor responsibilities only
- Do not pull SQL lineage, Hydrologist logic, semantic indexing, LangGraph
  workflows, or LLM features into this stage
- All artifacts, cache, and logs must remain in project-controlled directories
- Preserve deterministic ordering and explicit evidence labeling in every
  durable Surveyor output
