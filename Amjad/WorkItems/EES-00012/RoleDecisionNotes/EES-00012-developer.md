# EES-00012 — Developer Decision Notes

## Implementation Summary

TDD red→green. 15 new tests added, all 268 tests passing.

## Changes Made

### `src/ees/fact_extractor.py`
- Added `on_status: Callable[[str], None] | None = None` keyword-only parameter to `extract()`.
- Added `_emit()` helper that wraps `on_status` in try/except for error isolation.
- Emit status at 3 points in the agentic loop:
  1. `"Turn N: calling LLM..."` — before each API call
  2. `"Turn N: tool_name..."` — for each tool call dispatched
  3. `"Turn N: X facts, Y rules collected"` — after processing all tools in a turn

### `src/ees/gui/adapters.py`
- Promoted `_then_display()` to module-level function. Handles both `RuleOutput` (v2) and `RuleThen` (v1 backward compat) via `isinstance` check.
- Updated `rules_to_rows()` to use `_then_display()` for `then` and `else_` branches. Output dict now includes `"else"` key (empty string if no ELSE branch).
- Updated `eval_result_to_display()` to include `"outputs"` key: list of `{rule_id, branch, kind, description}` dicts from `result.outputs`. Backward-compat keys (`root_causes`, `ruled_out`, `gap_rules`) preserved.

### `src/ees/gui/app.py`
- Added "else" column to proposed rules treeview (5 columns now).
- Added "else" column to KB rules treeview (7 columns now).
- Updated `_on_extraction_complete()` to include `else` value when populating rules tree.
- Updated `_refresh_kb_rules()` to include `else` value.
- Updated `_on_kb_rules_double_click()` to display ELSE in detail.
- Rewrote `_show_rule_detail()` to use `_then_display()` — removed all v1-only attribute access. Shows ELSE branch when present.
- Rewrote `_format_eval_display()` to use `outputs` grouped by kind (CHANGE_STATE, RULED_OUT, GAP) with branch labels (ELSE shown when not THEN).
- Wired `on_status` callback in `_extract_facts()` via `root.after(0, self.status_var.set, msg)`.

### `tests/test_gui_adapters.py`
- Added `TestRulesToRowsV2` (6 tests): CHANGE_STATE, RULED_OUT, GAP display, ELSE branch, no-ELSE, conditions formatting.
- Added `TestEvalResultToDisplayV2` (4 tests): outputs with branch info, ELSE branch, mixed kinds, empty.

### `tests/test_fact_extractor.py`
- Added `TestOnStatusCallback` (5 tests): turn info, tool names, None default, summary counts, error isolation.

## Test Results

268 passed, 0 failed (15 new tests added to baseline of 253).
