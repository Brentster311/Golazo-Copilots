# GCP-0053 Design Document: POA Closure Gate — Enforce POA Re-entry After Retrospective in Complete Mode

**Work Item:** GCP-0053  
**Author:** Program Manager  
**Status:** Draft

---

## Summary

In the current Golazo Copilot workflow, the `complete` profile's 10-role sequence ends at `retrospective`. However, the `project-owner-assistant` (POA) role already contains a `## Closure` section describing final acceptance, commit verification, and closure documentation. Today, nothing in the system *enforces* a return to POA after retrospective — the closure pathway exists in the role file text but is not programmatically required.

GCP-0053 closes this gap by making the retrospective → POA transition mandatory for `complete` profile work items, introducing a detectable "closure" state so the system (and user) can distinguish first-entry POA from closure-re-entry POA, and making the output validator context-aware so that the `{id}-closure.md` output is only gated during closure re-entry.

## Problem Statement

1. **No enforced closure step.** A `complete` profile work item can end at retrospective without formal project-owner sign-off, final commit verification, or closure documentation.
2. **No distinguishable state.** If a work item *does* return to POA after retrospective (manually), `gcp_status` cannot distinguish this from a backward rework transition — there is no "closure" indicator in state or status output.
3. **Output validator is not context-aware.** The POA role file's `## Required Outputs` section lists `{id}-closure.md` with an HTML comment "Only during Closure re-entry," but the `parse_required_outputs()` function ignores HTML comments — it either validates the file always or never.

## Business Case

- **Why now:** The POA role file already contains closure instructions (added in GCP-0047). The subagent initiative (GCP-0048–0052) completes the handoff protocol. Enforcing closure is the final piece to guarantee every `complete` work item has formal acceptance.
- **Impact:** Every `complete`-profile work item will require explicit closure, preventing silent completion and ensuring acceptance criteria are verified before a work item is considered done.
- **Scope boundary:** Express and spike profiles are unaffected — they continue to end at retrospective.

## Stakeholders

- **Project Owners** — benefit from guaranteed closure and acceptance sign-off.
- **Golazo Copilot developers** — must implement the state tracking and transition logic changes.
- **Existing work items** — must not break. Backward compatibility is required.

---

## Proposed Approach

### 1. Closure State Tracking in `WorkItemState`

**What:** Add an optional boolean field `closure_pending` (default `False`) to `WorkItemState` in `core/types.py`.

**Why:** The system needs a single, unambiguous signal to distinguish "POA initial entry" from "POA closure re-entry." The `role_history` list already shows that POA was visited before, but inspecting history is fragile and semantically unclear — `closure_pending` makes intent explicit.

