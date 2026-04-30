**Status**: IMPLEMENTED

**User Story**
- Title: Make Project Owner Assistant always perform workflow closure
- As a: Golazo Copilot maintainer
- I want: every workflow profile to return to `project-owner-assistant` for formal closure after retrospective
- So that: acceptance validation, closure artifacts, and final workflow completion are handled consistently regardless of profile
- Out of scope:
  - Redesigning the role set for complete, express, or spike beyond closure routing
  - Changing work item creation defaults or introducing new profiles
  - Altering non-closure role responsibilities unless required to keep instructions consistent with the new closure policy
- Assumptions:
  - Assumption (explicit): closure is a universal workflow invariant and the currently shipped complete-only behavior is incorrect.
  - Assumption (explicit): express and spike should retain their reduced in-flight role sets, but still re-enter `project-owner-assistant` after retrospective for final closure tasks.
  - Assumption (explicit): required outputs and status messaging must remain profile-aware while allowing closure mode for all profiles.
- Acceptance Criteria (bulleted, testable):
  - Transition validation allows `retrospective -> project-owner-assistant` for complete, express, and spike profiles.
  - Status/transition behavior enters closure mode when any profile transitions from retrospective to `project-owner-assistant`.
  - Bootstrapped workflow instructions and default role guidance no longer state that express or spike end at retrospective.
  - Automated tests cover the updated closure semantics for non-complete profiles.
- Non-functional requirements:
  - Keep existing complete-profile closure behavior intact.
  - Minimize surface-area changes to only workflow semantics, instructions, and tests required for correctness.
  - Preserve backward-safe status formatting and output gating behavior during closure mode.
- Telemetry / metrics expected:
  - No external telemetry changes are required.
  - Success is measured by profile transition coverage and consistent closure-mode reporting across profiles.
- Rollout / rollback notes:
  - Rollout: ship as a workflow semantics correction with updated instructions and regression tests.
  - Rollback: restore the prior profile-specific retrospective terminal behavior if downstream consumers depend on it.

## Closure

- Summary of what was delivered:
  - Corrected workflow behavior so `retrospective -> project-owner-assistant` enters closure mode for complete, express, and spike profiles.
  - Updated canonical bootstrap instructions, retrospective guidance, POA guidance, and README text to state that POA always closes.
  - Added regression coverage for express/spike closure mode and released the change as version `5.0.2` in package metadata and changelog.
- Acceptance criteria status:
  - PASS: Transition validation allows `retrospective -> project-owner-assistant` for complete, express, and spike profiles.
  - PASS: Status/transition behavior enters closure mode when any profile transitions from retrospective to `project-owner-assistant`.
  - PASS: Bootstrapped workflow instructions and default role guidance no longer state that express or spike end at retrospective.
  - PASS: Automated tests cover the updated closure semantics for non-complete profiles.
- Future work items:
  - Remove or replace the placeholder `example-capability` registry entry that currently fails capability validation.
  - Consider follow-up typing cleanup for existing mypy issues outside this work item's changed slice.
  - Refresh bootstrapped/deployed instruction files after release so runtime guidance matches the updated package source.
- Final status confirmation:
  - IMPLEMENTED. Code, docs, focused tests, package build validation, local git commit, global installation, and Azure Artifacts publication are complete. Git push was not performed because it was not requested.