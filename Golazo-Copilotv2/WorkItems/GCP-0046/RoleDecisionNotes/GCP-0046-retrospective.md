# GCP-0046: Retrospective

## What Went Well

1. **Data-driven architecture paid off** — Adding domain-expert required changes to only ONE production file (transitions.py). The TRANSITIONS dict, PHASE_MAP, and ROLE_ORDER are the single source of truth. No new tool logic was needed.

2. **TDD red-green-refactor worked cleanly** — 16 tests written first (11 failed as expected), production code made all pass, then regression fixes brought the full suite to green. The approach caught all breakages systematically.

3. **Full Golazo workflow execution** — All 10 roles were exercised for this work item. The process generated comprehensive artifacts (User Story, Design Doc, Review Comments, Test Cases, Capability Impact) before any code was written.

4. **Modularity audit (refactor-expert)** — Confirmed that the production code change (transitions.py at 96 lines, 4 functions) is well within quality thresholds.

5. **Capability registry validation** — All 12 capabilities passed validation at build time, confirming no regressions.

## What Didn't Go Well

1. **MCP server schema stale during session** — The running MCP server had a cached tool schema that didn't include "domain-expert" in the enum. This is expected (server started before changes), but meant I couldn't test the full workflow via MCP tools during development. Also discovered the running server uses "documentor" (old spelling) while source uses "documenter".

2. **Test helper `advance_to_role` has wrong role order** — The helper's hardcoded sequence has `builder` before `documenter`, but TRANSITIONS/ROLE_ORDER has `documenter` before `builder`. Transition failures are silently ignored, so tests pass by accident. This is a pre-existing issue, not introduced by GCP-0046.

3. **10 regression tests** — The domain-expert insertion between PM and QA broke 10 tests across 3 files. All required mechanical fixes (inserting domain-expert steps). This is inherent to adding a new role but could be reduced with better test helper design.

## Action Items

| # | Proposed Change | Priority | New Work Item? |
|---|----------------|----------|----------------|
| 1 | Fix `advance_to_role` role sequence order (builder/documenter swapped) and add assertion checking transition success | Medium | Yes |
| 2 | Add MCP server hot-reload or schema refresh capability for development workflows | Low | Yes |
| 3 | Consider generating test role sequences from `ROLE_ORDER` import instead of hardcoding | Medium | Yes — would prevent this class of regression |
| 4 | Resolve "documenter" vs "documentor" spelling inconsistency across the codebase | High | Yes |

## Metrics

- **Test count growth:** 236 → 252 (+16 new tests for domain-expert)
- **Production files changed:** 1 (transitions.py) — demonstrates architecture extensibility
- **Total files changed:** 26 (including all artifacts, role files, test updates)
- **Build version:** 2.104.4 → 2.104.5
- **All capabilities validated:** 12/12
