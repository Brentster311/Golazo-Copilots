# GCP-0053 Test Cases

**Work Item:** GCP-0053 — POA Closure Gate  
**Author:** Quality Assurance  
**Date:** 2026-02-22  
**Total Test Cases:** 19  

---

## Test Case Index

| ID | Category | Test Name | Maps to AC |
|----|----------|-----------|-----------|
| TC-01 | Transition | Complete profile: retro→POA forced transition | AC1 |
| TC-02 | Transition | Express profile: retro ends workflow (no forced POA) | AC4 |
| TC-03 | Transition | Spike profile: retro ends workflow (no forced POA) | AC4 |
| TC-04 | State | closure_pending set to True on retro→POA in complete | AC1, AC2 |
| TC-05 | State | closure_pending is False on initial POA entry | AC3 |
| TC-06 | Status | gcp_status shows closure_pending when True | AC2 |
| TC-07 | Status | gcp_status does NOT show closure on initial POA entry | AC2 |
| TC-08 | Output Validator | closure.md NOT required on initial POA entry | AC3 |
| TC-09 | Output Validator | closure.md IS required on closure re-entry | AC3 |
| TC-10 | Backward Compat | Old state.json without closure_pending defaults to False | NFR |
| TC-11 | Output Validator | `<!-- closure-only -->` annotation tags OutputSpec | AC3 |
| TC-12 | Output Validator | closure-only outputs excluded when closure_mode=False | AC3 |
| TC-13 | Edge Case | Backward transition from closure POA preserves closure_pending | Edge |
| TC-14 | Role Content | Retrospective role file contains profile transition instruction | AC1 |
| TC-15 | Status | Next steps reflect closure guidance when closure_pending | AC2 |
| TC-16 | Bug Fix | Inline HTML comment NOT included in file path | AC3 |
| TC-17 | Output Validator | Multiple closure-only outputs are all tagged | AC3 |
| TC-18 | Output Validator | Non-closure outputs unaffected by closure_mode | AC3 |
| TC-19 | Regression | All existing tests pass | AC5 |

---

## Detailed Test Cases

### TC-01: Complete Profile — Retro→POA Forced Transition

**Category:** Transition  
**Maps to:** AC1  
**Priority:** Critical  

**Preconditions:**
- Work item created with `profile="complete"`
- Work item advanced to `retrospective` role with all role notes created
- Retrospective role notes file exists

**Steps:**
1. Call `gcp_transition(work_item_id="TC01", role="project-owner-assistant")` from retrospective

**Expected:**
- `result["success"]` is `True`
- `result["current_role"]` is `"project-owner-assistant"`
- State file `current_role` is `"project-owner-assistant"`
- Role instructions are loaded for POA

**Failure message:** "Complete profile MUST allow transition from retrospective to project-owner-assistant for closure"

---

### TC-02: Express Profile — Retro Ends Workflow (No Forced POA)

**Category:** Transition  
**Maps to:** AC4  
**Priority:** Critical  

**Preconditions:**
- Work item created with `profile="express"`
- Work item advanced to `retrospective` role

**Steps:**
1. Verify that retrospective role instructions for express profile do NOT mandate POA transition
2. Optionally call `gcp_transition(role="project-owner-assistant")` — should be allowed (rework) but `closure_pending` should NOT be set

**Expected:**
- Retrospective does not force POA re-entry for express profile
- If manual transition occurs, `state.closure_pending` remains `False`

**Failure message:** "Express profile must NOT have closure enforcement — retrospective is the final role"

---

### TC-03: Spike Profile — Retro Ends Workflow (No Forced POA)

**Category:** Transition  
**Maps to:** AC4  
**Priority:** Critical  

**Preconditions:**
- Work item created with `profile="spike"`
- Work item advanced to `retrospective` role

**Steps:**
1. Verify that retrospective role instructions for spike profile do NOT mandate POA transition  
2. Optionally call `gcp_transition(role="project-owner-assistant")` — should be allowed but `closure_pending` should NOT be set

