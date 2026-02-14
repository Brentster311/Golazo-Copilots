# EES-00015 — Developer Notes

## Implementation Summary
- Added `facts_used_by_rules(facts, rules) -> set[int]` to `adapters.py` — pure function, returns indices of facts whose (noun, property) pair matches any rule condition item (excluding chaining nouns).
- Added `_CHAINING_NOUNS` frozenset in adapters for the exclusion check.
- In `app.py`:
  - Configured `"used"` tag with bold font on `facts_tree` at widget creation.
  - After extraction, computed `_used_fact_indices` and applied the `"used"` tag to matching rows.
  - Added "Confirm Used" button with tooltip — calls `_confirm_used_facts()` which confirms only facts in the used set.
- Created `tests/test_adapters.py` with 7 tests covering TC-01 through TC-05 plus additional edge cases.

## TDD Compliance
- Tests written first, verified they failed, then implemented to make them pass.
- 270 tests passing (263 existing + 7 new).
