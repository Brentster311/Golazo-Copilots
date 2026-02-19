# EES-00018 Retrospective

## What Went Well
- Clean TDD cycle: 22 tests RED → GREEN in one pass (only 1 test needed a minor impl adjustment)
- Test cases from QA were comprehensive and caught a real design ambiguity (per-rule vs per-iteration resolution)
- All three schema overhaul items (EES-00016, -00017, -00018) built cleanly on each other with no integration issues
- The Goal dataclass kept the evaluator changes minimal — only ~40 new lines in the hot path

## What Didn't Go Well
- Design doc had contradictory statements: FR-4 said "after each rule fires" but Risk Mitigation said "after current iteration completes." This was caught by TC-18-14 during GREEN phase, requiring a quick implementation adjustment. The design doc should have been internally consistent.
- The contradiction was minor (fixed in <2 minutes) but illustrates the importance of QA reviewing design doc internal consistency, not just test surface coverage.

## Action Items
1. **QA role should cross-check FR descriptions against Risk Mitigations** — add a review checklist item for internal consistency between design doc sections
2. **Consider adding a "Design Decision" section** in design docs for deliberate choices between alternatives that affect implementation (e.g., "resolution check is per-rule, escalation check is per-iteration")

## Metrics
- EES-00018 completed in one pass (no blocked states, no new user stories needed)
- 22 tests added, 344 total passing
- 4 production files changed (models.py, rule_evaluator.py + 3 test files)
