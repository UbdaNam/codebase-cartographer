---

description: "Task list for Brownfield Cartographer Stage 0 foundation"
---

# Tasks: Brownfield Cartographer Stage 0 Foundation

**Input**: Design documents from `/specs/001-bootstrap-cartographer-foundation/`
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
- Paths below assume the Stage 0 single-project structure from plan.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Bootstrap the Python project, baseline structure, and developer
tooling required by all later work

- [X] T001 Create the Stage 0 source and test directory skeleton in `src/`, `src/utils/`, `src/models/`, `src/analyzers/`, `src/agents/`, `src/graph/`, `src/llm/`, `src/index/`, `tests/unit/`, `tests/integration/`, `tests/contract/`, and `tests/fixtures/`
- [X] T002 Initialize `pyproject.toml` for Python 3.11+ with `uv`, Typer, Pydantic, and pytest project metadata
- [X] T003 [P] Add package entrypoint stubs in `src/__init__.py` and `src/constants.py`
- [X] T004 [P] Add developer bootstrap and test commands to `README.md`
- [X] T005 [P] Create deterministic project-controlled artifact directories in `.cartography/runs/`, `.cartography/cache/`, and `.cartography/logs/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core Stage 0 infrastructure that MUST be complete before any user
story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Implement typed runtime settings and override hooks in `src/config.py`
- [X] T007 [P] Define shared constants for support statuses, default ignore sets, and artifact directory names in `src/constants.py`
- [X] T008 [P] Create typed manifest, scan-policy, and run-metadata models in `src/models/manifest.py` and `src/models/run_metadata.py`
- [X] T009 Implement centralized safe-scanning and skip-reason policy in `src/utils/ignore_policy.py`
- [X] T010 [P] Implement language/support classification registry in `src/utils/file_classification.py`
- [X] T011 Implement deterministic single-pass repository manifest builder in `src/analyzers/repository_manifest.py`
- [X] T012 Implement structured logging helpers for Stage 0 runs in `src/utils/logging.py`
- [X] T013 Implement artifact initialization and run-context helpers in `src/utils/artifacts.py`
- [X] T014 Implement orchestration shell for run setup and minimal summaries in `src/orchestrator.py`
- [X] T015 Create fixture repositories for supported, unsupported, skipped, and secret-sensitive cases in `tests/fixtures/sample_repo/` and `tests/fixtures/secret_repo/`

**Checkpoint**: Foundation ready; user story implementation can now begin in
priority order or in parallel where dependencies allow

---

## Phase 3: User Story 1 - Start a Safe Foundation (Priority: P1) MVP

**Goal**: Deliver a usable Stage 0 project foundation with typed configuration,
artifact initialization, minimal CLI entrypoints, and run metadata behavior

**Independent Test**: A contributor can bootstrap the project, run the
placeholder CLI, and verify `.cartography` initialization and minimal run
summary behavior without any deep repository analysis

### Tests for User Story 1

> **NOTE**: Write these tests FIRST and ensure they FAIL before implementation

- [X] T016 [P] [US1] Add configuration validation tests in `tests/unit/test_config.py`
- [X] T017 [P] [US1] Add artifact initialization and run metadata tests in `tests/unit/test_artifacts.py`
- [X] T018 [P] [US1] Add CLI contract tests for `analyze` and `query` stubs in `tests/contract/test_cli_contract.py`
- [X] T019 [P] [US1] Add integration test for placeholder run startup in `tests/integration/test_stage0_run_summary.py`

### Implementation for User Story 1

- [X] T020 [P] [US1] Implement run-context and summary models in `src/models/run_metadata.py`
- [X] T021 [US1] Implement `.cartography` initialization and run summary writing in `src/utils/artifacts.py`
- [X] T022 [US1] Implement minimal analyze/query orchestration flow in `src/orchestrator.py`
- [X] T023 [US1] Implement Typer CLI entrypoints in `src/cli.py`
- [X] T024 [US1] Update Stage 0 quickstart commands and expected outcomes in `specs/001-bootstrap-cartographer-foundation/quickstart.md`

**Checkpoint**: User Story 1 should be fully functional and independently
testable as the Stage 0 MVP

---

## Phase 4: User Story 2 - Respect Repository Boundaries at Scale (Priority: P2)

**Goal**: Deliver centralized ignore policy, deterministic file classification,
and a safe single-pass manifest foundation for large brownfield repositories

**Independent Test**: A contributor can point the Stage 0 foundation at a
fixture repository and verify that excluded paths, secret-bearing files,
oversized files, and support-status classifications are handled deterministically

### Tests for User Story 2

- [X] T025 [P] [US2] Add ignore-rule and secret-sensitive path tests in `tests/unit/test_ignore_policy.py`
- [X] T026 [P] [US2] Add file classification and support-status tests in `tests/unit/test_file_classification.py`
- [X] T027 [P] [US2] Add deterministic manifest generation tests in `tests/unit/test_repository_manifest.py`
- [X] T028 [P] [US2] Add integration test for safe scanning over fixture repositories in `tests/integration/test_safe_scan_manifest.py`

### Implementation for User Story 2

- [X] T029 [P] [US2] Implement structured skip-reason types and policy decisions in `src/models/manifest.py`
- [X] T030 [US2] Implement centralized ignore and safe-scanning policy in `src/utils/ignore_policy.py`
- [X] T031 [US2] Implement supported-extension and support-status classification logic in `src/utils/file_classification.py`
- [X] T032 [US2] Implement deterministic single-pass repository inventory assembly in `src/analyzers/repository_manifest.py`
- [X] T033 [US2] Integrate manifest summary generation into the orchestrator flow in `src/orchestrator.py`

**Checkpoint**: User Story 2 should be independently testable with fixture
repositories and deterministic skip/classification outcomes

---

## Phase 5: User Story 3 - Extend the System Without Rebuilding It (Priority: P3)

**Goal**: Deliver future-ready architecture boundaries for agents, analyzers,
graph/index/llm seams, and stable project conventions without implementing
later-stage analysis systems

**Independent Test**: A contributor can inspect the codebase and tests and map
future Surveyor, Hydrologist, Semanticist, Archivist, and Navigator work onto
existing boundaries without restructuring the Stage 0 foundation

### Tests for User Story 3

- [X] T034 [P] [US3] Add tests for stable model serialization and status values in `tests/unit/test_models.py`
- [X] T035 [P] [US3] Add architecture-boundary smoke test for CLI-to-orchestrator wiring in `tests/integration/test_architecture_boundaries.py`

### Implementation for User Story 3

- [X] T036 [P] [US3] Add future-agent boundary stubs in `src/agents/__init__.py` and `src/agents/boundaries.py`
- [X] T037 [P] [US3] Add analyzer, graph, llm, and index boundary stubs in `src/analyzers/__init__.py`, `src/graph/__init__.py`, `src/llm/__init__.py`, and `src/index/__init__.py`
- [X] T038 [P] [US3] Add shared utility exports in `src/utils/__init__.py` and model exports in `src/models/__init__.py`
- [X] T039 [US3] Document Stage 0 extension seams and non-goals in `README.md` and `specs/001-bootstrap-cartographer-foundation/contracts/cli-contract.md`

**Checkpoint**: All user stories should now be independently functional and the
Stage 0 architecture should be ready for later phases

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup across all Stage 0 stories

- [X] T040 [P] Run the full pytest suite and fix any remaining failures from `tests/unit/`, `tests/integration/`, and `tests/contract/`
- [X] T041 [P] Validate quickstart commands and artifact initialization flow against `specs/001-bootstrap-cartographer-foundation/quickstart.md`
- [X] T042 Verify deterministic output placement, skip reason stability, and read-only repository handling across `src/` and `.cartography/`
- [X] T043 [P] Clean up docstrings, typing, and module-level documentation in `src/config.py`, `src/orchestrator.py`, `src/utils/ignore_policy.py`, and `src/analyzers/repository_manifest.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion; recommended MVP
- **User Story 2 (Phase 4)**: Depends on Foundational completion and should build on shared manifest and policy primitives
- **User Story 3 (Phase 5)**: Depends on Foundational completion and can proceed after or alongside User Story 2 once shared models stabilize
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: No dependency on other user stories; establishes the Stage 0 MVP
- **User Story 2 (P2)**: Independent in business value, but reuses foundational settings, models, and orchestration helpers
- **User Story 3 (P3)**: Independent in value, but safest after the core CLI, orchestration, and model seams are established

