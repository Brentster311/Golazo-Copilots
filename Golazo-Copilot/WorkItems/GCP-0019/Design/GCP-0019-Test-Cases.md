# GCP-0019: Test Cases

## Test Coverage Matrix

| Acceptance Criterion | Test Case(s) |
|---------------------|--------------|
| gcp_transition checks for outgoing role notes | TC-01, TC-02, TC-03 |
| Warning field returned when notes missing | TC-02 |
| Warning displayed but transition succeeds | TC-02 |
| gcp_status includes missing_notes list | TC-04, TC-05 |
| Correct naming convention used | TC-06 |

---

## Test Cases

### TC-01: Transition with notes present - no warning
**Given**: Work item with PM role notes file exists  
**When**: `gcp_transition(work_item_id, role="quality-assurance")`  
**Then**:
- Returns `success: True`
- No `warning` field in response (or warning is None)

### TC-02: Transition with notes missing - warning returned
**Given**: Work item without PM role notes file  
**When**: `gcp_transition(work_item_id, role="quality-assurance")`  
**Then**:
- Returns `success: True` (transition succeeds)
- Returns `warning` containing "Missing role notes"
- Warning includes role name

### TC-03: First transition (from PO) - no check needed
**Given**: New work item at project-owner-assistant  
**When**: `gcp_transition(work_item_id, role="program-manager")`  
**Then**:
- Returns `success: True`
- No warning about missing notes (PO notes not checked until leaving PO)

### TC-04: Status shows missing notes list
**Given**: Work item with history [PO, PM, QA] but only PO notes exist  
**When**: `gcp_status(work_item_id)`  
**Then**:
- Response includes `missing_notes: ["program-manager"]`
- Does not include roles with notes

### TC-05: Status with all notes present - empty list
**Given**: Work item with all role notes present  
**When**: `gcp_status(work_item_id)`  
**Then**:
- Response includes `missing_notes: []`

### TC-06: Role suffix mapping correct
**Given**: Work item at refactor-expert role  
**When**: Check for notes file  
**Then**:
- Looks for `<id>-refactor.md` (not `<id>-refactor-expert.md`)

---

## Edge Cases

### TC-07: Backward transition - existing notes
**Given**: Notes exist from previous forward pass  
**When**: Transition backward to same role  
**Then**: No warning (notes exist)

### TC-08: Custom work_items_dir
**Given**: Non-default work_items_dir  
**When**: Transition with notes check  
**Then**: Checks correct directory path

---

## Existing Tests Impact

- `test_gcp_transition.py`: May need updates if warning field affects assertions
- Add new test class `TestRoleNotesWarning`