**Behavior:**
- When `gcp_transition` moves from `retrospective` → `project-owner-assistant` in `complete` profile, it sets `closure_pending = True` on the state before saving.
- When `gcp_status` reads state where `current_role == "project-owner-assistant"` and `closure_pending == True`, it includes a `"closure_pending": true` flag in its response (and optionally surfaces `phase: "closure"` or similar in the status output).
- The field defaults to `False`, so existing `state.json` files without it remain valid (Pydantic's default handles this). Schema version stays at `"1.0"` since this is an additive, backward-compatible change.

**Alternatives considered for state tracking** — see Alternatives section below.

### 2. Profile-Gated Transition from Retrospective

**What:** Modify `gcp_transition` (or the `TRANSITIONS` dict / `validate_transition()` function) so that in `complete` profile, transitioning forward from `retrospective` resolves to `project-owner-assistant` and **not** to workflow termination.

**Why:** Today, `TRANSITIONS["retrospective"]` already includes `"project-owner-assistant"` as a forward target. The transition is *allowed* but not *required*. The enforcement must come from the transition tool itself: when a `complete`-profile work item is at `retrospective` and the user (or orchestrator) attempts to end the workflow, the system should instead transition to POA.

**Behavior:**
- In `complete` profile: `gcp_transition` from `retrospective` MUST go to `project-owner-assistant`. The tool sets `closure_pending = True` on the state.
- In `express` / `spike` profiles: No change. Retrospective remains the final role.
- The retrospective role markdown file should be updated to explicitly instruct: "In complete profile, transition to project-owner-assistant for closure."

**Decision: No new role.** Closure is a *state* of the existing POA role, not an 11th role. Adding a role would break `ROLE_ORDER`, `PHASE_MAP`, `VALID_ROLES`, all test assertions on role counts, the subagent handoff matrix, and the progress bar. The cost far exceeds the benefit.

### 3. Context-Aware Output Validator

**What:** Modify `parse_required_outputs()` in `core/output_validator.py` to recognize a convention for conditional outputs — specifically, outputs annotated with an HTML comment like `<!-- closure-only -->` on the same line or immediately preceding line — and filter them based on the current work item state.

**Why:** The POA role file lists `{id}-closure.md` in Required Outputs, but this file should only be required when POA is in closure re-entry mode. On initial POA entry, demanding `{id}-closure.md` would block the POA → PM transition incorrectly.

**Behavior:**
- `parse_required_outputs()` gains an optional parameter (e.g., `closure_mode: bool = False`).
- When parsing the Required Outputs section, if a line is annotated with `<!-- closure-only -->`, the resulting `OutputSpec` is tagged (e.g., `closure_only: bool = True` on `OutputSpec`).
- The caller (`gcp_transition`, `gcp_status`) passes `closure_mode=state.closure_pending` so that closure-only outputs are included only when appropriate.
- Alternatively, the filtering happens at the caller level: `gcp_transition` reads `state.closure_pending` and strips closure-only specs from the validation list when `closure_pending` is `False`.

**Design choice:** The annotation convention (`<!-- closure-only -->`) is preferred over hardcoding paths because it keeps the output validator generic and allows future roles to use similar conditional gating without code changes.

### 4. Status Output Enhancement

**What:** `gcp_status` should include `closure_pending` in its response when the flag is `True`.

**Why:** AC2 requires that status output distinguishes the closure state from normal operation. This lets the orchestrator, user, and any automation detect that the work item is in its final acceptance phase.

**Behavior:**
- When `state.closure_pending` is `True` and `state.current_role == "project-owner-assistant"`, the status response includes `"closure_pending": true`.
- The `next_steps` list should include closure-specific guidance (e.g., "Perform closure: verify acceptance criteria, final commit, create closure.md").
- Optionally, `current_phase` could be reported as `"closure"` instead of `"definition"` — but this is a display/UX decision for the architect to finalize. The phase enum in `PHASE_MAP` maps POA to `"definition"`, and changing the enum has broader implications. A simpler approach: keep `current_phase` as-is and add `closure_pending` as a separate field.

### 5. Retrospective Role File Update

**What:** Update `roles/defaults/retrospective.md` to include an explicit instruction about transitioning to POA in complete profile.

**Why:** AC1 requires the retrospective role instructions to explicitly state this. Currently, the retrospective role file says nothing about what happens after completion.

**Content to add:** A note in the role file (e.g., in a new `## Next Step` or `## Transition` section) stating: "In complete profile, transition to project-owner-assistant for closure. In express/spike profiles, the workflow ends here."

---

## Alternatives Considered

### A1: Derive closure state from `role_history` instead of adding a field

**Description:** Instead of adding `closure_pending` to `WorkItemState`, inspect `role_history` to check if POA has been visited before and retrospective has been completed.

**Pros:** No schema change; purely computational.

**Cons:** 
- Fragile: backward transitions also create repeat POA entries in history, making it impossible to distinguish "rework re-entry" from "closure re-entry" without also checking whether retrospective was the immediately preceding role.
- Complex: Every consumer (status, transition, output validator) must independently implement the same history-scanning logic.
- Semantically unclear: the intent ("this is closure") is inferred, not stated.

**Decision:** Rejected. An explicit flag is clearer, cheaper to check, and less error-prone.

### A2: Add an 11th role (e.g., `closure`)

**Description:** Create a new role called `closure` that follows `retrospective` in `ROLE_ORDER`.

**Pros:** Clean separation; no conditional logic in POA.

**Cons:**
- Breaks `ROLE_ORDER` (10 → 11 items), `PHASE_MAP`, `VALID_ROLES`, role progress calculations, subagent handoff matrix, all test assertions that check role counts or sequence.
- Adds a new role file, new role notes suffix, new entries in `_DEPLOYED_TO_SOURCE` for stale-file checking.
- The closure tasks (acceptance, commit verification, documentation) are already defined in the POA role file. A separate role would duplicate this content or require restructuring.
- Increases cognitive overhead for users who must now understand 11 roles instead of 10.

**Decision:** Rejected. The cost-to-benefit ratio is poor. Closure is a state, not a role.

### A3: Use `current_phase` = `"closure"` as the state indicator

**Description:** When POA is re-entered after retrospective, set `current_phase` to `"closure"` instead of `"definition"`.

**Pros:** Leverages an existing field; no new field needed.

**Cons:**
- `current_phase` is a `Literal["definition", "development", "completion"]` — adding `"closure"` changes the enum, which is a schema-level change affecting validation, serialization, and all consumers.
- `PHASE_MAP` derives phase from role, not from state context. Making phase context-dependent adds complexity to every code path that reads phase.
- Conflates two orthogonal concepts: where you are in the workflow (phase) and what mode the current role is in (closure vs. initial).

**Decision:** Rejected as standalone approach. The `closure_pending` flag is orthogonal to phase. However, architect may choose to *additionally* surface `"closure"` as a display label in status output.

### A4: Hardcode `{id}-closure.md` filtering in the output validator

**Description:** Instead of a generic annotation convention, special-case the closure output by path pattern in the validator code.

**Pros:** Simpler implementation; no parsing changes.

**Cons:**
- Brittle: any change to the closure output filename requires a code change.
- Not extensible: if future roles need conditional outputs, each requires its own hardcoded special case.
- Violates the existing design principle that outputs are declared in role markdown and parsed generically.

**Decision:** Rejected. The annotation convention (`<!-- closure-only -->`) is more maintainable and extensible.

---

## Risks and Mitigations

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|-----------|
| R1 | Existing `state.json` files without `closure_pending` cause load failures | Low | High | Pydantic default (`False`) handles missing field gracefully. No schema version bump needed. Validate with backward-compat test. |
| R2 | Annotation parsing (`<!-- closure-only -->`) is fragile with markdown formatting variations | Medium | Medium | Define a strict convention (exact comment text, must be on the line immediately before the output line or inline). Test with multiple formatting cases. |
| R3 | Express/spike profiles accidentally trigger closure logic | Low | Medium | Guard all closure logic with `if state.profile == "complete"` checks. Test coverage for express and spike profiles. |
| R4 | Multi-iteration loops (POA → retro → POA → retro) | Low | Low | Out of scope per user story. `closure_pending` is a one-shot flag: set once when entering closure, cleared or ignored after. The retrospective → POA transition only happens once. |
| R5 | Retrospective role file changes break existing role-content tests | Low | Low | The addition is a new section with advisory text. Existing test assertions on retrospective content should not be affected unless they assert "no other sections." |

---

## Dependencies

| Dependency | Type | Status | Notes |
|-----------|------|--------|-------|
| GCP-0047 (Role improvements — POA Closure section) | Prerequisite | Complete | POA role file already has `## Closure` section |
| GCP-0025 (Output validator) | Prerequisite | Complete | `parse_required_outputs()` and `validate_all_outputs()` exist |
| GCP-0020 (Role notes gate) | Prerequisite | Complete | `gcp_transition` already enforces role notes |
| GCP-0051 (Parallel status) | Prerequisite | Complete | `gcp_status` uses `asyncio.gather` — closure flag integration must be thread-safe (it's a simple field read, so no issue) |
| Pydantic v2 | Runtime | In use | `WorkItemState` uses Pydantic BaseModel; adding optional field with default is supported |

---

## Files Affected

| File | Change Type | Description |
|------|------------|-------------|
| `core/types.py` | Modify | Add `closure_pending: bool = False` to `WorkItemState` |
| `core/output_validator.py` | Modify | Support `closure_only` annotation; add optional filtering parameter or `OutputSpec` field |
| `core/transitions.py` | Possibly modify | May not need changes if enforcement is in `gcp_transition` tool |
| `tools/gcp_transition.py` | Modify | Set `closure_pending = True` when transitioning retro → POA in complete profile; pass closure state to output validator |
| `tools/gcp_status.py` | Modify | Include `closure_pending` in status response; update `_generate_next_steps` for closure |
| `roles/defaults/retrospective.md` | Modify | Add transition instruction for complete profile |
| `roles/defaults/project-owner-assistant.md` | Possibly modify | Ensure `<!-- closure-only -->` annotation is on the closure output line |
| `tests/` (new + existing) | Add/Modify | New test file for GCP-0053; ensure existing tests pass |

---

## Test Strategy

### New Tests (AC5)

| ID | Test Case | Maps to AC |
|----|----------|-----------|
| TC-A | `test_complete_profile_retro_to_poa_transition` — In complete profile, `gcp_transition` from retrospective MUST target POA and set `closure_pending = True` on state. | AC1 |
| TC-B | `test_status_shows_closure_pending` — After retro → POA transition in complete profile, `gcp_status` response includes `closure_pending: true`. | AC2 |
| TC-C | `test_closure_output_required_only_on_reentry` — Output validator requires `{id}-closure.md` only when `closure_pending = True`. On initial POA entry, it is NOT required. | AC3 |
| TC-D | `test_express_profile_ends_at_retrospective` — In express profile, retrospective is the final role; no forced POA re-entry. | AC4 |
| TC-E | `test_spike_profile_ends_at_retrospective` — Same as TC-D for spike profile. | AC4 |
| TC-F | `test_backward_compat_missing_closure_field` — Loading a `state.json` without `closure_pending` defaults to `False` without error. | Non-functional |
| TC-G | `test_closure_pending_false_on_initial_poa` — When a work item is created, POA initial entry has `closure_pending = False`. | AC3 |

### Existing Test Regression

All existing tests in `tests/` must continue to pass. Key files to verify:
- `test_gcp_transition.py` — transition validation
- `test_gcp_status.py` / `test_gcp_status_parallel.py` — status output shape
- `test_output_validator.py` — output parsing
- `test_gcp047_role_improvements.py` — POA closure section assertions
- `test_role_self_contained.py` — role file structure

---

## Non-Functional Requirements

- No breaking changes to `state.json` schema (additive only, no renames/removals).
- Backward compatible with existing work items (missing `closure_pending` defaults gracefully).
- No new MCP tools (uses existing `gcp_transition` and `gcp_status`).
- Version bump required after implementation.

## Out of Scope

- Changes to `express` or `spike` profiles.
- Adding new MCP tools.
- Modifying the POA role file's closure section *content* (already exists from GCP-0047).
- Multi-iteration loops (POA → retro → POA → retro...) — only one closure re-entry.