### Within Each User Story

- Tests MUST be written and fail before implementation
- Shared models and policy primitives before orchestration integration
- CLI and orchestration wiring after supporting models and utilities exist
- Story-specific documentation after implementation behavior is stable

### Parallel Opportunities

- Setup tasks `T003` to `T005` can run in parallel after `T001` and `T002`
- Foundational tasks `T007`, `T008`, `T010`, and `T015` can run in parallel
  once `T006` defines the settings contract
- User Story 1 test tasks `T016` to `T019` can run in parallel
- User Story 2 test tasks `T025` to `T028` can run in parallel
- User Story 3 implementation tasks `T036` to `T038` can run in parallel
- Polish tasks `T040`, `T041`, and `T043` can run in parallel once
  implementation is complete

---

## Parallel Example: User Story 1

```bash
Task: "Add configuration validation tests in tests/unit/test_config.py"
Task: "Add artifact initialization and run metadata tests in tests/unit/test_artifacts.py"
Task: "Add CLI contract tests for analyze and query stubs in tests/contract/test_cli_contract.py"
Task: "Add integration test for placeholder run startup in tests/integration/test_stage0_run_summary.py"
```

## Parallel Example: User Story 2

```bash
Task: "Add ignore-rule and secret-sensitive path tests in tests/unit/test_ignore_policy.py"
Task: "Add file classification and support-status tests in tests/unit/test_file_classification.py"
Task: "Add deterministic manifest generation tests in tests/unit/test_repository_manifest.py"
Task: "Add integration test for safe scanning over fixture repositories in tests/integration/test_safe_scan_manifest.py"
```

