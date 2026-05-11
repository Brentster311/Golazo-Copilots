# FRC-004 Design Doc

## Summary
Add tax-aware planning surfaces and threshold alerts using local transaction data and configurable tax settings.

## Problem Statement
Users need early warning when projected annual tax burden exceeds their planned budget or withholding pace.

## Functional Requirements
1. Tax settings persistence
- Save marginal tax rate, annual tax budget threshold, monthly withholding estimate.

2. Tax planning surface
- Return YTD taxable income, projected annual tax, projected annual withholding, and configured settings.

3. Threshold alerts
- Emit budget-overrun alert when projected annual tax exceeds annual budget threshold.
- Emit withholding-gap alert when projected annual tax exceeds projected annual withholding.

4. Determinism
- Repeated surface and alert reads with unchanged data must be stable.

## Non-Functional Requirements
- Deterministic local calculations.
- No dependency on external tax APIs.

## Approach
- Add single-row tax_settings table.
- Add planner methods for settings upsert/read, tax planning summary, and threshold alert generation.
- Use simple annualization model from YTD income and configured marginal rate.

## Risks and Mitigations
- Risk: simplified model diverges from real filing obligations.
  - Mitigation: use advisory language and avoid filing claims.
- Risk: sparse income history can over/under-project.
  - Mitigation: expose days elapsed and calculation basis in surface output.

## Test Strategy Summary
- Settings persistence and validation tests.
- Deterministic tax surface tests.
- Threshold alert coverage for budget and withholding gaps.
- Full regression execution for prior work items.
