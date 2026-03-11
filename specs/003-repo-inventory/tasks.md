---

description: "Task list for Brownfield Cartographer Stage 2 repository inventory"
---

# Tasks: Brownfield Cartographer Stage 2 Repository Inventory

**Input**: Design documents from `/specs/003-repo-inventory/`
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
- Paths below assume the Stage 2 single-project layout from plan.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the Stage 2 inventory file layout, docs, and test inputs

- [ ] T001 Create the Stage 2 fixture repository directory `tests/fixtures/inventory_polyglot_repo/`
- [ ] T002 Confirm `pyproject.toml` keeps the Stage 2 Python 3.11+, Pydantic v2, pydantic-settings, Typer, and pytest baseline
- [ ] T003 [P] Update Stage 2 inventory overview text in `README.md`
- [ ] T004 [P] Add Stage 2 fixture notes and expected inventory behavior in `specs/003-repo-inventory/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core discovery, routing, and typed inventory foundations that all user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Extend the typed inventory and summary models for Stage 2 fields in `src/models/manifest.py`
- [ ] T006 [P] Add any Stage 2 config defaults for language routing and bounded inventory behavior in `src/config.py` and `src/constants.py`
- [ ] T007 [P] Refine centralized skip-reason enforcement for Stage 2 inventory decisions in `src/utils/ignore_policy.py`
- [ ] T008 [P] Implement normalized file identity and deterministic inventory helper utilities in `src/utils/ids.py`
- [ ] T009 Implement centralized mixed-language routing and parse-eligibility classification in `src/utils/file_classification.py`
- [ ] T010 [P] Add foundational unit coverage for Stage 2 manifest fields, routing enums, and inventory helpers in `tests/unit/test_repository_manifest.py`, `tests/unit/test_file_classification.py`, and `tests/unit/test_ids.py`

**Checkpoint**: Foundational inventory primitives are ready for story-specific discovery and integration work

---

## Phase 3: User Story 1 - Produce A Deterministic Repo Inventory (Priority: P1) MVP

**Goal**: Deliver the single-pass repository inventory pipeline and deterministic manifest output used by later analyzers

**Independent Test**: A developer can run repository inventory twice against the same unchanged fixture repository and verify stable manifest ordering and identical summary totals

### Tests for User Story 1

> **NOTE**: Write these tests FIRST and ensure they FAIL before implementation

- [ ] T011 [P] [US1] Add deterministic manifest and single-pass discovery tests in `tests/unit/test_repository_manifest.py`
- [ ] T012 [P] [US1] Add inventory artifact serialization and summary stability tests in `tests/integration/test_safe_scan_manifest.py`
- [ ] T013 [P] [US1] Add Stage 2 analyze-flow summary tests in `tests/integration/test_stage0_run_summary.py`

### Implementation for User Story 1

- [ ] T014 [P] [US1] Implement the Stage 2 repository walker and deterministic record assembly in `src/analyzers/repository_manifest.py`
- [ ] T015 [US1] Implement inventory summary generation and parse-eligible counts in `src/analyzers/repository_manifest.py`
- [ ] T016 [US1] Add deterministic manifest and summary serialization helpers in `src/utils/artifacts.py`
- [ ] T017 [US1] Integrate Stage 2 inventory artifact generation into `src/orchestrator.py`
- [ ] T018 [US1] Update the analyze output contract to surface Stage 2 inventory summary details in `src/models/state.py` and `src/models/run_metadata.py`

**Checkpoint**: User Story 1 should be fully functional and independently testable as the Stage 2 MVP

---

## Phase 4: User Story 2 - Classify Mixed-Language Files Consistently (Priority: P2)

**Goal**: Deliver centralized mixed-language routing with stable support-status and parse-eligibility outcomes

**Independent Test**: A developer can inventory a mixed-language fixture repository and verify correct language labels, support statuses, and parse eligibility for the required file classes

### Tests for User Story 2

- [ ] T019 [P] [US2] Add mixed-language detection and support-status tests in `tests/unit/test_file_classification.py`
- [ ] T020 [P] [US2] Add polyglot fixture inventory regression tests in `tests/unit/test_repository_manifest.py`
- [ ] T021 [P] [US2] Add Stage 2 fixture repository contents for Python, SQL, YAML, JavaScript, TypeScript, JSON, notebooks, and shell files in `tests/fixtures/inventory_polyglot_repo/`

### Implementation for User Story 2

- [ ] T022 [P] [US2] Expand extension and path-based routing rules for all required Stage 2 file classes in `src/constants.py` and `src/config.py`
- [ ] T023 [US2] Implement normalized language labels, support-status mapping, and parse-eligibility signaling in `src/utils/file_classification.py`
- [ ] T024 [US2] Extend manifest record creation to persist Stage 2 classification fields in `src/analyzers/repository_manifest.py` and `src/models/manifest.py`
- [ ] T025 [US2] Document public inventory routing expectations in `specs/003-repo-inventory/contracts/inventory-contract.md`

**Checkpoint**: User Story 2 should be independently testable with mixed-language routing and stable classification outputs

---

## Phase 5: User Story 3 - Enforce Safe Inventory Boundaries At Scale (Priority: P3)

**Goal**: Deliver skip-first safety enforcement and structured exclusion outcomes suitable for large brownfield repositories

**Independent Test**: A developer can inventory fixture repositories containing excluded, oversized, secret-bearing, unsupported, and irrelevant files and verify deterministic skip outcomes without parse-eligible leakage

### Tests for User Story 3

- [ ] T026 [P] [US3] Add secret-bearing, skipped-directory, and oversized-file tests in `tests/unit/test_ignore_policy.py`
- [ ] T027 [P] [US3] Add unsupported-file and skip-reason coverage tests in `tests/unit/test_repository_manifest.py`
- [ ] T028 [P] [US3] Add integration coverage for non-destructive inventory outputs and excluded-file handling in `tests/integration/test_safe_scan_manifest.py`

### Implementation for User Story 3

- [ ] T029 [P] [US3] Extend skip logic for lockfiles, minified assets, archives, binaries, and irrelevant file classes in `src/utils/ignore_policy.py`
- [ ] T030 [US3] Integrate structured skip reasons and parse-eligibility enforcement into manifest assembly in `src/analyzers/repository_manifest.py`
- [ ] T031 [US3] Add bounded inventory metadata behavior for large-repository conditions in `src/analyzers/repository_manifest.py` and `src/models/manifest.py`
- [ ] T032 [US3] Update analyze-path user-facing summary text for skipped and unsupported outcomes in `src/cli.py` and `src/orchestrator.py`

**Checkpoint**: All user stories should now be independently functional and the Stage 2 inventory subsystem should be ready for later analyzers

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup across all Stage 2 inventory behavior

- [ ] T033 [P] Run the full pytest suite for Stage 2 inventory coverage in `tests/unit/` and `tests/integration/`
- [ ] T034 [P] Validate quickstart inventory behavior and analyze output against `specs/003-repo-inventory/quickstart.md`
- [ ] T035 Verify deterministic manifest ordering, summary serialization, and artifact placement across `src/analyzers/repository_manifest.py`, `src/utils/artifacts.py`, and `src/orchestrator.py`
- [ ] T036 [P] Clean up docstrings, typing, and field descriptions in `src/models/manifest.py`, `src/utils/file_classification.py`, `src/utils/ignore_policy.py`, and `src/analyzers/repository_manifest.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion; recommended MVP
- **User Story 2 (Phase 4)**: Depends on Foundational completion and builds on shared routing and manifest primitives
- **User Story 3 (Phase 5)**: Depends on Foundational completion and builds on shared skip-policy and manifest primitives
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: No dependency on other user stories; establishes the Stage 2 inventory MVP
- **User Story 2 (P2)**: Independent in value, but safest after foundational routing and manifest record work are stable
- **User Story 3 (P3)**: Independent in value, but safest after foundational skip-policy and inventory assembly are stable

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Typed models and config updates before manifest assembly changes
- Routing and skip-policy logic before orchestrator or CLI integration
- Core implementation before integration and documentation updates
- Story documentation after behavior stabilizes

