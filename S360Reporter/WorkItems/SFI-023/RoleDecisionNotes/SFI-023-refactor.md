# SFI-023 — Refactor Expert Decision Notes

## Refactoring Applied

### Extracted `_populate_rows` in `DetailModal`
- **Problem**: `_build_tree` and `_refresh_items` had identical row-insertion loops (8 lines duplicated).
- **Fix**: Extracted shared logic into `_populate_rows(items)`. Both callers now delegate to it.
- **Impact**: Single source of truth for row-building. Adding/removing columns only requires one change.

## Not Refactored (Rationale)
- `_SLA_DISPLAY_MAP` uses a flat dict with all key variants — simple, fast O(1) lookup. A normalize-and-lookup approach would be more "elegant" but slower and harder to debug.
- `_resolve_eta_status` is intentionally simple (one-liner). No need to over-engineer.
- `EtaModeDialog._create_widgets` inlines button creation — could extract, but the method is short (20 lines) and readable as-is.

## Test Results
```
211 passed in 0.90s (no changes to behavior)
```