## Parallel Example: User Story 3

```bash
Task: "Add future-agent boundary stubs in src/agents/__init__.py and src/agents/boundaries.py"
Task: "Add analyzer, graph, llm, and index boundary stubs in src/analyzers/__init__.py, src/graph/__init__.py, src/llm/__init__.py, and src/index/__init__.py"
Task: "Add shared utility exports in src/utils/__init__.py and model exports in src/models/__init__.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate quickstart behavior and `.cartography` initialization
5. Stop and review the Stage 0 MVP before adding manifest and extension work

### Incremental Delivery

1. Complete Setup + Foundational to establish the stable Stage 0 base
2. Add User Story 1 to deliver bootstrap, CLI, and run metadata behavior
3. Add User Story 2 to deliver safe scanning and deterministic manifest behavior
4. Add User Story 3 to finalize architecture seams for later stages
5. Finish with Phase 6 validation and cleanup

### Parallel Team Strategy

1. One contributor handles project bootstrap and settings (`T001` to `T008`)
2. One contributor handles scanning policy and manifest work (`T009` to `T033`)
3. One contributor handles CLI, orchestration, and boundary documentation (`T014`, `T021` to `T024`, `T036` to `T039`)
4. Merge on the Phase 6 validation tasks once story phases are complete

---

## Notes

- All tasks use the required checklist format with checkbox, task ID, labels,
  and explicit file paths where applicable
- User Story 1 is the recommended MVP scope
- The task list intentionally excludes tree-sitter parsing, sqlglot lineage,
  graph execution, embeddings, and LLM calls
- Each user story remains independently testable and aligned to Stage 0 only
