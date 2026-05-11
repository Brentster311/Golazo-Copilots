# FRC-003 Test Cases

## AC Coverage
- AC1: position create/update persists fields and values.
- AC2: allocation dashboard returns total and per-class percentages.
- AC3: recommendation options generated from target allocations.
- AC4: each recommendation includes pros/cons and amount suggestion, no trade command.
- AC5: repeated reads return deterministic payload order.

## Negative tests
- Reject negative/zero market value.
- Reject invalid target allocation percentages.
- Reject empty symbol/asset class inputs.

## Regression
- FRC-001 and FRC-002 baseline tests remain green.
