**Status**: IMPLEMENTED

**User Story**
- Title: Save bootstrap spine file and copied roles under `.github/agents` with updated naming
- As a: Golazo Copilot workspace maintainer
- I want: bootstrap to save the spine file in the workspace `.github/agents/golazo-copilot` folder as `orchestrator.md`, and place copied role files under `.github/agents/golazo-copilot/roles`
- So that: all generated agent artifacts are centralized under one agents location with the requested naming and structure
- Out of scope:
  - Changing role file content or role semantics
  - Altering non-bootstrap tooling behavior unrelated to file placement/naming
  - Backfilling historical work items or previously bootstrapped folders unless explicitly rerun
- Assumptions:
  - Assumption (explicit): Interface type is MCP tool-based bootstrap execution (no separate GUI/CLI UX change requested), because the request targets bootstrap artifact locations and names.
  - Assumption (explicit): Target platform remains cross-platform path handling while being validated on Windows, because the active workspace is Windows and no platform limitation was requested.
  - Assumption (explicit): Data persistence remains file-system based in the workspace root, because the request specifies concrete output folders/files.
  - Requirement (explicit): Spine file must be written to `.github/agents/golazo-copilot/orchestrator.md`.
  - Requirement (explicit): Copied role files must be written to `.github/agents/golazo-copilot/roles/...` and not to any generic or variable subfolder under `.github/agents`.
- Acceptance Criteria (bulleted, testable):
  - Running bootstrap in a workspace creates/updates the spine artifact at `.github/agents/golazo-copilot/orchestrator.md`.
  - Bootstrap no longer writes the spine file to legacy locations when the new path is available.
  - When role copying is enabled, copied role files are written under `.github/agents/golazo-copilot/roles/...`.
  - Existing bootstrap options continue to work, and role copying can still be toggled on/off without errors.
  - Documentation/help text for bootstrap output locations reflects the new spine filename and role-copy folder structure.
- Non-functional requirements:
  - Preserve backward compatibility for existing bootstrap flags and defaults unless directly required by this story.
  - Path creation must be deterministic and idempotent across repeated bootstrap runs.
  - File operations must avoid partial writes and return actionable errors on permission/path failures.
- Telemetry / metrics expected:
  - Bootstrap run emits/logs resolved spine output path.
  - Bootstrap run emits/logs copied roles output folder when role-copy is enabled.
  - Error telemetry distinguishes path-resolution errors from write/copy failures.
- Rollout / rollback notes:
  - Rollout: ship path/name change with docs update in the same release.
  - Rollback: revert to prior bootstrap output-path logic and restore previous documented locations.

## Closure

- Summary of what was delivered:
  - Bootstrap contract finalized and implemented to write orchestrator instructions to `.github/agents/golazo-copilot/orchestrator.md`.
  - Role copy destination finalized and implemented as `.github/agents/golazo-copilot/roles/...`.
  - Workspace and bootstrap templates were aligned to enforce Retrospective inline execution policy.
  - Validation completed with targeted and full test runs plus package build success.

- Acceptance criteria pass/fail status:
  - AC1 (`.github/agents/golazo-copilot/orchestrator.md` created/updated): **PASS**
  - AC2 (no legacy spine destination for new bootstrap flow): **PASS**
  - AC3 (copied roles written under `.github/agents/golazo-copilot/roles/...`): **PASS**
  - AC4 (bootstrap options remain functional and role-copy toggle works): **PASS**
  - AC5 (docs/help text and instruction references reflect new structure): **PASS**

- List of future work items (if any):
  - Add a dedicated automated regression test that fails if `.github/copilot-instructions.md` is absent after bootstrap.
  - Add explicit policy test to enforce “Retrospective always inline” in orchestration behavior.

- Final status confirmation:
  - Work item `GCP-0059` is complete from requirements through build verification and retrospective.
