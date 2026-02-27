**Status**: IMPLEMENTED

**User Story**
- **Title**: Implement True Role-Skipping for Express and Spike Profiles
- **As a**: Golazo Copilot user
- **I want**: The express and spike profiles to skip roles that aren't relevant to their workflow
- **So that**: Small changes (express) and analysis work (spike) don't require traversing all 10 roles, reducing overhead and matching each profile's stated intent

- **Out of scope**:
  - Adding new profiles beyond the existing three (complete, express, spike)
  - Changing the complete profile's behavior
  - Modifying role responsibilities or role markdown content
  - Changing state.json schema (profile-specific role lists are derived, not stored)

- **Assumptions**:
  - **Assumption (explicit)**: Express profile roles: `project-owner-assistant` → `quality-assurance` → `developer` → `builder` → `retrospective` (5 roles). Skips PM, domain-expert, architect, refactor-expert, documenter.
  - **Assumption (explicit)**: Spike profile roles: `project-owner-assistant` → `domain-expert` → `architect` → `developer` → `retrospective` (5 roles). Purpose is to analyze a problem and produce a backlog/prototype. Skips PM, QA, refactor-expert, documenter, builder.
  - **Assumption (explicit)**: `validate_transition()` in transitions.py will consult the active profile to determine which roles are in the sequence and which forward transitions are allowed.
  - **Assumption (explicit)**: Role notes and required outputs gates still apply for roles that are in the profile's sequence.
  - **Assumption (explicit)**: Backward transitions remain unrestricted (can go back to any earlier role in the profile's sequence).
  - **Assumption (explicit)**: The `TRANSITIONS` dict and/or `ROLE_ORDER` will be made profile-aware rather than hardcoded to a single 10-role sequence.
  - **Assumption (explicit)**: This is a library/API change — no user interface changes needed.

- **Acceptance Criteria** (bulleted, testable):
  - [ ] **AC1**: Express profile transitions enforce the 5-role sequence (POA → QA → Dev → Builder → Retro) and reject forward transitions to skipped roles.
  - [ ] **AC2**: Spike profile transitions enforce the 5-role sequence (POA → Domain-Expert → Architect → Dev → Retro) and reject forward transitions to skipped roles.
  - [ ] **AC3**: Complete profile behavior is unchanged — all 10 roles including closure loop.
  - [ ] **AC4**: `golazo_status` reports the correct role sequence for the active profile.
  - [ ] **AC5**: All existing tests pass with zero regressions; new tests cover express and spike role sequences.
  - [ ] **AC6**: Backward transitions within a profile's role sequence work correctly (e.g., express: Dev can go back to QA).

- **Non-functional requirements**:
  - No breaking changes to state.json schema
  - Profile role sequences defined declaratively (data-driven, not scattered if/else)

- **Telemetry / metrics expected**: None

- **Rollout / rollback notes**:
  - Existing work items with express/spike profiles will pick up the new behavior on next transition.
  - Work items mid-flight on a skipped role would need manual state correction (edge case — unlikely since profiles currently don't skip).
