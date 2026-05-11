# FRC-002 Test Cases

## Acceptance Criteria Coverage

### AC1: Persist unusual-detection settings
- TC-AC1-001: Update unusual settings and reload.
  - Expected: persisted values returned unchanged.
  - Failure: "Expected persisted unusual settings to match latest configured values."

### AC2: Detect unusual debit transactions
- TC-AC2-001: Seed baseline merchant history, add high outlier debit, request unusual alerts.
  - Expected: outlier transaction flagged with reason/severity and transaction id.
  - Failure: "Expected unusual alert for outlier debit transaction but none was returned."

### AC3: Create savings goals persisted locally
- TC-AC3-001: Create savings goal and read goals list.
  - Expected: goal present with target amount/date/monthly contribution.
  - Failure: "Expected created savings goal to be persisted and queryable."

### AC4: Record contributions and detect drift
- TC-AC4-001: Add partial contributions behind expected pace and request drift alerts.
  - Expected: drift alert returned with expected, actual, and deficit fields.
  - Failure: "Expected goal drift alert with deficit details for behind-schedule goal."

### AC5: Deterministic actionable alert payloads
- TC-AC5-001: Query unusual and goal alerts twice without data changes.
  - Expected: payloads and ordering remain identical across reads.
  - Failure: "Expected deterministic alert payload/order across repeated reads."

## Negative and Edge Tests
- TC-N-001: Reject invalid unusual settings (negative minimum amount, non-positive sensitivity).
- TC-N-002: Reject invalid goal definitions (negative target, target date in past, non-positive monthly contribution).
- TC-N-003: No unusual alert when merchant baseline sample is below minimum sample floor.
- TC-N-004: No goal drift alert when contributions meet or exceed expected pace.

## Regression
- TC-R-001: Re-run FRC-001 baseline tests to ensure existing sync/categorization/budget behavior remains unchanged.