**Expected:**
- Spike profile retrospective does not force POA re-entry
- If manual transition occurs, `state.closure_pending` remains `False`

**Failure message:** "Spike profile must NOT have closure enforcement — retrospective is the final role"

---

### TC-04: closure_pending Flag Set on Retro→POA in Complete Profile

**Category:** State  
**Maps to:** AC1, AC2  
**Priority:** Critical  

**Preconditions:**
- Work item created with `profile="complete"`
- Work item at `retrospective` role

**Steps:**
1. Call `gcp_transition(work_item_id="TC04", role="project-owner-assistant")`
2. Load state from disk

**Expected:**
- `state.closure_pending` is `True`
- `state.current_role` is `"project-owner-assistant"`
- The flag is persisted in `state.json`

**Failure message:** "closure_pending must be set to True when transitioning from retrospective to POA in complete profile"

---

### TC-05: closure_pending is False on Initial POA Entry

**Category:** State  
**Maps to:** AC3  
**Priority:** Critical  

**Preconditions:**
- None

**Steps:**
1. Call `gcp_create_workitem(work_item_id="TC05", profile="complete")`
2. Load state

**Expected:**
- `state.closure_pending` is `False`
- `state.current_role` is `"project-owner-assistant"`

**Failure message:** "closure_pending must default to False on work item creation (initial POA entry)"

---

### TC-06: gcp_status Shows closure_pending When True

**Category:** Status  
**Maps to:** AC2  
**Priority:** High  

**Preconditions:**
- Work item at POA with `closure_pending = True` (post-retro transition in complete profile)

**Steps:**
1. Call `gcp_status(work_item_id="TC06")`

**Expected:**
- Response includes `closure_pending: True` (or equivalent field)
- Closure state is distinguishable from normal POA in the formatted output

**Failure message:** "gcp_status must include closure_pending=True when work item is in closure mode"

---

### TC-07: gcp_status Does NOT Show Closure on Initial POA Entry

**Category:** Status  
**Maps to:** AC2  
**Priority:** High  

**Preconditions:**
- Freshly created work item at initial POA (closure_pending=False)

**Steps:**
1. Call `gcp_status(work_item_id="TC07")`

**Expected:**
- Response either omits `closure_pending` or shows `closure_pending: False`
- Status output does NOT reference closure tasks

**Failure message:** "gcp_status must NOT indicate closure mode on initial POA entry"

---

### TC-08: Output Validator — closure.md NOT Required on Initial POA Entry

**Category:** Output Validator  
**Maps to:** AC3  
**Priority:** Critical  

**Preconditions:**
- POA role file has `{id}-closure.md` as a `<!-- closure-only -->` annotated output
- Work item is at initial POA entry (`closure_pending=False`)

**Steps:**
1. Parse POA role file's Required Outputs with `closure_mode=False`
2. Attempt `gcp_transition` from POA to program-manager (normal forward path)

**Expected:**
- `{id}-closure.md` is NOT in the required outputs list when `closure_mode=False`
- Transition succeeds without creating closure.md
- Only `{id}-User-Story.md` and role notes are validated

**Failure message:** "Output validator must NOT require closure.md on initial POA entry — only on closure re-entry"

---

### TC-09: Output Validator — closure.md IS Required on Closure Re-Entry

**Category:** Output Validator  
**Maps to:** AC3  
**Priority:** Critical  

**Preconditions:**
- Work item at POA with `closure_pending=True`
- POA role file has `{id}-closure.md` with `<!-- closure-only -->` annotation

**Steps:**
1. Parse POA role file's Required Outputs with `closure_mode=True`
2. Attempt to transition (or end workflow) without creating `{id}-closure.md`

**Expected:**
- `{id}-closure.md` IS in the required outputs list when `closure_mode=True`
- Transition/completion is blocked with clear error referencing the missing closure file
- Creating the file and re-attempting succeeds

**Failure message:** "Output validator must require closure.md when POA is in closure re-entry mode"

---

### TC-10: Backward Compatibility — Old state.json Without closure_pending

