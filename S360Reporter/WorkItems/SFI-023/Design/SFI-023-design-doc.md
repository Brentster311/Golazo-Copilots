# SFI-023 — Design Document

## Summary

Expand the S360Reporter's ETA/status editing capabilities across all views:
- **Story A**: Home screen "Update ETAs" operates on all items (Manual reviews all; Bulk still targets invalid only)
- **Story B**: Add an "Update ETAs" button to the `DetailModal` (KPI/service/program drill-down)
- **Story C**: Fix SLA Status showing empty in drill-down + add ETA Status column

## Problem Statement

Currently the "Update ETAs" button is limited to items with invalid ETAs. Users frequently need to update ETA status/notes on items that already have valid dates (e.g., changing status to reflect progress). Additionally, the drill-down view lacks an ETA editing affordance, forcing users back to the home screen. Finally, SLA Status shows empty in the drill-down and ETA Status is not displayed.

## Business Case

- **Why now**: Team is actively using S360Reporter for weekly SFI compliance. Inability to update statuses on valid items and missing SLA data in drill-downs are daily friction points.
- **Impact**: Reduces clicks-per-update from ~5 (drill-down → item detail → edit → close → close) to 2 (button → review dialog).
- **KPIs**: All action items editable from any view; SLA Status populated for 100% of items in drill-down.

## Stakeholders

| Role | Who |
|------|-----|
| User / Requester | brentj |
| Developer | Copilot-assisted |

## Functional Requirements

### Story A: Expand Home ETA Button
| # | Requirement |
|---|-------------|
| A1 | `_on_update_etas` passes ALL `detailed_items` to `ManualEtaReviewDialog` when Manual is chosen |
| A2 | `_on_update_etas` passes only `get_items_needing_eta_update()` to `BulkEtaProgressDialog` when Bulk is chosen |
| A3 | `EtaModeDialog` button text changes from "⚡ Bulk — auto-apply proposed dates" to "⚡ Bulk — auto-fix N invalid ETAs" |
| A4 | "Update ETAs" button enabled when `detailed_items` is non-empty (remove invalid-count gate) |
| A5 | `EtaModeDialog` header changes from "N item(s) with invalid ETAs" to "N total item(s) (M with invalid ETAs)" |
| A6 | Manual review sorts invalid ETAs first, then valid items |

### Story B: Drill-Down ETA Button
| # | Requirement |
|---|-------------|
| B1 | `DetailModal` adds "📋 Update ETAs" button in toolbar row |
| B2 | Button opens `ManualEtaReviewDialog` with the filtered items displayed in the modal |
| B3 | After save, `DetailModal` table refreshes (re-populates tree from mutated items) |
| B4 | Home screen summary tables refresh via existing `_refresh_summaries()` callback |
| B5 | Button disabled when detail table has zero items |

### Story C: SLA/ETA Status Fix
| # | Requirement |
|---|-------------|
| C1 | Investigate and fix SLA Status mapping — likely `item.get('SlaType')` returns string `"0"`, `"1"`, `"2"` instead of int |
| C2 | Add `eta_status` column to `DetailModal` column definitions |
| C3 | ETA Status column shows `item.get('EtaStatus', '')` |
| C4 | ETA Status column updates after in-session ETA edits |

## Non-Functional Requirements

- No additional API calls — all changes operate on in-memory data
- No new dependencies
- Exe size unchanged (no new packages)
- All existing tests must continue to pass

## Proposed Approach (High Level)

### Story A — Changes to `tk_app.py`

1. **`_on_update_etas` (~L2535)**: Get both `all_items = self.current_data['detailed_items']` and `invalid_items = get_items_needing_eta_update(all_items)`. Pass `all_items` to `EtaModeDialog` and `ManualEtaReviewDialog`. Pass `invalid_items` to `BulkEtaProgressDialog`.

2. **`EtaModeDialog` (~L1637)**: Update `__init__` to accept both `total_count` and `invalid_count`. Update header and button text. Pass-through to appropriate dialog.

3. **`_build_eta_button` enable logic (~L2297)**: Change `self.btn_etas.configure(state='normal' if invalid_count > 0 else 'disabled')` to `state='normal' if total_count > 0 else 'disabled'`.

4. **`ManualEtaReviewDialog` sort order**: Sort items so invalid ETAs come first.

### Story B — Changes to `tk_app.py`

1. **`DetailModal.__init__` (~L1070)**: Add "📋 Update ETAs" button to the button row (after Close button).

2. **New method `DetailModal._on_update_etas`**: Collect items from `self.items`, open `ManualEtaReviewDialog`, on save: call `self._populate_tree()` to refresh, invoke optional parent callback.

3. **Wire parent callback**: `SFIReporterApp` passes `_refresh_summaries` callback to `DetailModal` for post-save refresh.

### Story C — Changes to `tk_app.py`

1. **SLA Status fix (~L1133)**: Change `sla_map` lookup to handle both `int` and `str` keys: `sla_map.get(item.get('SlaType'), sla_map.get(str(item.get('SlaType', '')), ''))` — or normalize to int first.

2. **Add `eta_status` column (~L1103)**: Add to `self.columns` list and configure Treeview heading.

3. **Populate ETA Status**: In `_populate_tree`, add `item.get('EtaStatus', '')` to row values.

## Alternatives Considered

| Alternative | Why rejected |
|-------------|-------------|
| Add Bulk option to drill-down | Over-scoped for first iteration; Manual is sufficient |
| Inline-edit ETA in drill-down table | Complex Treeview widget interaction; defer to future story |
| Add ETA Status to home summary tables | Already showing "Invalid ETA" count; display name change insufficient |

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| SLA Status field name varies across environments | Medium | Medium | Test with actual API data; add fallback to empty string |
| ManualEtaReviewDialog overwhelmed with large item lists (100+) | Low | Low | Already handles scrollable list; no change needed |
| Mutating items in drill-down doesn't propagate to home | Medium | High | Wire callback chain: DetailModal → SFIReporterApp._refresh_summaries |

## Open Questions

None — all clarified during PO phase.

## Dependencies

- `eta_logic.py`: `get_items_needing_eta_update()` — used unchanged for Bulk filtering
- `data.py`: `is_invalid_eta()` — used unchanged  
- `ManualEtaReviewDialog`, `BulkEtaProgressDialog`, `SingleEtaEditDialog` — existing dialogs, minor parameter changes

## Migration / Rollout / Rollback

- **Rollout**: Rebuild exe per BUILD_MANIFEST.md, redistribute zip
- **Rollback**: Revert git commit, rebuild exe
- **No data migration**: All changes are UI-only

## Observability Plan

- Existing log file at `%TEMP%\GUI\\sfi_reporter.log` captures ETA update events
- No new telemetry needed

## Test Strategy Summary

| Area | Type | Coverage |
|------|------|----------|
| Story A: ETA button enabled logic | Unit test | Button state based on item count |
| Story A: EtaModeDialog text | Unit test | Header/button text with various counts |
| Story A: Manual shows all items | Unit test | Verify all items passed, sorted invalid-first |
| Story A: Bulk still filters invalid | Unit test | Verify only invalid items passed |
| Story B: DetailModal ETA button | Unit test | Button presence, click handler wiring |
| Story B: Post-save refresh | Unit test | Verify callback chain |
| Story C: SLA Status mapping | Unit test | Test int, string, None, missing keys |
| Story C: ETA Status column | Unit test | Column presence, value population |
