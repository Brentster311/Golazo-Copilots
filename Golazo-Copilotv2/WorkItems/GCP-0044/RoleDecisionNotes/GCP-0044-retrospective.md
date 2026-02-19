# GCP-0044 — Retrospective

## What Went Well
- **Root cause was clear**: The production bug trace provided by the user directly pointed to `Path.cwd()` in `resolve_work_items_dir`
- **TDD cycle was clean**: 6 red tests → 6 green after implementation, 1 always-green (valid path test)
- **Minimal code change**: Only server.py modified (resolver + schemas + handlers), no tool function signatures changed
- **No new regressions**: 136 tests pass, all failures are pre-existing from GCP-0043

## What Didn't Go Well
- **Pre-existing test failures from GCP-0043**: 75+ tests across test_gcp_status, test_gcp_consent, test_gcp_transition, and test_gcp012_backward use old-format IDs (e.g., "status-1") that no longer pass validation. This made regression checking noisy — had to manually exclude known failures.
- **Incomplete test ID cleanup in GCP-0043**: Only `test_gcp_create_workitem.py` was updated with compliant IDs. Other test files were left broken.

## Action Items
1. **New work item needed**: Update all test IDs in `test_gcp_status.py`, `test_gcp_consent.py`, `test_gcp_transition.py`, and `test_gcp012_backward.py` to comply with `[A-Za-z]{1,4}-\d{3,}` format
2. **Process improvement**: When changing a validation rule, the developer role should audit ALL test files for compliance, not just the directly related test file

## Metrics
- Tests broken by stale IDs: ~75
- After cleanup work item: should be 0 failures (all green)
