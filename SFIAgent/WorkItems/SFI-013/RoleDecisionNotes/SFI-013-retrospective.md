# Retrospective Notes - SFI-013

**Work Item:** SFI-013 - Service Summary Grouped by Owner  
**Date:** 2025-01-10  
**Final Status:** ✅ Complete (DoR ✅, DoD ✅)

---

## What Went Well

### 1. TDD Flow Worked Smoothly
- Wrote 13 new tests first (red phase)
- Implemented 3 data-layer functions to make tests pass (green phase)
- Tests caught issues early (e.g., `is_manager_view` null handling)

### 2. Clear API Contract Design
- Architect phase defined precise function signatures
- Made implementation straightforward
- Easy to test in isolation

### 3. Parallel Owner Fetching
- Used `ThreadPoolExecutor` pattern from existing KPI fetching
- Kept UI responsive during data load
- Consistent with codebase patterns

### 4. Existing Tests Validated Changes
- Running full suite after each change caught regressions
- Tests for `do_refresh()` revealed missing mock for `get_client`

---

## What Didn't Go Well

### 1. Test Mock Path Issue
- Initially patched `sfi_reporter.tk_app.get_client` but it's imported inside `do_refresh()`
- Had to patch at source: `sfi_reporter.data.get_client`
- **Lesson**: Always patch where the import lives, not where it's called

### 2. Missing `get_all_programs` Mock
- Existing tests for `do_refresh()` didn't mock this new import
- Had to update test mocks when adding new imports to production code
- **Suggestion**: Consider mock factories or fixtures for common mocks

### 3. Tkinter GUI Test Skipped
- `test_sort_by_columns_empty` fails in CI due to no display
- Need to either skip these or use headless display
- Current workaround: `-k "not test_sort_by_columns_empty"`

---

## Action Items

| # | Action | Priority | Effort |
|---|--------|----------|--------|
| 1 | Add pytest fixture for S360 client mocks | Medium | Small |
| 2 | Mark GUI-dependent tests with `@pytest.mark.gui` | Low | Small |
| 3 | Document mock patterns in test README | Low | Tiny |

---

## Metrics

- **Tests Added**: 13 new tests
- **Lines Changed**: +1,079 insertions, -5 deletions
- **Workflow Time**: Single session completion
- **Regressions**: 0 (after fixing mock issues)

---

## Process Observations

The complete workflow (complete mode) was appropriate for this feature:
- Required careful API design
- Needed QA edge case thinking
- Benefited from architect contract definition

For simpler changes, express mode would have been sufficient.
