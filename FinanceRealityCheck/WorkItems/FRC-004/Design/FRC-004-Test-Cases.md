# FRC-004 Test Cases

## AC coverage
- AC1: tax settings persist and read back correctly.
- AC2: tax planning surface returns deterministic YTD/projection/threshold fields.
- AC3: budget-overrun alert emitted when projected tax exceeds annual budget threshold.
- AC4: withholding-gap alert emitted when projected tax exceeds projected annual withholding.
- AC5: repeated reads with unchanged data are deterministic.

## Negative tests
- Reject invalid tax rate values.
- Reject non-positive budget and withholding values.
- Reject invalid dates for tax surface query.

## Regression
- Existing FRC-001/FRC-002/FRC-003 tests remain green.
