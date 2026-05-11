# FRC-003 Domain Expert Notes

## Domain guidance
- Use transparent recommendation math (target %, current %, delta amount) to avoid black-box outputs.
- Recommendations should be options, not directives.
- Pros/cons should mention risk concentration vs diversification tradeoffs.
- Keep recommendation generation deterministic for trust and testability.

## Risks
- Position values can become stale without refresh process.
- Recommendation confidence can be overstated if targets are incomplete.
