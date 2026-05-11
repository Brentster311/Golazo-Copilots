# FRC-002 Domain Expert Notes

## Domain Expertise Assessment
Domain expertise required:
- Finance anomaly-detection heuristics (for unusual transaction logic).
- Personal-finance goal tracking semantics (for drift calculations).

## Guidance
- Require baseline minimum sample size before flagging unusual behavior to reduce false positives.
- Use deterministic scoring formula with persisted settings for reproducibility.
- Goal drift alerts should include expected contribution, actual contribution, and deficit to keep reasoning transparent.
- Keep all computations local and avoid external enrichment dependencies.

## Risks
- Sparse merchant history may produce unstable outlier thresholds.
- Overly strict drift thresholds may trigger alert fatigue.

## Decision
Domain guidance documented for QA and Architect; proceed to quality-assurance.
