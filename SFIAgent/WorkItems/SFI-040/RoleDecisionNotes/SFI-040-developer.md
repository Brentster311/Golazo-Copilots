# SFI-040 Developer Notes

## TDD Execution
- Added tests first in `SFIReporter/tests/test_sfi_039_app.py`:
  - `test_score_column_precedes_cost_and_ratio_column_exists`
  - `test_score_per_min_renders_for_non_zero_cost`
  - `test_score_per_min_renders_infinity_for_zero_cost`
- Verified red phase (3 failures) before code changes.
- Implemented code in `SFIReporter/src/sfi_reporter/app.py`.
- Verified green phase (new tests pass) and full regression suite.

## Implementation Summary
- Added helper `_format_score_per_min(score, cost)` in `app.py`.
- Reordered table columns to place `score` before `cost` in:
  - Services table
  - Program Summary table
  - Action Items table
- Added new `score_per_min` column with heading `Score/Min`.
- Updated all row insertion paths (including manager/grouped branches) to populate:
  - `score`
  - `cost`
  - `score_per_min` (uses fallback cost `28,800` when incoming cost is zero)

## Validation
- Focused tests: 3 passed.
- Full app test file: 131 passed.
- Full SFIReporter suite: 955 passed, 2 warnings, 0 failures.

## Scope Compliance
- No API/data/persistence changes.
- No new dependencies.
- UI rendering-only change per user story.
