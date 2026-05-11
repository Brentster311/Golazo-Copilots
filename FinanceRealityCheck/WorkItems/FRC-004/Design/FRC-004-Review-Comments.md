# FRC-004 Review Comments

## Domain Expert Guidance
- Keep formulas transparent in output payload.
- Use advisory language and avoid filing-grade claims.
- Limit alert scope to budget and withholding thresholds.

## Quality Assurance Review
- Validate deterministic tax surface and alert payload ordering.
- Validate both threshold alerts are independently triggerable.
- Add input validation tests for tax settings and alert query inputs.
- Keep regression tests for FRC-001 through FRC-003 behavior.

## Architect Notes
- Add a dedicated tax_settings table with one-row semantics for deterministic configuration reads.
- Keep tax planning calculations advisory-only with explicit model assumptions in output fields.
- Ensure threshold alerts are separate contracts: budget_overrun and withholding_gap.
- Treat income and tax settings as sensitive local-only data.
