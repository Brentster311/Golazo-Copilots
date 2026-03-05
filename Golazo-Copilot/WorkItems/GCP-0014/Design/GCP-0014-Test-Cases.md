# GCP-0014: Test Cases

## Test Coverage Matrix

| Acceptance Criterion | Test Case(s) |
|---------------------|--------------|
| `gcp_consent` requires rationale (min 10 chars) | TC-01, TC-02 |
| Error when called without rationale | TC-02 |
| Deviation includes rationale in state.json | TC-03 |
| `gcp_status` shows deviations with rationale | TC-04, TC-05 |
| Tool description states PO must provide consent | TC-06 |

---

## Test Cases

### TC-01: Consent with valid rationale succeeds
**Given**: Work item GCP-TEST exists  
**When**: `gcp_consent(work_item_id="GCP-TEST", action="skip_role", reason="PO approved bypass")`  
**Then**:
- Returns `success: True`
- Message contains "Consent recorded from Project Owner"
- Deviation stored in state.json with full rationale text

### TC-02: Consent with short/empty rationale fails
**Given**: Work item GCP-TEST exists  
**When**: `gcp_consent(work_item_id="GCP-TEST", action="skip_role", reason="ok")`  
**Then**:
- Returns `success: False`
- Error message mentions minimum 10 characters
- No deviation stored

### TC-03: Deviation rationale persisted in state.json
**Given**: Consent recorded with reason "Work item already implemented per PO review"  
**When**: Load state.json for work item  
**Then**:
- `deviations[0].reason` equals "Work item already implemented per PO review"
- Full text preserved (no truncation)

### TC-04: Status shows deviations list
**Given**: Work item with 2 recorded deviations  
**When**: `gcp_status(work_item_id="GCP-TEST")`  
**Then**:
- Response includes `deviations` array
- Each deviation has: id, action, reason, timestamp, consumed
- Deviations appear in chronological order

### TC-05: Status with no deviations shows empty list
**Given**: Work item with no deviations  
**When**: `gcp_status(work_item_id="GCP-TEST")`  
**Then**:
- Response includes `deviations: []`
- Formatted output shows "No deviations recorded" or omits section

### TC-06: Tool description emphasizes PO consent
**Given**: MCP server running  
**When**: List available tools  
**Then**:
- `gcp_consent` description contains "Project Owner" or "PO"
- Description states rationale must be provided by human, not assistant

---

## Existing Tests to Update

- `test_gcp_consent.py`: Update expected message format
- Add new test file or extend existing for deviations in status
