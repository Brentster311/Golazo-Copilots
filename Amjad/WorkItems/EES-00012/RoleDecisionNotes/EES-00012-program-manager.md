# EES-00012 — Program Manager Decision Notes

## Key Design Decisions

1. **Reuse `_then_display()` in `rules_to_rows()`**: The adapter already has a v2-aware helper for evaluation display. Promoting it to be used in `rules_to_rows()` avoids duplication.

2. **Callback over polling for live status**: A simple `on_status` callable is cleaner than polling or event-based patterns. It defaults to `None` so the public API is backward compatible.

3. **Thread-safe GUI updates via `root.after(0, ...)`**: This is the established pattern in the codebase (used by `on_complete`/`on_error`). Status callbacks follow the same pattern.

4. **Use `result.outputs` with branch field**: The v2 `EvaluationResult.outputs` list contains `{rule_id, branch, output}` dicts. This is more informative than the deprecated backward-compat properties.

5. **Add "else" column to treeviews**: Minimal UI change. Shows blank for rules without ELSE branches, which is the common case. Not adding a new detail popup — the existing double-click handler is sufficient.

## Scope Boundary

- No rule editing in GUI (future work).
- No new widgets beyond the existing status bar label.
- No changes to data persistence or the extraction agentic loop logic — only adding status emission points.