**Category:** Backward Compatibility  
**Maps to:** Non-functional requirements  
**Priority:** High  

**Preconditions:**
- A `state.json` file that was created before GCP-0053 (no `closure_pending` field)

**Steps:**
1. Create a minimal `state.json` without `closure_pending`:
   ```json
   {
     "schema_version": "1.0",
     "work_item_id": "OLD-001",
     "profile": "complete",
     "current_phase": "definition",
     "current_role": "program-manager",
     "created_at": "2026-01-01T00:00:00Z",
     "updated_at": "2026-01-01T00:00:00Z",
     "role_history": [],
     "deviations": []
   }
   ```
2. Load it via `load_state("OLD-001")`

**Expected:**
- State loads without error
- `state.closure_pending` is `False`
- No crash, no validation error, no schema version mismatch

**Failure message:** "Loading state.json without closure_pending field must default to False (backward compatibility)"

---

### TC-11: `<!-- closure-only -->` Annotation Tags OutputSpec

**Category:** Output Validator  
**Maps to:** AC3  
**Priority:** High  

**Preconditions:**
- Role content with `<!-- closure-only -->` annotation preceding an output line

**Steps:**
1. Call `parse_required_outputs()` on:
   ```markdown
   ## Required Outputs
   - file: WorkItems/{id}/{id}-User-Story.md
   <!-- closure-only -->
   - file: WorkItems/{id}/{id}-closure.md
   ```

**Expected:**
- Two `OutputSpec` objects returned
- First spec (`User-Story.md`): `closure_only` is `False` (or not set)
- Second spec (`closure.md`): `closure_only` is `True`
- The path for the closure spec is `WorkItems/TC11/TC11-closure.md` — NO HTML comment text in the path

**Failure message:** "<!-- closure-only --> annotation must tag the following OutputSpec as closure_only=True"

---

### TC-12: Closure-Only Outputs Excluded When closure_mode=False

**Category:** Output Validator  
**Maps to:** AC3  
**Priority:** High  

**Preconditions:**
- Parsed output specs include one with `closure_only=True`

**Steps:**
1. Parse outputs from a role file containing closure-only annotated output
2. Filter with `closure_mode=False`

**Expected:**
- The closure-only spec is excluded from the validation list
- Only non-closure outputs are validated

**Failure message:** "Closure-only outputs must be excluded from validation when closure_mode is False"

---

### TC-13: Backward Transition from Closure POA Preserves closure_pending

**Category:** Edge Case  
**Maps to:** Edge case, design RC-1  
**Priority:** Medium  

**Preconditions:**
- Work item at POA with `closure_pending=True`

**Steps:**
1. Call `gcp_transition(role="builder")` (backward transition from closure POA)
2. Load state

**Expected:**
- Transition succeeds (backward transitions always allowed)
- `state.closure_pending` remains `True`
- `state.current_role` is `"builder"`

**Failure message:** "Backward transition from closure POA must preserve closure_pending flag"

---

### TC-14: Retrospective Role File Contains Profile Transition Instruction

**Category:** Role Content  
**Maps to:** AC1  
**Priority:** Medium  

**Preconditions:**
- Updated retrospective role file

**Steps:**
1. Read `retrospective.md` role file content
2. Search for complete profile transition instruction

**Expected:**
- File contains text indicating that in `complete` profile, the next step is to transition to `project-owner-assistant` for closure
- File mentions that in `express`/`spike` profiles, the workflow ends at retrospective

**Failure message:** "Retrospective role file must explicitly instruct transition to POA in complete profile"

---

### TC-15: Next Steps Reflect Closure Guidance When closure_pending

**Category:** Status  
**Maps to:** AC2  
**Priority:** Medium  

**Preconditions:**
- Work item at POA with `closure_pending=True`

**Steps:**
1. Call `gcp_status(work_item_id="TC15")`
2. Inspect `next_steps` in response

**Expected:**
- `next_steps` includes closure-specific guidance (e.g., references to acceptance criteria verification, closure.md creation, final commit)
- Does NOT show generic "Complete current role responsibilities" without closure context

