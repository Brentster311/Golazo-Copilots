# SFI-007: Test Cases

## Unit Tests

### TC-001: ItemDetailsModal Creation
- **Given**: A valid action item dict
- **When**: ItemDetailsModal is created
- **Then**: Modal window opens as a Toplevel widget
- **Expected**: Modal exists and is visible

### TC-002: Modal Close via Button
- **Given**: An open ItemDetailsModal
- **When**: User clicks Close button
- **Then**: Modal is destroyed
- **Expected**: `winfo_exists()` returns False

### TC-003: Modal Close via Escape
- **Given**: An open ItemDetailsModal  
- **When**: User presses Escape key
- **Then**: Modal is destroyed
- **Expected**: `winfo_exists()` returns False

### TC-004: Field Grouping Function
- **Given**: An item dict with various fields
- **When**: `group_item_fields(item)` is called
- **Then**: Fields are grouped into categories
- **Expected**: Returns dict with keys: identity, status, dates, ownership, service_program, other

### TC-005: Empty Fields Hidden
- **Given**: An item with some empty/null fields
- **When**: Fields are formatted for display
- **Then**: Empty fields are not shown
- **Expected**: Only non-empty fields appear in output

### TC-006: Field Label Formatting
- **Given**: Raw field names like "S360_AssignedTo", "_kpi_id"
- **When**: `format_field_label(field_name)` is called
- **Then**: Labels are human-readable
- **Expected**: "S360 Assigned To", "KPI ID"

### TC-007: List Value Formatting
- **Given**: A field with list value like `['id1', 'id2']`
- **When**: Value is formatted for display
- **Then**: List is displayed readably
- **Expected**: "id1, id2" or multi-line format

## Integration Tests (Manual)

### MT-001: Double-Click in Drill-Down Opens Details
1. Open app, load data
2. Double-click a service row (opens drill-down modal)
3. Double-click a row in the drill-down modal
4. Verify ItemDetailsModal opens with correct item data

### MT-002: Field Display Verification
1. Open details for an item
2. Verify fields are grouped logically
3. Verify empty fields are hidden
4. Verify list fields display correctly

### MT-003: Scrolling Works
1. Open details for an item with many fields
2. Verify content is scrollable
3. Verify all content is accessible via scroll
