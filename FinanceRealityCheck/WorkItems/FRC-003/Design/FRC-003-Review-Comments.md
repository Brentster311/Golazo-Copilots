# FRC-003 Review Comments

## Domain Expert Guidance
- Emit recommendation options with explicit drift math and no execution commands.
- Include portfolio concentration and diversification tradeoffs in pros/cons text.
- Keep recommendation ordering deterministic.

## Quality Assurance Review
- Require deterministic ordering for positions, allocation breakdown, and recommendation lists.
- Validate recommendation payload includes both pros and cons for each option.
- Validate no recommendation text implies direct trade execution.
- Add negative tests for invalid target allocations and invalid position market values.

## Architect Notes
- Keep position persistence, allocation aggregation, and recommendation generation as separate logical methods.
- Recommendation output contract must be explicit and action-oriented without execution semantics.
- Use stable sort keys to preserve deterministic response ordering.
- Security: treat position valuations as private financial data and keep persistence local-only.
- Capability impact currently maps to existing finance planner capability; update contracts during builder role.