**Failure message:** "gcp_status next_steps must include closure-specific guidance when closure_pending is True"

---

### TC-16: Inline HTML Comment NOT Included in File Path (Bug Fix)

**Category:** Bug Fix Validation  
**Maps to:** AC3  
**Priority:** High  

**Preconditions:**
- Role file with inline HTML comment on output line (if inline approach is chosen)

**Steps:**
1. Parse the following content:
   ```markdown
   ## Required Outputs
   - file: WorkItems/{id}/{id}-closure.md <!-- closure-only -->
   ```
2. Inspect the resulting `OutputSpec.path_or_pattern`

**Expected:**
- Path is `WorkItems/TC16/TC16-closure.md` — NOT `WorkItems/TC16/TC16-closure.md <!-- closure-only -->`
- HTML comment text is stripped from the path

**Note:** If the preceding-line annotation approach is chosen per review RC-3, this test validates that the existing `<!-- skip comments -->` logic correctly prevents the comment from polluting the next output line's path. Either way, this test must pass.

**Failure message:** "HTML comment text must NOT appear in OutputSpec.path_or_pattern"

---

### TC-17: Multiple Closure-Only Outputs in a Role File

**Category:** Output Validator  
**Maps to:** AC3  
**Priority:** Low  

**Preconditions:**
- Role content with multiple `<!-- closure-only -->` annotated outputs

**Steps:**
1. Parse:
   ```markdown
   ## Required Outputs
   - file: WorkItems/{id}/{id}-User-Story.md
   <!-- closure-only -->
   - file: WorkItems/{id}/{id}-closure.md
   <!-- closure-only -->
   - file: WorkItems/{id}/{id}-closure-summary.md
   ```

**Expected:**
- Three `OutputSpec` objects returned
- First: `closure_only=False`
- Second: `closure_only=True`
- Third: `closure_only=True`

**Failure message:** "Each <!-- closure-only --> annotation must independently tag its following output"

---

### TC-18: Non-Closure Outputs Unaffected by closure_mode Parameter

**Category:** Output Validator  
**Maps to:** AC3  
**Priority:** Medium  

**Preconditions:**
- Role file with both closure-only and non-closure outputs

**Steps:**
1. Parse outputs with `closure_mode=True`
2. Parse outputs with `closure_mode=False`

**Expected:**
- Non-closure outputs (e.g., `{id}-User-Story.md`, role notes) are included in BOTH cases
- Only closure-only outputs differ between the two modes

**Failure message:** "Non-closure-only outputs must always be validated regardless of closure_mode"

---

### TC-19: Regression — All Existing Tests Pass

**Category:** Regression  
**Maps to:** AC5  
**Priority:** Critical  

**Preconditions:**
- All GCP-0053 changes implemented

**Steps:**
1. Run full test suite: `pytest golazo-copilot/tests/ -v`

**Expected:**
- All existing tests pass (zero regressions)
- Key files to verify:
  - `test_gcp_transition.py` — transition validation unchanged
  - `test_gcp_status.py` / `test_gcp_status_parallel.py` — status output shape compatible
  - `test_output_validator.py` — output parsing backward compatible
  - `test_gcp047_role_improvements.py` — POA closure section assertions still hold
  - `test_role_self_contained.py` — role file structure valid

**Failure message:** "Existing tests must not regress after GCP-0053 changes"

---

## Test Implementation Notes

### Suggested Test File
`golazo-copilot/tests/test_gcp053_closure_gate.py`

### Test Infrastructure Needed
- Reuse existing `advance_to_role()` helper from `test_gcp_transition.py`
- Reuse `create_role_notes()` helper
- Need to create profile-specific work items (complete, express, spike)
- Need a fixture that creates a `state.json` without `closure_pending` for backward-compat testing
- Role file fixtures with `<!-- closure-only -->` annotations for output validator tests

### pytest Markers
- All async tests need `@pytest.mark.asyncio`
- Output validator tests are synchronous (no async needed)
- Role content tests are synchronous file reads
