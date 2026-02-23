**Status**: IMPLEMENTED

**User Story**
- **Title**: POA Closure Gate — Enforce POA Re-entry After Retrospective in Complete Mode
- **As a**: Project Owner using Golazo Copilot in `complete` profile
- **I want**: The workflow to programmatically require a final POA closure step after retrospective completes, so the work item cannot be considered "done" without my sign-off
- **So that**: Every work item in `complete` mode gets formal acceptance, final commit verification, and closure documentation — rather than ending silently at retrospective

- **Out of scope**:
  - Changes to `express` or `spike` profiles (they remain unaffected)
  - Adding new MCP tools (this uses existing `gcp_transition` and `gcp_status`)
  - Changing the POA role file's closure section content (already exists)
  - Multi-iteration loops (POA → retro → POA → retro...) — only one closure re-entry

- **Assumptions**:
  - **Assumption (explicit)**: The closure re-entry is a distinct state from the initial POA entry — the system needs to distinguish "first time in POA" from "closure re-entry after retro". This is needed so the output validator doesn't block the initial POA→PM transition by requiring closure artifacts that don't exist yet.
  - **Assumption (explicit)**: The retrospective role's forward transition target remains `project-owner-assistant` — no new role is added.
  - **Assumption (explicit)**: The `gcp_status` tool should indicate when a work item is awaiting closure vs. in-progress.

- **Acceptance Criteria** (bulleted, testable):
  - [ ] **AC1**: In `complete` profile, `gcp_transition` from retrospective MUST transition to `project-owner-assistant` (not end the workflow). The retrospective role instructions must explicitly state this.
  - [ ] **AC2**: `gcp_status` reports a distinct state when POA is re-entered after retrospective (e.g., `phase: closure` or a `closure_pending` flag), distinguishing it from the initial POA entry.
  - [ ] **AC3**: The POA closure output (`{id}-closure.md`) is only required when POA is in closure re-entry mode — not on the initial POA entry. The output validator must be context-aware.
  - [ ] **AC4**: In `express` and `spike` profiles, the workflow continues to end at retrospective (no forced POA re-entry).
  - [ ] **AC5**: All existing tests pass, plus new tests covering: (a) complete-mode retro→POA transition enforcement, (b) closure-only output gating, (c) express/spike profiles skip closure, (d) status output distinguishes closure state.

- **Non-functional requirements**:
  - No breaking changes to existing state.json schema (add fields, don't rename/remove)
  - Backward compatible with existing work items (missing closure fields default gracefully)

- **Telemetry / metrics expected**: None

- **Rollout / rollback notes**:
  - Existing work items with `complete` profile that are already at retrospective will not retroactively require closure — the enforcement only applies to forward transitions from retrospective.
  - Version bump required after implementation.

## Closure

### Summary of What Was Delivered
POA Closure Gate enforcing POA re-entry after retrospective in complete-profile work items. Implementation adds `closure_pending` state field, `<!-- closure-only -->` annotation support in the output validator, profile-gated transition logic, and closure-aware status reporting with CLOSURE MODE indicator.

### Acceptance Criteria Validation
- [x] **AC1**: `gcp_transition` from retro→POA sets `closure_pending=True` in complete profile. Retrospective role file contains Transition Guidance section. *(Verified by TC-01, TC-04, TC-14)*
- [x] **AC2**: `gcp_status` reports `closure_pending` in response dict. Status formatter shows `CLOSURE MODE` indicator. Next steps include closure guidance. *(Verified by TC-06, TC-07, TC-15)*
- [x] **AC3**: Output validator recognizes `<!-- closure-only -->` annotation. Closure.md only required when `closure_pending=True`. Inline HTML comments stripped from paths. *(Verified by TC-08, TC-09, TC-11, TC-12, TC-16, TC-17, TC-18)*
- [x] **AC4**: Express and spike profiles do NOT set `closure_pending`. *(Verified by TC-02, TC-03)*
- [x] **AC5**: 409 tests pass (18 new + 391 existing), zero regressions. *(Verified by TC-19)*

### Future Work Items
- **Retrospective A1**: Add `ROLE_ORDER` awareness to QA test case design (TC-13 assumed impossible backward transitions from index-0 role)
- **Retrospective A2**: Harden output validator regex (pre-existing fragility)
- **Retrospective A3**: Require lifecycle statements for new state fields in PM designs
- **Retrospective A4**: Document the `gcp_consent + force=True` bootstrap pattern

### Final Status
**IMPLEMENTED** — All acceptance criteria satisfied. Committed on branch `GCP-0053`, pushed to `origin/GCP-0053`.
