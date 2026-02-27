# SFI-016 — Retrospective

## What Went Well
1. **Architect review caught real bugs**: The `failed_kpis` NameError and early-return type mismatch would have crashed at runtime. The structured review process found them before deployment.
2. **Test suite provided confidence**: 139 tests across 3 packages meant we could quickly verify that bug fixes didn't break anything.
3. **Retroactive tracking worked**: Even though code was written before the work item, the Golazo workflow still added value — particularly in the architect review phase.

## What Didn't Go Well
1. **Code was written without Golazo**: The singleton fix, retry feature, and initial test fixes were all implemented before creating a work item. This bypassed DoR gates (no design doc, no test cases defined first) and could have missed the bugs that architect review caught.
2. **Two bugs shipped in the initial implementation**: `failed_kpis` was never initialized as a local variable, and the early return didn't match the new tuple type. Both would have been caught by TDD if test cases had been written first (test-first would have required testing the failure path).
3. **Retroactive workflow is lower-value**: Most role outputs (user story, design doc, QA review) were created after the fact to document what was already done, rather than guiding decisions proactively.

## Action Items
1. **Process**: When the user asks for a feature, always create a Golazo work item first — even for "quick fixes." The singleton change seemed trivial but the retry feature was substantial.
2. **TDD enforcement**: The two bugs found by architect review (`failed_kpis` NameError, tuple mismatch) would have been caught by writing a test for the failure path first. The developer role instructions already say "write test code FIRST" — this needs to be followed even when code already exists.
3. **Architect review is high-value**: For SFI-016, the architect role was the most valuable — it found 2 runtime bugs. This validates that the architect role should never be skipped.

## Metrics
- **Bugs found by architect review**: 2 (target: 0 — should be caught by TDD)
- **Tests broken by code changes**: 6 (target: 0 — should update tests first)
- **Retroactive vs proactive work items**: 1 retroactive (target: 0)
