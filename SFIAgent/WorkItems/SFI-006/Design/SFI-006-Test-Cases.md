# SFI-006: Test Cases

## Unit Tests

### TC-001: Modal Creation
- **Given**: A valid filter context
- **When**: DetailModal is created
- **Then**: Modal window opens as a Toplevel widget
- **Expected**: Modal is a child of root window

### TC-002: Modal Close via Button
- **Given**: An open DetailModal
- **When**: User clicks Close button
- **Then**: Modal is destroyed
- **Expected**: `winfo_exists()` returns False

### TC-003: Modal Close via Escape
- **Given**: An open DetailModal
- **When**: User presses Escape key
- **Then**: Modal is destroyed
- **Expected**: `winfo_exists()` returns False

### TC-004: Filter by Service
- **Given**: detailed_items with multiple services
- **When**: Filtering by a specific serviceTreeId
- **Then**: Only items matching that service are returned
- **Expected**: All returned items have matching serviceTreeId

### TC-005: Filter by Program
- **Given**: detailed_items with program assignments
- **When**: Filtering by a specific program ID
- **Then**: Only items with that program in S360_ProgramIds are returned
- **Expected**: All returned items have matching program

### TC-006: Filter by Action Item ID
- **Given**: detailed_items list
- **When**: Filtering by a specific item ID
- **Then**: Exactly one item is returned
- **Expected**: Item ID matches filter

### TC-007: Empty Filter Result
- **Given**: Filter that matches no items
- **When**: Modal is opened
- **Then**: Modal shows "No items found" message
- **Expected**: User sees empty state, not error

## Integration Tests (Manual)

### MT-001: Double-Click Service Row
1. Load data for a user
2. Double-click a service row
3. Verify modal opens with correct title
4. Verify items shown are for that service only

### MT-002: Double-Click Program Row
1. Load data for a user
2. Double-click a program row
3. Verify modal opens with correct title
4. Verify items shown are for that program only

### MT-003: Double-Click Action Item Row
1. Load data for a user
2. Double-click an action item row
3. Verify modal opens showing single item details
