---

description: "Task list for Brownfield Cartographer Stage 3 repository input resolution and structural analysis"
---

# Tasks: Brownfield Cartographer Stage 3 Repository Input Resolution and Structural Analysis

**Input**: Design documents from `/specs/004-structural-analysis/`
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
- Paths below assume the Stage 3 single-project layout from plan.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare Stage 3 dependencies, fixture layout, and documentation

- [X] T001 Confirm `pyproject.toml` includes the Stage 3 Python 3.11+, Pydantic v2, pydantic-settings, Typer, pytest, and tree-sitter baseline
- [X] T002 Create the Stage 3 fixture repository directories in `tests/fixtures/structural_local_repo/`, `tests/fixtures/structural_polyglot_repo/`, and `tests/fixtures/structural_malformed_repo/`
- [X] T003 [P] Update the Stage 3 overview and CLI expectations in `README.md`
- [X] T004 [P] Add Stage 3 validation notes and fixture usage guidance in `specs/004-structural-analysis/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core preparation, routing, and typed structural foundations that all user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create typed repository input and prepared-repository models in `src/models/repository_input.py`
- [X] T006 [P] Create typed structural result and artifact payload models in `src/models/structural.py`
- [X] T007 [P] Add Stage 3 repository-preparation and structural artifact settings in `src/config.py` and `src/constants.py`
- [X] T008 [P] Add deterministic repository identity and prepared-repo path helpers in `src/utils/ids.py`
- [X] T009 Implement centralized `LanguageRouter` capability and parser-routing contracts in `src/utils/language_router.py`
- [X] T010 [P] Add foundational unit coverage for repository identity, structural models, and language routing in `tests/unit/test_repository_input_models.py`, `tests/unit/test_structural_models.py`, and `tests/unit/test_language_router.py`

**Checkpoint**: Foundation ready; repository preparation and structural extraction stories can now begin

---

## Phase 3: User Story 1 - Resolve Repository Input For Analysis (Priority: P1) MVP

**Goal**: Accept local paths and Git URLs, prepare or reuse a safe local repository root, and hand that root to downstream analysis

**Independent Test**: A developer can analyze one local path input and one Git URL input and verify that both produce a deterministic local analysis root and preparation metadata without requiring structural extraction

### Tests for User Story 1

> **NOTE**: Write these tests FIRST and ensure they FAIL before implementation

- [X] T011 [P] [US1] Add repository-input model and validation tests in `tests/unit/test_repository_input_models.py`
- [X] T012 [P] [US1] Add repository preparation and clone-reuse tests in `tests/integration/test_repository_preparation.py`
- [X] T013 [P] [US1] Add CLI and orchestrator repository-input resolution tests in `tests/contract/test_repository_input_cli_contract.py`

### Implementation for User Story 1

- [X] T014 [P] [US1] Implement repository input parsing and URL detection in `src/models/repository_input.py` and `src/utils/repository_preparation.py`
- [X] T015 [US1] Implement shallow clone, local path validation, and clone-reuse behavior in `src/utils/repository_preparation.py`
- [X] T016 [US1] Integrate repository preparation into the analyze flow in `src/orchestrator.py`
- [X] T017 [US1] Update the CLI analyze entrypoint to accept local paths and Git URLs in `src/cli.py`
- [X] T018 [US1] Add prepared-repository metadata and artifact-path updates in `src/models/state.py` and `src/models/run_metadata.py`

**Checkpoint**: User Story 1 should be fully functional and independently testable as the Stage 3 MVP

---

## Phase 4: User Story 2 - Extract Structural Facts Across Mixed Languages (Priority: P2)

**Goal**: Run manifest-scoped tree-sitter structural extraction for supported languages and emit Surveyor-ready deterministic structural artifacts

**Independent Test**: A developer can analyze a mixed-language fixture repository and verify deterministic structural records with evidence metadata for supported files

### Tests for User Story 2

- [X] T019 [P] [US2] Add language-router coverage for supported and partial languages in `tests/unit/test_language_router.py`
- [X] T020 [P] [US2] Add mixed-language structural extraction tests in `tests/unit/test_tree_sitter_analyzer.py`
- [X] T021 [P] [US2] Add structural artifact serialization and manifest-integration tests in `tests/integration/test_structural_analysis_pipeline.py`
- [X] T022 [P] [US2] Add mixed-language fixture repository contents for Python, SQL, YAML, JavaScript, TypeScript, notebooks, and shell files in `tests/fixtures/structural_polyglot_repo/`

### Implementation for User Story 2

- [X] T023 [P] [US2] Implement tree-sitter parser initialization and analyzer scaffolding in `src/analyzers/tree_sitter_analyzer.py`
- [X] T024 [US2] Implement manifest-scoped language routing and eligible-file selection in `src/utils/language_router.py` and `src/analyzers/tree_sitter_analyzer.py`
- [X] T025 [US2] Implement typed structural record creation with evidence metadata in `src/analyzers/tree_sitter_analyzer.py` and `src/models/structural.py`
- [X] T026 [US2] Add deterministic structural artifact serialization in `src/utils/artifacts.py` and `src/models/artifacts.py`
- [X] T027 [US2] Integrate structural extraction outputs into orchestrator analyze summaries in `src/orchestrator.py`
- [X] T028 [US2] Document public structural-analysis artifact expectations in `specs/004-structural-analysis/contracts/structural-analysis-contract.md`

**Checkpoint**: User Story 2 should be independently testable with mixed-language structural extraction and deterministic artifact output

---

## Phase 5: User Story 3 - Preserve Safe Partial Results Under Brownfield Conditions (Priority: P3)

**Goal**: Keep structural analysis safe and useful when files are malformed, unsupported, partially supported, or dynamically difficult

**Independent Test**: A developer can analyze malformed and mixed-support fixture repositories and verify structured warnings, partial results, and deterministic degraded outputs without run-wide failure

### Tests for User Story 3

- [X] T029 [P] [US3] Add malformed-file and parser-failure tests in `tests/unit/test_tree_sitter_analyzer.py`
- [X] T030 [P] [US3] Add unsupported and partially supported file handling tests in `tests/integration/test_structural_analysis_pipeline.py`
- [X] T031 [P] [US3] Add malformed and degraded fixture repository contents in `tests/fixtures/structural_malformed_repo/`

### Implementation for User Story 3

- [X] T032 [P] [US3] Implement structured parse warnings, partial-result signaling, and failure capture in `src/analyzers/tree_sitter_analyzer.py`
- [X] T033 [US3] Integrate degraded-outcome tracking with analysis state in `src/models/state.py` and `src/models/structural.py`
- [X] T034 [US3] Ensure unsupported and manifest-ineligible files are excluded from deep parsing while preserving structured outcomes in `src/analyzers/tree_sitter_analyzer.py` and `src/orchestrator.py`
- [X] T035 [US3] Update analyze-path summary text for partial, malformed, and unsupported structural outcomes in `src/cli.py` and `src/orchestrator.py`

**Checkpoint**: All user stories should now be independently functional and safe for brownfield structural analysis

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup across Stage 3 repository preparation and structural analysis behavior

- [X] T036 [P] Run the full pytest suite for Stage 3 repository preparation and structural extraction coverage in `tests/unit/`, `tests/integration/`, and `tests/contract/`
- [X] T037 [P] Validate local-path and Git-URL quickstart behavior against `specs/004-structural-analysis/quickstart.md`
- [X] T038 Verify deterministic repository preparation reuse, structural artifact ordering, and output placement across `src/utils/repository_preparation.py`, `src/analyzers/tree_sitter_analyzer.py`, `src/utils/artifacts.py`, and `src/orchestrator.py`
- [X] T039 [P] Clean up docstrings, typing, and field descriptions in `src/models/repository_input.py`, `src/models/structural.py`, `src/utils/language_router.py`, `src/utils/repository_preparation.py`, and `src/analyzers/tree_sitter_analyzer.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion; recommended MVP
- **User Story 2 (Phase 4)**: Depends on Foundational completion and builds on repository-preparation and routing primitives
- **User Story 3 (Phase 5)**: Depends on Foundational completion and builds on routing, parsing, and typed structural result primitives
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: No dependency on other user stories; establishes the Stage 3 repository-preparation MVP
- **User Story 2 (P2)**: Independent in value after Foundational completion, but safest once repository preparation and manifest reuse are stable
- **User Story 3 (P3)**: Independent in value after Foundational completion, but safest once parser routing and structural result handling are stable

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Typed models and settings before service and analyzer integration
- Repository preparation before analyze-path orchestration changes
- Language routing before parser extraction
- Analyzer implementation before artifact serialization and CLI summary updates
- Story documentation after behavior stabilizes

