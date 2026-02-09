# GCP-0031 Design Document: Remove DoR/DoD Checklist System

## Summary

Remove the dead DoR/DoD checklist system from state, status rendering, gate checks, and supporting modules. The output validation system (Required Outputs in role files) is the replacement (GCP-0025/0026/0027).

## Problem Statement

The DoR/DoD checklist system is a zombie:
1. `gcp_mark_dor`/`gcp_mark_dod` tools were removed (GCP-0027) — no way to mark items complete
2. `check_dor_gate` blocks transition to developer based on items that can never be marked
3. Status shows "DoR: [...] 0/4" and "DoD: [...] 0/7" — always incomplete, always confusing
4. `checklists.py` has zero consumers outside the status formatting that's being removed
5. `ChecklistItem` model, dor/dod fields in state, migration validator — all dead weight

## Business Case

### Why Now
- Every `gcp_transition` to developer requires consent + force to bypass the DoR gate — this is friction on every work item
- Status output is cluttered with permanently-incomplete DoR/DoD counts
- Dead code creates confusion during maintenance

### Impact
- Clean status output: no more zombie DoR/DoD counts
- No more forced bypasses needed for developer transition
- Smaller, cleaner codebase: ~200 lines of dead code removed

### KPIs
- Zero `check_dor_gate` calls in codebase
- Zero `dor`/`dod` fields in new state.json files
- Zero `checklists.py` imports
- Status output has no DoR/DoD lines

## Functional Requirements

### FR1: Remove ChecklistItem and dor/dod from state model
- Delete `ChecklistItem` class from `types.py`
- Remove `dor` and `dod` fields from `WorkItemState`
- Delete migration validator for legacy checklist format
- Configure model to ignore extra fields (`model_config = ConfigDict(extra="ignore")`) for backward compatibility with old state files

### FR2: Remove DoR gate from transitions
- Delete `check_dor_gate()`, `DOR_GATE_ROLE` from `transitions.py`
- Remove the DoR gate block from `gcp_transition.py` (~lines 101-120)
- Output validation gate remains as the only gate

### FR3: Remove DoR/DoD from status
- Delete checklists import from `gcp_status.py`
- Remove dor/dod computation, items view, and return dict fields
- Remove dor/dod rendering from `server.py`

### FR4: Delete checklists.py
- Entire module — zero production consumers after FR3

### FR5: Remove dor/dod from state initialization
- `state.py` `create_initial_state()` no longer passes dor/dod to constructor

### FR6: Rename skip_dor → skip_outputs
- In `gcp_consent.py` VALID_ACTIONS
- In `gcp_transition.py` output validation force check
- In `server.py` consent action enum
- Remove `skip_dod` action entirely
- Update all test references

### FR7: Clean up _generate_next_steps
- Remove `dor_complete`, `dod_complete`, `dor_missing` parameters
- Only `state` and `required_outputs` remain
- Definition phase: show output remediation (already done in GCP-0027) + "transition to next role" when outputs complete
- Development phase: role-specific instructions (keep existing)
- Completion phase: "work item in completion phase" (remove DoD references)

## Proposed Approach

### Step 1: Delete `core/checklists.py`
### Step 2: Modify `core/types.py` — remove ChecklistItem, dor/dod fields, migration validator, add `extra="ignore"`
### Step 3: Modify `core/state.py` — remove dor/dod from create_initial_state
### Step 4: Modify `core/transitions.py` — remove check_dor_gate, DOR_GATE_ROLE, ChecklistItem import
### Step 5: Modify `tools/gcp_consent.py` — rename skip_dor → skip_outputs, remove skip_dod
### Step 6: Modify `tools/gcp_transition.py` — remove DoR gate block, update imports, update skip_dor → skip_outputs
### Step 7: Modify `tools/gcp_status.py` — remove all DoR/DoD code, simplify _generate_next_steps
### Step 8: Modify `server.py` — remove DoR/DoD rendering, update descriptions
### Step 9: Update tests — delete DoR/DoD test classes, remove mark_all_dor_complete helpers, rename skip_dor → skip_outputs
### Step 10: Version bump

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Old state.json with dor/dod breaks on load | `extra="ignore"` in Pydantic model config |
| skip_dor rename breaks existing consent records | Old deviations in state files retain their original action string — this is audit data, not functional |
| Tests rely on dor state manipulation | Remove/rewrite those tests |

## Test Strategy

| Test Type | Coverage |
|-----------|----------|
| Deletion verification | grep confirms zero checklists.py, ChecklistItem, check_dor_gate |
| Backward compat | Test loading a state.json with dor/dod fields → no crash |
| Transition | Developer transition works without DoR gate (output validation only) |
| Status | No dor/dod in status output |
| Consent | skip_outputs action works, skip_dod rejected |
| Regression | All remaining tests pass |
