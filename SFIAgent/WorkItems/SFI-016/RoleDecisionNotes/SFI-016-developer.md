# SFI-016 — Developer Notes

## Implementation Summary
Code was implemented prior to work item creation (retroactive tracking). Architect review caught and fixed two bugs.

## Files Changed (4 files, +178/-20 lines)
| File | Change |
|---|---|
| `SFIReporter/src/sfi_reporter/data.py` | Singleton `get_client()`, `get_detailed_action_items` → tuple return, `failed_kpis` tracking |
| `SFIReporter/src/sfi_reporter/tk_app.py` | Retry button, `_on_retry_failed()`, `_on_retry_complete()`, updated `_on_refresh_complete()` |
| `SFIReporter/tests/test_data.py` | Autouse fixture to reset `_client_instance` singleton |
| `SFIReporter/tests/test_tk_app.py` | Updated mock return values from `[]` to `([], [])` |

## Bugs Fixed During Architect Review
1. `failed_kpis` was never initialized → added `failed_kpis: list[dict] = []`
2. Early return `return []` → `return [], []` for tuple consistency
3. Type annotation and docstring updated to `tuple[list[dict], list[dict]]`

## Test Results
- `tests/` (s360_client): **39 passed**
- `SFIReporter/tests/`: **84 passed**, 1 warning
- `accia-s360/tests/`: **16 passed**
- **Total: 139 passed, 0 failed**

## TDD Note
Tests were written/updated concurrently with code (not strictly test-first) since this was retroactive tracking. All 6 previously-failing tests were fixed to match the new return signature.
