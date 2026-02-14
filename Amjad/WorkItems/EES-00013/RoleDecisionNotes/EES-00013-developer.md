# EES-00013 Developer Decision Notes

## Implementation Summary

Rewrote `src/ees/fact_extractor.py` from a single-shot JSON extraction to a multi-turn tool-calling agentic loop.

### Files Changed
- `src/ees/fact_extractor.py` — full rewrite (~310 lines)
- `tests/test_fact_extractor.py` — full rewrite (~430 lines, 31 tests)

### Key Implementation Decisions

1. **Tool handlers as static methods**: `_handle_submit_fact`, `_handle_submit_rule`, `_handle_set_root_cause`, `_handle_get_ontology`, `_handle_get_existing_rules` — all are `@staticmethod` since they don't need `self`.

2. **Central dispatch with try/except (A-3)**: `_dispatch_tool()` wraps all handler calls in try/except, returning error strings for unexpected exceptions. Only API-level errors propagate as `LLMError`.

3. **`for/else` loop pattern**: The `for turn in range(max_turns)` uses Python's `for/else` — the `else` block executes only when the loop exhausts without `break`, logging a warning about max turns reached.

4. **Token guard (A-8)**: `if response.usage:` before accessing `total_tokens`.

5. **Messages built as plain dicts**: Tool results appended as `{"role": "tool", "tool_call_id": ..., "content": ...}`. Assistant messages appended directly from the SDK response object.

6. **Removed imports**: `RuleThen` no longer imported (only `RuleOutput` used). `json.loads` used for tool args parsing.

7. **Imported `VALID_OPERATORS` and `VALID_OUTPUT_KINDS`**: Used directly from `models.py` instead of duplicating validation constants.

### Test Results
- 31 new tests covering all 27 test cases (+ extras for edge cases)
- 253 total tests passing (0 regressions)
- TDD cycle: red → green completed

### Deviations from Design
- None. Implementation matches design doc exactly.