### Parallel Opportunities

- Setup tasks `T003` and `T004` can run in parallel after `T001` and `T002`
- Foundational tasks `T006` to `T010` can run in parallel where they touch separate files
- User Story 1 test tasks `T011` to `T013` can run in parallel
- User Story 2 test and fixture tasks `T019` to `T022` can run in parallel
- User Story 3 test and fixture tasks `T029` to `T031` can run in parallel
- Polish tasks `T036`, `T037`, and `T039` can run in parallel once implementation is complete

---

## Parallel Example: User Story 1

```bash
Task: "Add repository-input model and validation tests in tests/unit/test_repository_input_models.py"
Task: "Add repository preparation and clone-reuse tests in tests/integration/test_repository_preparation.py"
Task: "Add CLI and orchestrator repository-input resolution tests in tests/contract/test_repository_input_cli_contract.py"
```

## Parallel Example: User Story 2

```bash
Task: "Add language-router coverage for supported and partial languages in tests/unit/test_language_router.py"
Task: "Add mixed-language structural extraction tests in tests/unit/test_tree_sitter_analyzer.py"
Task: "Add mixed-language fixture repository contents for Python, SQL, YAML, JavaScript, TypeScript, notebooks, and shell files in tests/fixtures/structural_polyglot_repo/"
```

