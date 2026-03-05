# GCP-0059 Design Document — Save Bootstrap Spine and Copied Roles under `.github/agents`

## Summary
This change updates bootstrap output locations so generated agent artifacts are centralized under `.github/agents`. The spine output file is written to `.github/agents/golazo-copilot/orchestrator.md`, and copied role files are written under `.github/agents/golazo-copilot/roles/...`. Existing bootstrap options remain supported, including toggling role-copy behavior on and off.

## Problem Statement
- Current/legacy bootstrap output locations are not aligned with the desired agent artifact structure.
- Users need deterministic and documented output paths for both the spine file and copied roles.
- Inconsistent placement increases onboarding friction and can cause tooling/docs mismatch.

## Business Case
### Why now
- The required output structure has been explicitly standardized to `.github/agents` and must be reflected in implementation and docs now to prevent drift.

### Impact
- Improves artifact discoverability by consolidating generated files under one folder tree.
- Reduces setup confusion by making output path and filename deterministic.
- Keeps operational behavior stable by preserving existing bootstrap option semantics.

### KPIs
- `%` of bootstrap runs writing spine to `.github/agents/golazo-copilot/orchestrator.md`.
- `%` of role-copy-enabled runs writing role files under `.github/agents/golazo-copilot/roles`.
- Count of bootstrap errors categorized as path-resolution vs write/copy failures.
- No regression in successful bootstrap run rate.

## Stakeholders
- Workspace maintainers using bootstrap for initial setup.
- Developers consuming role files and spine content.
- QA/Release teams validating bootstrap outputs and docs.

## Requirements
### Functional Requirements
1. Bootstrap writes/updates the spine file at `.github/agents/golazo-copilot/orchestrator.md`.
2. Bootstrap does not write spine output to legacy locations when the new path is available.
3. When role copying is enabled, copied role files are written under `.github/agents/golazo-copilot/roles/...`.
4. Existing bootstrap options and flags continue to work, including role-copy toggle behavior.
5. Documentation/help text reflects the new output structure and exact spine filename.

### Non-Functional Requirements
1. Path handling is deterministic, idempotent, and cross-platform compatible.
2. File operations avoid partial writes and surface actionable errors.
3. Backward compatibility is preserved for bootstrap interface usage (flags/default behaviors unless story-scoped changes require otherwise).
4. Performance impact remains negligible for path resolution and output writes.

## Proposed Approach
### High-Level Plan
1. Update bootstrap path resolution constants/helpers to target `.github/agents` as the base output folder.
2. Set spine output filename to exact literal `orchestrator.md` under `.github/agents/golazo-copilot`.
3. Route role copy destination to `.github/agents/golazo-copilot/roles` when `include_roles` is enabled.
4. Keep role-copy disabled behavior unchanged (no copied roles created).
5. Update docs/help text and tests to match resolved output paths.

### File/Path Contract
- Spine output: `.github/agents/golazo-copilot/orchestrator.md`
- Roles copy output (when enabled): `.github/agents/golazo-copilot/roles/<role-files...>`
- Base folder creation: ensure `.github/agents`, `.github/agents/golazo-copilot`, and `.github/agents/golazo-copilot/roles` are created as needed.

## Alternatives Considered
1. Keep roles directly under `.github/agents/golazo-copilot` (no `roles` subfolder).
   - Rejected: does not satisfy clarified requirement for concrete structure `.github/agents/golazo-copilot/roles/...`.
2. Use `.github/roles` while only moving spine to `.github/agents`.
   - Rejected: violates requirement that roles are now under the agents hierarchy.
3. Rename spine file differently (e.g., preserving old casing/filename).
   - Rejected: requirement is explicit that spine must be `golazo-copilot.md`.

## Risks, Mitigations, Open Questions
### Risks
1. Legacy tests/docs may still reference old output locations.
2. Case/casing handling differences on case-sensitive filesystems for `.MD` extension and exact filename.
3. Existing users may expect historical locations from prior versions.

### Mitigations
1. Update tests and docs in the same change set.
2. Use exact literal path constants and assertions in automated tests.
3. Provide clear release notes/changelog guidance on output path migration.

### Open Questions
- No blocking open questions for this scope. Requirement clarification provides definitive target paths.

## Dependencies
- Bootstrap implementation path-resolution logic.
- File-system helper methods for directory creation and file copy/write.
- Existing test suites for bootstrap behavior and path assertions.
- Documentation/help text sources that describe bootstrap outputs.

## Migration / Rollout / Rollback Plan
### Migration
- No data migration required.
- New bootstrap runs produce outputs under `.github/agents`; historical files remain untouched unless users rerun bootstrap and/or manually clean up.

### Rollout
1. Ship implementation, tests, and documentation updates together.
2. Validate in fresh workspace and existing workspace scenarios.
3. Validate both `include_roles=true` and `include_roles=false` paths.

### Rollback
- Revert path-resolution changes to prior output locations and restore matching docs/tests if rollback is required.

## Observability Plan
- Emit/log resolved spine output path for every bootstrap run.
- Emit/log resolved roles output folder when role copy is enabled.
- Classify failures into path-resolution, write-failure, and copy-failure categories.
- Track success/failure rates before and after release.

## Test Strategy Summary
1. Test that bootstrap writes spine to `.github/agents/golazo-copilot/orchestrator.md`.
2. Test that bootstrap does not write spine to legacy path when new path is available.
3. Test that role files copy to `.github/agents/golazo-copilot/roles` when role copy is enabled.
4. Test that no role-copy outputs are created when role copy is disabled.
5. Test docs/help text expectations for updated output locations.
6. Regression test existing bootstrap options to ensure compatibility is preserved.
