# SFI-022 Design Document: View & Manage Saved LLM Analyses

## Summary

Add "View Saved Analysis" to the right-click context menus (both the KPI action tree and the DetailModal item list) so users can load and view previously saved LLM analyses without re-calling the API. The existing `AnalysisModal` displays the result with a "Saved on [timestamp]" indicator. "Analyze with LLM" (re-analyze) remains available alongside.

## Problem Statement

SFI-020 saves LLM analysis results to disk, and the storage functions (`load_analysis`, `analysis_exists`) are already imported in `tk_app.py` but **never used**. Users currently have no way to view saved analyses through the UI — they must re-analyze every time, wasting time and API calls.

## Business Case

- **Why now**: SFI-020 already saves analyses. This is the natural completion of that feature.
- **Impact**: Users save 15-30 seconds per analysis view by loading from disk instead of calling the LLM.
- **KPIs**: Reduction in redundant LLM API calls; faster access to prior analysis work.

## Proposed Approach

### 1. Context Menu Enhancement

Both `_on_item_right_click()` (DetailModal, ~line 1181) and `_on_kpi_right_click()` (KPI tree, ~line 2499) will be updated:

```python
menu = tk.Menu(parent, tearoff=0)

# Get action item ID for saved analysis lookup
action_item_id = str(item.get("id", item.get("S360_ActionItemId", "")))

if action_item_id and analysis_exists(action_item_id):
    menu.add_command(
        label="📄 View Saved Analysis",
        command=lambda: _view_saved_analysis(parent, action_item_id),
    )

menu.add_command(
    label="🤖 Analyze with LLM",
    command=lambda: _launch_llm_analysis(parent, item),
)
```

### 2. New `_view_saved_analysis()` Function

```python
def _view_saved_analysis(parent, action_item_id: str):
    """Load and display a saved analysis from disk."""
    result = load_analysis(action_item_id)
    if result is None:
        messagebox.showerror(
            "Cannot Load Analysis",
            "The saved analysis file is corrupted or unreadable.\n"
            "Use 'Analyze with LLM' to generate a fresh analysis.",
            parent=parent,
        )
        return
    root = parent.winfo_toplevel()
    AnalysisModal(root, result, saved=True)
```

### 3. AnalysisModal Enhancement

Add an optional `saved: bool = False` parameter to `AnalysisModal.__init__()`. When `saved=True`:

- Display a **"📁 Saved on [date/time]"** header at the top of the analysis text (before the sections), using a new `"saved_header"` tag with distinct styling (e.g., blue foreground, slightly larger font).
- The timestamp comes from `result.timestamp`.

### 4. Files Changed

| File | Change |
|------|--------|
| `tk_app.py` | Update both context menus, add `_view_saved_analysis()`, modify `AnalysisModal` |

No new dependencies. No changes to `llm_storage.py` or `llm_client.py`.

## Alternatives Considered

1. **Separate "SavedAnalysisModal"**: Rejected — duplicates modal code. Adding a `saved` flag to the existing modal is simpler.
2. **Delete saved analysis button**: Out of scope per user story.
3. **Show analysis inline in the tree**: Too complex for a context menu feature.

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| `analysis_exists()` does disk I/O on every right-click | Fast path check — single `Path.exists()` call, sub-millisecond |
| Corrupted JSON file | `load_analysis()` already handles `json.JSONDecodeError` etc. and returns `None`; UI shows error + fallback |
| Action item ID mismatch | Use same ID extraction logic as `_launch_llm_analysis` |

## Test Strategy

- Unit tests for `_view_saved_analysis` (mock `load_analysis`, verify `AnalysisModal` is called or error shown)
- Unit tests for `AnalysisModal(saved=True)` behavior (saved header displayed)
- Unit tests for context menu showing/hiding "View Saved Analysis" based on `analysis_exists()`
- Test corrupted JSON fallback path

## Dependencies

- SFI-020 (complete): `save_analysis`, `load_analysis`, `analysis_exists`, `AnalysisModal`
- No external library changes needed
