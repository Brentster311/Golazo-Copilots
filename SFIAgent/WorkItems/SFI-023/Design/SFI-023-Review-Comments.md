# SFI-023 — QA Review Comments

## Design Review

### Clarity & Completeness
- **GOOD**: Clear separation of Manual (all items) vs Bulk (invalid only) 
- **GOOD**: SLA Status fix correctly identified as likely type mismatch (int vs str)
- **MINOR**: Design says "normalize to int first" for SLA fix but should specify where — at data load time or at display time. Recommend display-time normalization to avoid mutating source data.

### Feasibility & Sequencing
- **GOOD**: C → A → B order is sound. C is independent, A changes parameters, B builds on A patterns.
- **NOTE**: All three stories can realistically be implemented together since the changes are small and concentrated in `tk_app.py`.

### Edge Cases Identified
1. **Story A**: What happens when `detailed_items` is empty? The button should be disabled and `EtaModeDialog` should not open.
2. **Story A**: What if ALL items have valid ETAs (invalid_count=0)? Bulk button should be disabled or communicate "0 items to fix".
3. **Story B**: What if DetailModal is opened and then items are updated from the home screen concurrently? → Not applicable — tkinter is single-threaded, modals block.
4. **Story C**: `SlaType` could be `None`, `0`, `"0"`, `"InSla"`, `"OutOfSla"` depending on the API response. Need to handle all variants.
5. **Story C**: `EtaStatus` could be `None` or empty string — column should display empty, not "None".

### Risk Coverage
- **GOOD**: Callback chain risk identified and mitigated
- **ADD**: Should test that the `_on_eta_update_complete` callback correctly recalculates summary stats after editing previously-valid items (new behavior)

### Naming
- **OK**: Existing naming (`ManualEtaReviewDialog`, `EtaModeDialog`) is clear and reused appropriately

## Recommendations

1. Handle `EtaModeDialog` with zero invalid items: Show "⚡ Bulk — no invalid ETAs to fix" (disabled)
2. Display-time SLA normalization: Convert to int at point of use via `int(item.get('SlaType', 0))` with try/except
3. Test with actual API data shapes to confirm `SlaType` field values

---

## Architect Notes

### Architectural Alignment
- **APPROVED**: All changes are confined to `tk_app.py` UI layer. No changes to `data.py` data fetching, `eta_logic.py` core logic, or `client.py` API layer. Clean layer separation maintained.
- **APPROVED**: Callback chain pattern (DetailModal → SFIReporterApp) follows existing `ItemDetailsModal._on_eta_saved` pattern. No new architectural concepts introduced.

### API / Data Contracts
- **SlaType field**: Reviewed existing `models.py` and API responses. The field comes from S360 API as an integer (`0`, `1`, `2`). However, JSON deserialization may yield strings in some edge cases. The `_safe_sla_lookup` approach (try int conversion, fallback to string map) is the right contract.
- **EtaStatus field**: String field, nullable. No schema change needed — it already exists in item dicts.

### Security & Privacy
- No new external calls. No credential handling changes. No PII exposure changes. **No concerns.**

### Coupling & Blast Radius
- Changes are UI-only. If the new button/column code has a bug, it only affects the display — no data corruption possible since all API writes go through existing `SingleEtaEditDialog` save paths.
- `ManualEtaReviewDialog` and `BulkEtaProgressDialog` constructors are unchanged — only the data passed to them changes. Low coupling risk.

### Rollback Safety
- Pure UI changes. Git revert + rebuild exe = full rollback. No data migrations.

### Framework Default Behaviors
- **tkinter Treeview column width**: New ETA Status column will use default auto-width. Should set `minwidth` to avoid column being too narrow. Recommend `minwidth=80`.
- **Sort stability**: Python's `sorted()` with `key` is stable — invalid-first sort preserves relative order within each group. Confirmed safe.
