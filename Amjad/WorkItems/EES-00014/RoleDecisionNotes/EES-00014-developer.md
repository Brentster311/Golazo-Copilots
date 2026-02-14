# EES-00014 — Developer Notes

## Implementation Summary
- Removed `because` from: `Rule`, `submit_rule` schema, `_handle_submit_rule`, `gap_detector.py`, CLI `_confirm_rules`, GUI KB treeview, detail dialogs, adapters
- Removed `set_root_cause` from: `_TOOLS`, `_dispatch_tool`, `_handle_set_root_cause`, `_TOOL_LABELS`, system prompt, `LLMResponse`, GUI `_pending_root_cause` flow, CLI `_confirm_root_cause`
- Removed `RootCause` import from `app.py` and `main.py` (no longer needed after removing auto-save-root-cause logic)
- Updated 7 test files + 1 fixture JSON

## Test Results
- 258 tests passing (down from 268 — removed 10 tests for `because` validation and `_confirm_root_cause`)
- Zero regressions
- Commit: `d2bde3e`
