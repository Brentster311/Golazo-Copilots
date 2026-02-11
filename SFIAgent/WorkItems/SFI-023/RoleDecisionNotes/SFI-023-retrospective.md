# SFI-023 — Retrospective

## What went well
- **TDD cycle was clean**: 13 tests failed (red), all 22 passed after implementation (green), refactor preserved behavior.
- **Bug root-cause was identified early**: SLA Status int-vs-string mismatch was spotted during code reading, confirmed via test, fixed in one shot.
- **Extracted `_populate_rows`**: Refactor step caught the duplicated row-building pattern immediately.
- **All 211 tests pass with zero regressions**.
- **Build succeeded on first attempt** after code changes.

## What didn't go well
- **Session state was lost** between conversations — the Golazo state.json was stale and had to be re-read with explicit `workspace_path` to pick up the correct role.
- **Test file needed recreation** because the previous session's work was lost at the boundary.

## Action items
- None proposed — the workflow executed smoothly this session.

## Metrics
- **Time to green**: ~5 minutes (test write → implementation → all pass)
- **Test count**: +22 new tests, 211 total, 0 failures
- **Changed files**: 2 (tk_app.py, test_sfi_023.py)
- **New functions**: `_resolve_sla_display`, `_resolve_eta_status`, `_populate_rows`, `_on_detail_update_etas`, `_on_detail_eta_complete`, `_refresh_items`
