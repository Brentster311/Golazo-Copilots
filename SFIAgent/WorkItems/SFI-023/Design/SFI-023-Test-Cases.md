# SFI-023 — Test Cases

## Story A: Expand Home ETA Button

### TC-A01: Update ETAs button enabled with valid items only
- **Given**: `detailed_items` has 10 items, all with valid ETAs (invalid_count=0)
- **When**: Data refresh completes
- **Then**: "Update ETAs" button state is `'normal'` (not disabled)
- **Maps to**: AC "button enabled whenever detailed_items is non-empty"

### TC-A02: Update ETAs button disabled with empty items
- **Given**: `detailed_items` is empty
- **When**: Data refresh completes
- **Then**: "Update ETAs" button state is `'disabled'`

### TC-A03: EtaModeDialog shows total and invalid counts
- **Given**: 10 total items, 3 with invalid ETAs
- **When**: `EtaModeDialog` is created
- **Then**: Header text contains "10 total item(s)" and "3 with invalid ETAs"

### TC-A04: Manual opens with ALL items
- **Given**: 10 total items (3 invalid, 7 valid)
- **When**: User picks "Manual" from `EtaModeDialog`
- **Then**: `ManualEtaReviewDialog` receives list of 10 items

### TC-A05: Manual sorts invalid ETAs first
- **Given**: Items list with mix of valid and invalid ETAs
- **When**: `ManualEtaReviewDialog` receives items
- **Then**: First N items (where N = invalid count) all have invalid ETAs; remaining have valid ETAs

### TC-A06: Bulk only receives invalid items
- **Given**: 10 total items (3 invalid, 7 valid)
- **When**: User picks "Bulk" from `EtaModeDialog`
- **Then**: `BulkEtaProgressDialog` receives list of 3 items (only invalid)

### TC-A07: Bulk button disabled when zero invalid
- **Given**: 10 total items, 0 with invalid ETAs
- **When**: `EtaModeDialog` is created
- **Then**: Bulk button is disabled and text shows "⚡ Bulk — no invalid ETAs to fix"

### TC-A08: Existing get_items_needing_eta_update unchanged
- **Given**: Existing test input data
- **When**: `get_items_needing_eta_update` called
- **Then**: Returns same results as before (regression test)

---

## Story B: Drill-Down ETA Button

### TC-B01: DetailModal has Update ETAs button
- **Given**: `DetailModal` is instantiated with items
- **When**: Modal widget is created
- **Then**: Button with text "📋 Update ETAs" exists in the button frame

### TC-B02: DetailModal ETA button opens ManualEtaReviewDialog
- **Given**: `DetailModal` showing 5 filtered items
- **When**: "Update ETAs" button is clicked
- **Then**: `ManualEtaReviewDialog` is opened with those 5 items

### TC-B03: DetailModal refreshes after ETA save
- **Given**: `DetailModal` open, user edits ETA via Manual review
- **When**: Save completes successfully
- **Then**: Detail table rows are repopulated with updated ETA dates

### TC-B04: Home screen refreshes after drill-down ETA save
- **Given**: `DetailModal` open from home screen
- **When**: ETA save completes in drill-down
- **Then**: Parent `_refresh_summaries` callback is invoked

### TC-B05: DetailModal ETA button disabled when empty
- **Given**: `DetailModal` with 0 items (e.g., filter yields no results)
- **When**: Modal is displayed
- **Then**: "Update ETAs" button is disabled

---

## Story C: SLA Status Fix + ETA Status Column

### TC-C01: SLA Status maps integer SlaType correctly
- **Given**: Item with `SlaType = 0`
- **When**: SLA column value is computed in `DetailModal`
- **Then**: Displays "In SLA"

### TC-C02: SLA Status maps string SlaType correctly
- **Given**: Item with `SlaType = "2"`
- **When**: SLA column value is computed
- **Then**: Displays "Out of SLA"

### TC-C03: SLA Status handles None SlaType
- **Given**: Item with `SlaType = None`
- **When**: SLA column value is computed
- **Then**: Displays empty string (not "None", not crash)

### TC-C04: SLA Status handles missing SlaType key
- **Given**: Item dict without `SlaType` key
- **When**: SLA column value is computed
- **Then**: Displays empty string

### TC-C05: SLA Status maps "InSla"/"OutOfSla" string variants
- **Given**: Item with `SlaType = "OutOfSla"` (API string variant)
- **When**: SLA column value is computed
- **Then**: Displays "Out of SLA"

### TC-C06: ETA Status column present in DetailModal
- **Given**: `DetailModal` column definitions
- **When**: Treeview is created
- **Then**: Column with heading "ETA Status" exists

### TC-C07: ETA Status shows field value
- **Given**: Item with `EtaStatus = "Updated 2026-01-15"`
- **When**: Row is populated in detail tree
- **Then**: ETA Status cell shows "Updated 2026-01-15"

### TC-C08: ETA Status handles None value
- **Given**: Item with `EtaStatus = None`
- **When**: Row is populated
- **Then**: ETA Status cell shows empty string

### TC-C09: ETA Status updates after in-session edit
- **Given**: Item displayed in `DetailModal` with empty ETA Status
- **When**: User edits ETA and saves with notes "Fixed date"
- **Then**: ETA Status column for that item now shows "Fixed date"
