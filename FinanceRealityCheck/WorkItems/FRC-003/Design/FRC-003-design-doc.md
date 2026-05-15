# FRC-003 Design Doc

## Summary
Add local portfolio position tracking plus allocation dashboard and recommendation options with pros/cons.

## Problem Statement
Current planner supports cashflow and alerts but lacks portfolio-allocation visibility and actionable allocation guidance.

## Business Case
- Completes core planning loop by connecting spending/goal awareness with investment allocation awareness.
- Increases decision quality without introducing trade-execution risk.

## Functional Requirements
1. Position persistence
- Create/update positions with symbol, asset class, account, market value.

2. Allocation dashboard
- Aggregate positions by asset class.
- Return total invested value plus percentage allocation by asset class.

3. Recommendation options
- Accept target allocation percentages.
- Return underweight/overweight options with suggested amount and pros/cons.
- No direct trade instructions.

4. Determinism
- Repeated dashboard/recommendation reads with unchanged data must be stable.

## Non-Functional Requirements
- Local-only deterministic computation.
- Responsive for 1,000 positions.

## Approach
- Add investment_positions table.
- Add planner methods for position upsert/list, allocation summary, and recommendation options.
- Recommendation formula based on drift from target percentages and total portfolio value.

## Risks and Mitigations
- Risk: recommendation over-simplification.
  - Mitigation: include transparent pros/cons and no single mandatory action.
- Risk: stale market values.
  - Mitigation: require explicit user updates to position values.

## Test Strategy Summary
- Test position persistence and update behavior.
- Test allocation aggregation percentages.
- Test recommendation options contain drift amounts and pros/cons.
- Test deterministic outputs across repeated reads.
