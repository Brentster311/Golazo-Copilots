# GCP-0071 Design Document

## Summary
Correct Golazo workflow semantics so every profile returns to `project-owner-assistant` after retrospective for formal closure. The change must align transition validation, closure-mode state handling, status messaging, and shipped workflow instructions so express and spike no longer terminate at retrospective.

## Problem Statement
The current implementation and guidance model closure as complete-profile-only behavior. That conflicts with the intended process requirement that Project Owner Assistant always performs acceptance validation and final closure. As shipped, express and spike profiles end at retrospective, which skips formal closure artifacts and leaves the workflow inconsistent across profiles.

## Business Case
- Ensures one consistent workflow contract across all profiles.
- Restores the required acceptance-validation and closure-artifact step for reduced profiles.
- Reduces operator confusion caused by contradictory instructions and profile-specific terminal behavior.

## Stakeholders
- Golazo Copilot maintainers.
- Users executing express and spike workflows.
- Project owners relying on consistent closure behavior and artifacts.

## Functional Requirements
- Permit `retrospective -> project-owner-assistant` for complete, express, and spike profiles.
- Enter closure mode whenever any profile transitions from retrospective back to `project-owner-assistant`.
- Update status/help text and role guidance so no profile is documented as ending at retrospective.
- Preserve closure-only output gating so `closure.md` is required only when POA is actually in closure mode.

## Non-Functional Requirements
- Keep the existing role sets for each profile unchanged apart from final closure re-entry semantics.
- Preserve complete-profile behavior while extending the same closure mechanism to express and spike.
- Minimize changes outside workflow semantics, instructions, and regression coverage.

## Proposed Approach

### 1. Update transition model
- Modify profile transition construction so retrospective may transition to `project-owner-assistant` for all profiles.
- Keep other forward-role sequencing unchanged.

### 2. Generalize closure-mode entry logic
- Update transition handling that sets `closure_pending` and `current_phase = "closure"` so it applies to any profile when moving from retrospective to POA.
- Verify status next-step generation and closure-only output filtering already behave correctly once closure mode is entered.

### 3. Fix shipped instructions
- Update bootstrap instructions and the retrospective/POA default role docs to state that POA always closes.
- Remove text claiming express/spike end at retrospective.

### 4. Add regression coverage
- Add focused tests covering transition validity and closure-mode behavior for express and spike.
- Update any documentation-oriented tests that encode the old profile-specific guidance.

## Alternatives Considered

### Alternative A: Update docs only
- Rejected because the runtime transition logic would remain wrong.

### Alternative B: Force closure without transitioning back to POA
- Rejected because it would contradict the existing role-based closure model and closure-only outputs.

### Alternative C: Keep complete-only closure and make it configurable later
- Rejected because the user clarified the current behavior is incorrect, not optional.

## Risks, Mitigations, Open Questions

### Risks
- Existing tests may encode the old assumption that express/spike stop at retrospective.
- Status or output gating may have hidden complete-profile assumptions beyond transition validation.
- Documentation may remain inconsistent if only one instruction source is updated.

### Mitigations
- Search for all express/spike closure statements across code, role docs, and tests.
- Run focused transition/status/role-instruction tests after the first code change.
- Prefer changes in canonical sources used by bootstrap and role context generation.

### Open Questions
- None blocking. The user clarified the desired behavior directly: POA always closes.

## Dependencies
- `golazo-copilot/src/golazo_copilot/core/transitions.py`
- `golazo-copilot/src/golazo_copilot/tools/golazo_transition.py`
- `golazo-copilot/src/golazo_copilot/bootstrap-instructions.md`
- `golazo-copilot/src/golazo_copilot/roles/defaults/project-owner-assistant.md`
- `golazo-copilot/src/golazo_copilot/roles/defaults/retrospective.md`
- related tests under `golazo-copilot/tests/`

## Migration / Rollout / Rollback Plan
- Rollout as a workflow semantics correction in the next package version.
- Validate transition/status behavior and role guidance in focused tests.
- Roll back by restoring the prior profile-specific terminal behavior only if downstream consumers explicitly depend on it.

## Observability Plan
- No external telemetry changes.
- Success is measured through status output, transition behavior, and regression tests for express/spike closure entry.

## Test Strategy Summary
- Add tests for `retrospective -> project-owner-assistant` validity in express and spike profiles.
- Add tests for closure mode activation on retrospective-to-POA transitions outside the complete profile.
- Update instruction-content tests or assertions that currently say express/spike end at retrospective.