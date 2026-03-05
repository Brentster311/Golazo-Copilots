# GCP-0034: Fix Workspace Markers in Bootstrap — Remove .git, Add WorkItems

**Status**: IMPLEMENTED

## User Story

- **Title**: Fix Workspace Markers in Bootstrap — Remove .git, Add WorkItems
- **As a**: Golazo Copilot user
- **I want**: `gcp_bootstrap` to recognize `WorkItems/` as a valid workspace marker and NOT recognize `.git`
- **So that**: Bootstrap deploys to my project workspace (which has WorkItems/) instead of matching a parent repo root that has `.git`

## Out of Scope
- Auto-creating WorkItems/ if it doesn't exist

## Assumptions
- **Assumption (explicit)**: `.git` is removed because it causes bootstrap to match parent directories, deploying to the wrong location
- **Assumption (explicit)**: Remaining markers: `pyproject.toml`, `package.json`, `Cargo.toml`, `.hg`, `WorkItems`

## Acceptance Criteria

1. [ ] `gcp_bootstrap` succeeds when `WorkItems/` exists in the target directory
2. [ ] `.git` is NOT a valid workspace marker
3. [ ] Remaining markers (`pyproject.toml`, `package.json`, `Cargo.toml`, `.hg`) continue to work
4. [ ] All existing tests pass (updated as needed)
5. [ ] New test verifies `WorkItems/` is recognized as a valid workspace marker

## Non-Functional Requirements
- No breaking changes to existing bootstrap behavior

## Telemetry / Metrics Expected
- None

## Rollout / Rollback Notes
- Safe to deploy — additive change to marker list
