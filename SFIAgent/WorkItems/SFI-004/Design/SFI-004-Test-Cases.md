# Test Cases - SFI-004

## Unit Tests

### TC-001: Window Launch
- **Input:** Run `python -m sfi_reporter.flet_app`
- **Expected:** Native window appears (not browser)
- **Type:** Manual/Integration

### TC-002: User Alias Auto-Detection
- **Input:** Launch app with Azure CLI logged in
- **Expected:** User alias field pre-populated with detected alias
- **Type:** Integration

### TC-003: User Alias Edit
- **Input:** Modify text in user alias field
- **Expected:** New value is retained and used for data fetch
- **Type:** Manual

### TC-004: Refresh Button - Success
- **Precondition:** Valid user alias entered
- **Input:** Click Refresh button
- **Expected:** 
  - Loading indicator appears
  - Data fetched from S360
  - Tables populated with services and action items
  - Success feedback shown
- **Type:** Integration

### TC-005: Refresh Button - Error
- **Precondition:** S360 API unavailable (mock)
- **Input:** Click Refresh button
- **Expected:** Error message displayed, app remains functional
- **Type:** Unit (mocked)

### TC-006: Services Table Display
- **Precondition:** Cache contains services data
- **Input:** App loads
- **Expected:** Services displayed in table with Name and ID columns
- **Type:** Integration

### TC-007: Action Items Table Display
- **Precondition:** Cache contains action items
- **Input:** App loads
- **Expected:** Action items displayed with Name, ID, Count, Out of SLA columns
- **Type:** Integration

### TC-008: Cache Age - Fresh
- **Precondition:** Cache < 30 minutes old
- **Input:** App loads
- **Expected:** Cache age shown in normal color
- **Type:** Unit

### TC-009: Cache Age - Stale
- **Precondition:** Cache > 30 minutes old
- **Input:** App loads
- **Expected:** Cache age shown in warning color (orange/yellow)
- **Type:** Unit

### TC-010: Clear Cache Button
- **Precondition:** Cache exists
- **Input:** Click Clear Cache button
- **Expected:** Cache file deleted, UI reset to empty state
- **Type:** Integration

### TC-011: Window Resizable
- **Input:** Drag window edges
- **Expected:** Window resizes, content adapts
- **Type:** Manual

### TC-012: Loading State
- **Precondition:** Slow network (mock delay)
- **Input:** Click Refresh
- **Expected:** Progress indicator visible during fetch, UI not frozen
- **Type:** Manual

## Coverage Matrix

| Acceptance Criteria | Test Case |
|---------------------|-----------|
| AC-1: Native window | TC-001 |
| AC-2: Auto-detect alias | TC-002, TC-003 |
| AC-3: Refresh button | TC-004, TC-005 |
| AC-4: Services table | TC-006 |
| AC-5: Action items table | TC-007 |
| AC-6: Cache age indicator | TC-008, TC-009 |
| AC-7: Clear cache | TC-010 |
