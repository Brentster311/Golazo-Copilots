# SFI-037 Retrospective

## What Went Well
- **TDD cycle was clean**: 15 tests written first, all failed, then all passed after implementation — no test rework needed
- **Minimal code surface**: 3 small functions in data.py + stats accumulation pattern reuse in services.py + column additions in app.py
- **Graceful degradation**: API failure returns empty dict, UI shows "—" — no error dialogs for missing cost data
- **No new dependencies**: Used existing `S360Client.query_kpi_costs()` endpoint

## What Didn't Go Well
- **Context window pressure**: The conversation was summarized mid-implementation because app.py is large (~1055 lines) and reviewing it consumed significant context
- **Live test suite is slow**: Full test run takes ~90s due to live API calls in `test_sfi_026_live.py`

## Action Items
1. Consider splitting `app.py` `_update_tables()` into smaller methods per table to reduce review scope
2. Consider marking live tests with `@pytest.mark.live` and excluding by default

## Metrics
- 15 new tests, 0 regressions
- 3 files changed for production code, 1 test file, 1 README update
- Total: 923 insertions, 19 deletions