### Parallel Opportunities

- Setup tasks `T003` and `T004` can run in parallel after `T001` and `T002`
- Foundational tasks `T006` to `T010` can run in parallel where they touch separate files
- User Story 1 test tasks `T011` to `T013` can run in parallel
- User Story 2 test and fixture tasks `T019` to `T021` can run in parallel
- User Story 3 test tasks `T026` to `T028` can run in parallel
- Polish tasks `T033`, `T034`, and `T036` can run in parallel once implementation is complete

---

## Parallel Example: User Story 1

```bash
Task: "Add deterministic manifest and single-pass discovery tests in tests/unit/test_repository_manifest.py"
Task: "Add inventory artifact serialization and summary stability tests in tests/integration/test_safe_scan_manifest.py"
Task: "Add Stage 2 analyze-flow summary tests in tests/integration/test_stage0_run_summary.py"
```

## Parallel Example: User Story 2

```bash
Task: "Add mixed-language detection and support-status tests in tests/unit/test_file_classification.py"
Task: "Add polyglot fixture inventory regression tests in tests/unit/test_repository_manifest.py"
Task: "Add Stage 2 fixture repository contents for Python, SQL, YAML, JavaScript, TypeScript, JSON, notebooks, and shell files in tests/fixtures/inventory_polyglot_repo/"
```

## Parallel Example: User Story 3

```bash
Task: "Add secret-bearing, skipped-directory, and oversized-file tests in tests/unit/test_ignore_policy.py"
Task: "Add unsupported-file and skip-reason coverage tests in tests/unit/test_repository_manifest.py"
Task: "Add integration coverage for non-destructive inventory outputs and excluded-file handling in tests/integration/test_safe_scan_manifest.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate deterministic manifest generation and analyze-path inventory output
5. Stop and review the Stage 2 MVP before adding mixed-language routing expansion and deeper skip behavior

### Incremental Delivery

1. Complete Setup + Foundational to stabilize inventory records, routing, and skip decisions
2. Add User Story 1 for the deterministic repository inventory MVP
3. Add User Story 2 for explicit mixed-language routing and support-status coverage
4. Add User Story 3 for safe exclusion and large-repository boundary enforcement
5. Finish with Phase 6 validation and cleanup

### Parallel Team Strategy

1. One contributor handles shared models, config, and routing primitives (`T005` to `T010`)
2. One contributor handles manifest assembly, serialization, and orchestrator integration (`T014` to `T018`)
3. One contributor handles fixture repos, routing tests, and skip-policy coverage (`T019` to `T032`)
4. Merge on the Phase 6 validation tasks once story phases are complete

---

## Notes

- All tasks use the required checklist format with checkbox, task ID, labels, and explicit file paths where applicable
- User Story 1 is the recommended MVP scope
- The task list intentionally excludes AST parsing, lineage extraction, graph logic, LangGraph workflow execution, and agent implementation
- Each user story remains independently testable and focused on discovery and classification behavior only
