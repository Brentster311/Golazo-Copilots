# GCP-0074 Test Cases

## Acceptance-Criteria Mapping

| ID | Scenario | Expected Result | Acceptance Criterion |
|---|---|---|---|
| TC-01 | POA closure with completed Retrospective history, `closure_pending=true`, `IMPLEMENTED` story, and closure artifacts | Finalization succeeds and computes the next ID | AC1 |
| TC-02 | Current role is Retrospective | Reject as premature with actionable precondition error; global state is unchanged | AC2 |
| TC-03 | Initial POA with `closure_pending=false` | Reject as not in closure mode | AC2 |
| TC-04 | POA with `closure_pending=true` but no completed Retrospective history | Reject forged/incomplete lifecycle | AC2 |
| TC-05 | Closure file or final POA note is missing | Reject with the missing path identified | AC2 |
| TC-06 | User Story canonical status is not `IMPLEMENTED` | Reject with status guidance | AC2 |
| TC-07 | Finalization is called twice for the same valid closure | Both calls are safe; completed list contains one entry | AC3 |
| TC-08 | Existing global state contains prior completed work | Preserve prior entries and append the current ID once | AC3 |
| TC-09 | MCP registry, role guidance, and README describe POA closure finalization | Policy assertions pass | AC4 |
| TC-10 | Invalid work-item ID or global-state load/save failure | Existing structured failures remain unchanged | Regression |

## Test Execution

- Add focused async tests to `tests/test_gcp_transition_workitem.py` before production changes.
- Run focused tests to establish the expected red state.
- Run focused tests with `pytest-cov` after implementation and require the touched module to exceed 70% coverage.
- Run the complete test suite and Ruff before closure.
