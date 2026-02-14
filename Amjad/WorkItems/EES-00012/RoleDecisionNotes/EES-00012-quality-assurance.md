# EES-00012 — Quality Assurance Decision Notes

## Design Review Summary

The design doc correctly identifies all v1 code paths that need updating. The phased approach (status callback → adapter updates → GUI updates) is sound — each phase is independently testable.

## Key Review Findings

1. **C-1/C-2 are Critical**: `rules_to_rows()` and `_show_rule_detail()` will crash on v2 rules since they access v1-only attributes. These must be fixed before any v2 rule can be displayed.

2. **`_then_display()` reuse is good**: The eval adapter already has the v2-aware helper. Promoting it to a module-level function used by both `rules_to_rows()` and `eval_result_to_display()` avoids duplication.

3. **Thread-safety concern addressed**: The `root.after(0, ...)` pattern is already used for `on_complete`/`on_error`. Using the same pattern for status updates is correct.

4. **Backward compatibility**: The `on_status=None` default ensures existing callers (tests, CLI if any) are unaffected.

## Test Strategy

- 18 test cases covering all 6 acceptance criteria.
- Focus on adapter unit tests (pure Python, no GUI needed).
- `on_status` callback tests use existing mock infrastructure from `test_fact_extractor.py`.
- Regression: full suite must pass (253+ tests).

## Capability Impact

Files affected: `fact_extractor.py`, `adapters.py`, `app.py`, test files. These touch the `fact-extraction`, `rule-display`, and `evaluation` capabilities.
