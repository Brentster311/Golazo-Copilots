# GCP-0047 Retrospective

## What went well
- **TDD cycle was clean**: 25 of 31 tests failed in red phase, all 31 passed after implementation — exactly as expected
- **3-copy sync worked smoothly**: PowerShell copy loop made syncing role files across defaults/`.github/roles/` locations trivial
- **No regressions**: Full suite went from 252→281 passed with 0 regressions
- **Clear design phase**: Having Review Comments, Test Cases, and Capability Impact before coding made the developer phase efficient — no ambiguity about what to change

## What didn't go well
- **Editable install doesn't live-link data files**: `pip install -e` copies (not symlinks) non-Python files. Had to re-run `pip install -e golazo-copilot/` mid-development to pick up markdown changes. Tests passed in isolation but failed in full suite until reinstalled.
- **Server enum "documentor" typo**: The MCP server's stale enum required creating a duplicate file with the misspelled name. This is a known issue but still friction.
- **Domain Expert role was skipped**: The stale server enum for transitions doesn't include "domain-expert", so we couldn't formally enter that role. The DE analysis was folded into QA's work.

## Action items
1. **Fix "documentor" → "documenter" spelling** in server enum — this has caused friction in multiple work items. (New work item recommended)
2. **Document the editable install data-file behavior** in TechBestPractices.md or a developer guide — this is a recurring gotcha
3. **Consider a `make sync-roles` or script** that copies from source defaults to all 3 locations, so it's not manual each time
4. **Update MCP server enum** to include "domain-expert" in transition targets

## Metrics
- Test count: 252 → 281 (+29 net, accounting for 2 removed from ROLES_WITH_REGISTRY)
- Files changed: 38 (7 role files × 3 copies + transitions.py + 2 test files + 12 artifacts)
- Zero regressions
