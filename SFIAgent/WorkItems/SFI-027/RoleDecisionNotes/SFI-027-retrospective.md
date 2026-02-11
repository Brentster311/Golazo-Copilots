# SFI-027 Retrospective

**Work Item**: SFI-027 — MS Graph People Hierarchy in accia-s360  
**Date**: 2025-07-20  

## What Went Well

1. **POC-driven design**: The live MS Graph POC (from SFI-026 debugging) directly informed the design. All technical assumptions were validated before any Golazo artifacts were created, resulting in zero surprises during implementation.

2. **Clean TDD cycle**: Tests written first, 31/34 passed on first implementation run. The 3 failures were test-mock issues (not production bugs) — the CEO-vs-user-not-found 404 disambiguation needed extra mock responses. Quick fix, no production code changes needed.

3. **Zero regressions**: All 29 existing accia-s360 tests passed unchanged throughout. Additive-only change pattern worked perfectly.

4. **Fast execution**: Full 9-role workflow completed in a single session. Library changes are simpler than UI changes (contrast with SFI-026's multi-day struggles).

5. **Capability impact analysis**: Identified 10 affected capabilities early. Confirmed all impact was transitive (no contract changes), which de-risked the implementation.

## What Didn't Go Well

1. **Models location decision point**: The design initially proposed `models/org.py` (new package) but the codebase uses `models.py` (single file). QA and architect both flagged it. This could have been caught earlier if the PM had reviewed the existing file structure before proposing the module layout.

2. **Test mock complexity for 404 disambiguation**: The CEO-vs-user-not-found logic creates a branching path that requires careful mock setup. 3 tests initially failed because they didn't account for the verification call. This suggests the verification approach, while correct, adds test complexity.

## Action Items

1. **Process**: When designing module layouts in the PM role, explicitly list existing files in the target directory to avoid proposing structures that conflict with current conventions.

2. **Tech Best Practice candidate**: Consider adding a "Graph API 404 disambiguation" pattern to TechBestPractices.md if more Graph endpoints are added in the future.

## Metrics
- **Tests**: 34 new + 29 existing = 63 total, all passing
- **Code**: ~260 lines production (`graph.py` + model additions), ~480 lines tests
- **Roles completed**: 9/9
- **Rework**: 3 test fixes (mock adjustments, not production bugs)
