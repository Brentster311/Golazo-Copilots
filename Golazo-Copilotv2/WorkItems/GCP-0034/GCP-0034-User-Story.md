# GCP-0034: Add WorkItems/ as Valid Workspace Marker in Bootstrap

**Status**: BACKLOG

## User Story

- **Title**: Add WorkItems/ as Valid Workspace Marker in Bootstrap
- **As a**: Golazo Copilot user
- **I want**: `gcp_bootstrap` to recognize a `WorkItems/` directory as a valid workspace marker
- **So that**: Bootstrap deploys to my project workspace (which has WorkItems/) instead of falling back to the repo root

## Out of Scope
- Changing any other workspace detection logic beyond adding the new marker
- Auto-creating WorkItems/ if it doesn't exist

## Assumptions
- **Assumption (explicit)**: The existing markers (`.git`, `pyproject.toml`, `package.json`, `Cargo.toml`, `.hg`) remain valid — this adds `WorkItems/` to the list
- **Assumption (explicit)**: `WorkItems/` is a directory marker, checked via directory existence (not file)

## Acceptance Criteria

1. [ ] `gcp_bootstrap` succeeds when `WorkItems/` exists in the target directory, even if no other markers are present
2. [ ] Existing markers (`.git`, `pyproject.toml`, etc.) continue to work
3. [ ] Bootstrap deploys `.github/` files to the directory containing `WorkItems/`, not to a parent
4. [ ] All existing tests pass
5. [ ] New test verifies `WorkItems/` is recognized as a valid workspace marker

## Non-Functional Requirements
- No breaking changes to existing bootstrap behavior

## Telemetry / Metrics Expected
- None

## Rollout / Rollback Notes
- Safe to deploy — additive change to marker list