## Parallel Example: User Story 3

```bash
Task: "Add malformed-file and parser-failure tests in tests/unit/test_tree_sitter_analyzer.py"
Task: "Add unsupported and partially supported file handling tests in tests/integration/test_structural_analysis_pipeline.py"
Task: "Add malformed and degraded fixture repository contents in tests/fixtures/structural_malformed_repo/"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate repository input resolution and prepared-repository reuse independently
5. Stop and review the Stage 3 MVP before adding structural extraction work

### Incremental Delivery

1. Complete Setup + Foundational to stabilize repository preparation, routing, and typed structural contracts
2. Add User Story 1 for repository input resolution and prepared-repository reuse
3. Add User Story 2 for tree-sitter structural extraction and deterministic artifacts
4. Add User Story 3 for graceful degradation and malformed or unsupported file handling
5. Finish with Phase 6 validation and cleanup

### Parallel Team Strategy

1. One contributor handles shared models, settings, and repository-preparation primitives (`T005` to `T010`)
2. One contributor handles repository input resolution and analyze-flow integration (`T014` to `T018`)
3. One contributor handles parser routing, fixtures, and structural extraction coverage (`T019` to `T035`)
4. Merge on the Phase 6 validation tasks once story phases are complete

---

## Notes

- All tasks use the required checklist format with checkbox, task ID, labels, and explicit file paths where applicable
- User Story 1 is the recommended MVP scope
- The task list intentionally excludes module graph ranking, git velocity analysis, SQL lineage extraction, graph algorithms, LangGraph workflow execution, and LLM-backed features
- Each user story remains independently testable and focused on repository preparation and structural extraction only
