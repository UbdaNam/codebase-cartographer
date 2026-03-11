# Phase 0 Research: Brownfield Cartographer Stage 2 Repository Inventory

## Decision: Keep repository discovery single-pass and reuse the manifest builder as the Stage 2 inventory pipeline

**Rationale**: Stage 0 already established a deterministic manifest builder.
Stage 2 should strengthen that path into the canonical inventory workflow
rather than add agent-specific repo scans that would violate large-repository
performance constraints.

**Alternatives considered**:
- Separate discovery scans per future analyzer: rejected because repeated
  repository walks do not scale and create inconsistent input surfaces.
- A discovery cache without a deterministic base manifest: rejected because it
  complicates later incremental work before the core inventory contract is
  stable.

## Decision: Centralize language routing in one classification service with explicit support outcomes

**Rationale**: Mixed-language repositories require one authoritative routing
surface for language label, support status, and parse eligibility. This keeps
later analyzers from re-implementing file type logic differently.

**Alternatives considered**:
- Per-analyzer language detection: rejected because it invites drift across
  Surveyor, Hydrologist, and later stages.
- Extension-only labels with no support-status field: rejected because later
  stages need to distinguish supported, partially supported, skipped, and
  unsupported files deterministically.

## Decision: Preserve skip-first evaluation before content reads

**Rationale**: Brownfield repositories contain secrets, binaries, vendored
trees, generated assets, archives, lockfiles, and oversized files. Excluding
these before content parsing is required for safety, cost control, and
production readiness.

**Alternatives considered**:
- Read file content before final exclusion: rejected because it increases
  safety risk and unnecessary I/O.
- Silent skipping with no structured reason: rejected because later analyzers
  and operators need inspectable degradation behavior.

## Decision: Extend manifest records with analyzer-facing inventory metadata instead of inventing a second inventory artifact type

**Rationale**: Future analyzers need stable record fields such as relative path,
extension, language, support status, parse eligibility, and digest strategy.
Adding these to the shared manifest keeps inventory and downstream contracts
aligned.

**Alternatives considered**:
- Separate manifest and inventory record models: rejected because it would
  duplicate path and classification semantics.
- Minimal file lists only: rejected because later analyzers need richer routing
  and incremental-analysis metadata.

## Decision: Serialize both detailed manifest and summary outputs inside `.cartography`

**Rationale**: Later orchestrator stages need durable inventory artifacts they
can consume directly. Separate detailed and summary artifacts preserve both
machine-readable inputs and human-reviewable run output.

**Alternatives considered**:
- CLI-only console output: rejected because later stages need persisted
  inventory artifacts.
- One oversized artifact with no summary companion: rejected because operators
  need lightweight run-level visibility into inventory results.

## Decision: Treat notebooks and shell files as partially supported inventory classes in Stage 2

**Rationale**: Stage 2 needs explicit mixed-language routing even before deep
parsing exists. Marking notebooks and shell files as partially supported gives
later stages a clear path without pretending full analyzer support already
exists.

**Alternatives considered**:
- Mark notebooks and shell files as fully supported now: rejected because Stage
  2 does not implement deep parsing yet.
- Mark them as unsupported only: rejected because the roadmap explicitly calls
  for these file classes to be visible and routable.

## Decision: Keep hashing bounded and optional for inventory records

**Rationale**: Stable inventory behavior matters more than eagerly hashing every
file in very large repositories. Records should preserve digest information or a
digest strategy placeholder without forcing expensive work for every skipped or
unchanged file.

**Alternatives considered**:
- Hash every file eagerly: rejected because it adds avoidable cost in large
  repositories.
- Omit digest strategy entirely: rejected because future incremental analysis
  needs a place to attach change-detection semantics.

## Decision: Integrate Stage 2 into the existing analyze flow rather than introduce a parallel command path

**Rationale**: The CLI and orchestrator already form the entrypoint for staged
analysis. Updating `analyze` to emit repository inventory artifacts preserves a
stable user-facing workflow while moving the product closer to the interim
deliverable expectations.

**Alternatives considered**:
- Add a separate inventory-only CLI command first: rejected because the main
  analyze path is already the intended orchestration surface.
- Defer CLI/orchestrator integration to a later stage: rejected because later
  stages need persisted inventory outputs now.
