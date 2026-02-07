# SFI-019 Retrospective

## What Went Well
- **TDD workflow was smooth**: 17 tests written first, all confirmed failing, then all turned green — no rework needed
- **Sauron reference was invaluable**: Having the production-tested payload format from `C:\Users\Brent\source\repos\Compute-Insights-Sauron\src\Tools\SFI_Agent` avoided guesswork about the S360 API payload structure
- **Payload format mismatch caught early**: QA/Architect review identified that accia-s360's `save_etas()` used `{"items": [...]}` while the real API uses `{ETADate, UserStatus, KpiId, ActionItems: [...]}` — fixed before any production bugs
- **Clean separation of concerns**: `eta_logic.py` (pure functions, easily testable) vs UI dialogs (presentation only) vs accia-s360 (API layer) kept the changes modular
- **All 176 tests green** throughout: no regressions

## What Didn't Go Well
- **Dialog centering boilerplate**: All 4 new dialogs + existing ones repeat the same 4-line centering pattern — a `BaseDialog` class would eliminate this duplication but was out of scope
- **Deferred imports proliferate**: `from sfi_reporter.eta_logic import ...` appears inside 5+ methods to avoid potential circular imports — worth investigating if the cycle can be broken with a restructure

## Action Items
| # | Proposal | Priority |
|---|----------|----------|
| 1 | Consider creating a `BaseDialog(tk.Toplevel)` class with centering + transient + grab_set boilerplate | Low — cosmetic, doesn't affect behavior |
| 2 | Investigate whether deferred imports in tk_app.py can be replaced with top-level imports | Low — works correctly as-is |
| 3 | Add integration test that hits the real S360 API in a staging environment to validate the payload format end-to-end | Medium — currently relies on matching Sauron's format |

## Metrics
- **Test count**: 176 total (147 SFIReporter + 29 accia-s360)
- **Files changed**: 21 (14 new, 7 modified)
- **Lines added**: 1,771
- **Lines removed**: 47
- **Build size**: 19.2 MB exe
