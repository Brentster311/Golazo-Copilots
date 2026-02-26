# SFI-038 — Quality Assurance Decision Notes

## Decisions
- Test cases map 1:1 to acceptance criteria.
- Added edge cases for: missing CSV, score=0 KPIs, name normalization.
- Recommended dual-key lookup (name + KPIID) for resilience.
- No capability registry impact — this is an additive UI column.
