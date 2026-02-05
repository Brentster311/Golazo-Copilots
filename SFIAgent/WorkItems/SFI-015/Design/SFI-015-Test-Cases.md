# SFI-015: Test Cases - Detail Modal Color Indicators

**Date**: 2026-02-05  
**QA Lead**: Quality Assurance Role  

---

## Test Overview

### Objective
Verify that section headers in the detail modal display colored circle indicators matching the sidebar list view.

### Test Environment
- **Platform**: Windows (required); Mac/Linux (optional)
- **Application**: SFI Reporter Desktop (tkinter)
- **Test Type**: Manual visual inspection + functional regression

### Acceptance Criteria Mapping

| Test ID | Acceptance Criterion | Test Method |
|---------|---------------------|-------------|
| TC-001 | Status header shows red circle | Visual inspection |
| TC-002 | Dates header shows blue circle | Visual inspection |
| TC-003 | Ownership header shows purple circle | Visual inspection |
| TC-004 | Service & Program header shows gray circle | Visual inspection |
| TC-005 | All indicators match sidebar colors | Side-by-side comparison |
| TC-006 | Detail modal renders in popup mode | Functional test |
| TC-007 | Detail modal renders in embedded mode | Functional test |

---

## Test Cases

### TC-001: Status Header Color Indicator

**Objective**: Verify Status section header displays a red circle indicator

**Preconditions**:
1. SFI Reporter app is running
2. At least one SFI action item is loaded in the sidebar
3. User has clicked to open the detail modal for an item

**Steps**:
1. Open SFI Reporter desktop app
2. Click on any action item in the sidebar to open the detail view
3. Locate the "Status" section header in the detail modal
4. Inspect the section header label

**Expected Result**:
- Section header shows text "🔴 Status" (red circle emoji + text)
- Red circle is clearly visible and matches the red circle in the sidebar list view
- Text is readable and not obscured

**Failed Result Example**:
- Header shows only "Status" without emoji
- Header shows emoji but it's black or a different color
- Emoji is not rendering (shows as blank or placeholder)

**Test Status**: [ ] Pass / [ ] Fail / [ ] Not Applicable  
**Notes**: _______________________________________________________________________________

---

### TC-002: Dates Header Color Indicator

**Objective**: Verify Dates section header displays a blue circle indicator

**Preconditions**:
Same as TC-001

**Steps**:
1. In the detail modal, locate the "Dates" section header
2. Inspect the section header label

**Expected Result**:
- Section header shows text "🔵 Dates" (blue circle emoji + text)
- Blue circle is clearly visible and matches the blue circle in the sidebar list view
- Text is readable and not obscured

**Failed Result Example**:
- Header shows only "Dates" without emoji
- Header shows emoji but it's not blue
- Emoji rendering failed

**Test Status**: [ ] Pass / [ ] Fail / [ ] Not Applicable  
**Notes**: _______________________________________________________________________________

---

### TC-003: Ownership Header Color Indicator

**Objective**: Verify Ownership section header displays a purple circle indicator

**Preconditions**:
Same as TC-001

**Steps**:
1. In the detail modal, locate the "Ownership" section header
2. Inspect the section header label

**Expected Result**:
- Section header shows text "🟣 Ownership" (purple circle emoji + text)
- Purple circle is clearly visible and matches the purple circle in the sidebar list view
- Text is readable and not obscured

**Failed Result Example**:
- Header shows only "Ownership" without emoji
- Header shows emoji but it's not purple
- Emoji rendering failed

**Test Status**: [ ] Pass / [ ] Fail / [ ] Not Applicable  
**Notes**: _______________________________________________________________________________

---

### TC-004: Service & Program Header Color Indicator

**Objective**: Verify Service & Program section header displays a gray circle indicator

**Preconditions**:
Same as TC-001

**Steps**:
1. In the detail modal, locate the "Service & Program" section header
2. Inspect the section header label

**Expected Result**:
- Section header shows text "⚫ Service & Program" (gray/dark circle emoji + text)
- Gray circle is clearly visible and matches the gray circle in the sidebar list view (if applicable)
- Text is readable and not obscured

**Failed Result Example**:
- Header shows only "Service & Program" without emoji
- Header shows emoji but it's not gray
- Emoji rendering failed

**Test Status**: [ ] Pass / [ ] Fail / [ ] Not Applicable  
**Notes**: _______________________________________________________________________________

---

### TC-005: All Indicators Match Sidebar Colors

**Objective**: Verify all detail modal indicators visually match the sidebar list view indicators

**Preconditions**:
1. SFI Reporter app is running with detail modal open
2. Sidebar list view is also visible

**Steps**:
1. Position windows so both sidebar and detail modal are visible
2. Compare each colored indicator in the detail modal against the corresponding indicator in the sidebar list view
3. Check for color consistency:
   - Status: red → red
   - Dates: blue → blue
   - Ownership: purple → purple
   - Service & Program: gray → gray

**Expected Result**:
- All indicators in detail modal match the color appearance of indicators in sidebar list view
- No color discrepancies observed (e.g., red appearing as orange, blue appearing as purple, etc.)

**Failed Result Example**:
- Status indicator in detail modal is red, but in sidebar is a different shade
- Emoji in detail vs. list view render differently
- Indicators are missing in one view but present in the other

**Test Status**: [ ] Pass / [ ] Fail / [ ] Not Applicable  
**Notes**: _______________________________________________________________________________

---

### TC-006: Detail Modal Renders in Popup Mode

**Objective**: Verify detail modal displays correctly in popup mode with colored indicators

**Preconditions**:
1. SFI Reporter is running with items loaded

**Steps**:
1. Click on an action item in the sidebar list to open the detail view in popup mode
2. Verify the popup window opens
3. Verify all section headers (Status, Dates, Ownership, Service & Program) are visible with colored indicators
4. Verify the modal can be closed (X button or ESC key)

**Expected Result**:
- Popup loads successfully with all section headers displaying colored circle indicators
- Popup is responsive and displays all action item details
- Popup can be closed without errors
- Other UI elements are not affected

**Failed Result Example**:
- Popup fails to render or crashes
- Colored indicators don't appear in popup mode
- Popup is unresponsive or throws errors

**Test Status**: [ ] Pass / [ ] Fail / [ ] Not Applicable  
**Notes**: _______________________________________________________________________________

---

### TC-007: Detail Modal Renders in Embedded Mode

**Objective**: Verify detail modal displays correctly if embedded in the sidebar (if applicable)

**Preconditions**:
1. SFI Reporter is running with an embedded detail view option (if supported)

**Steps**:
1. If the app supports embedded detail view, load an action item into the embedded details area
2. Verify all section headers (Status, Dates, Ownership, Service & Program) are visible with colored indicators
3. Verify the sidebar and detail view remain responsive together

**Expected Result**:
- Embedded detail view loads successfully with all section headers displaying colored circle indicators
- Embedded view displays all details without layout issues
- Both sidebar and embedded view remain responsive

**Failed Result Example**:
- Embedded detail view doesn't render colored indicators
- Layout is broken or overlapping
- App crashes when loading embedded details

**Test Status**: [ ] Pass / [ ] Fail / [ ] Not Applicable  
**Notes**: _______________________________________________________________________________

---

## Edge Case Tests

### TC-008: Long Section Names Alignment (Edge Case)

**Objective**: Verify indicator alignment with longer-than-expected section names

**Preconditions**:
- Detail modal is open

**Steps**:
1. If any section headers are extended (e.g., "Service & Program Information"), verify emoji alignment
2. Check that emoji doesn't overlap with text
3. Check that text doesn't wrap unexpectedly

**Expected Result**:
- Emoji is properly aligned before text
- No overlapping or text wrapping issues
- Headers remain readable

**Test Status**: [ ] Pass / [ ] Fail / [ ] Not Applicable  
**Notes**: _______________________________________________________________________________

---

### TC-009: Font Size Scaling (Edge Case)

**Objective**: Verify emoji scales correctly with different font sizes

**Preconditions**:
- Detail modal is open
- App font size can be adjusted (if supported)

**Steps**:
1. If the app supports font size adjustment, try increasing/decreasing font size
2. Open detail view and verify emoji scales proportionally
3. Verify alignment is maintained at different font sizes

**Expected Result**:
- Emoji scales with text and remains visible
- Alignment is maintained
- No rendering issues at extreme font sizes

**Test Status**: [ ] Pass / [ ] Fail / [ ] Not Applicable  
**Notes**: _______________________________________________________________________________

---

### TC-010: Dark Mode Rendering (Edge Case)

**Objective**: Verify indicators are visible in dark theme (if applicable)

**Preconditions**:
- SFI Reporter supports dark theme mode

**Steps**:
1. If dark theme is available, switch app to dark mode
2. Open detail modal
3. Verify all colored indicators are visible and have sufficient contrast

**Expected Result**:
- All indicators are clearly visible in dark mode
- Contrast is sufficient for readability
- No indicators are "lost" against the dark background

**Test Status**: [ ] Pass / [ ] Fail / [ ] Not Applicable  
**Notes**: _______________________________________________________________________________

---

## Regression Tests

### TC-011: Detail Modal Information Unchanged

**Objective**: Verify that adding colored indicators doesn't affect displayed information

**Preconditions**:
- Detail modal is open before and after emoji rendering changes

**Steps**:
1. Open detail view and note all displayed information (KPI ID, URL, Status values, Dates, Owner names, Service Tree Info, etc.)
2. Verify all information is still present after emoji rendering is added
3. Verify no information is cut off or hidden

**Expected Result**:
- All action item details are visible and unchanged
- No information is truncated or obscured by emoji
- Layout remains intact

**Failed Result Example**:
- Some fields are now hidden or truncated
- Text overlaps with emoji
- Information is cut off at window edges

**Test Status**: [ ] Pass / [ ] Fail / [ ] Not Applicable  
**Notes**: _______________________________________________________________________________

---

### TC-012: Detail Modal Interaction Unchanged

**Objective**: Verify that adding colored indicators doesn't affect modal interaction

**Preconditions**:
- Detail modal is open

**Steps**:
1. Test modal interactions:
   - Can close modal (X button, ESC key, click outside)
   - Can scroll detail contents if needed
   - Can interact with any clickable links (e.g., URLs)
   - Can resize modal if resizable
   - Can drag modal if draggable

**Expected Result**:
- All interactions work as expected before the change
- No new errors or unresponsiveness

**Failed Result Example**:
- Modal can't be closed
- Scrolling is broken
- Links don't work
- Modal is unresponsive

**Test Status**: [ ] Pass / [ ] Fail / [ ] Not Applicable  
**Notes**: _______________________________________________________________________________

---

## Test Summary

| Test ID | Status | Pass | Fail | Notes |
|---------|--------|------|------|-------|
| TC-001 | | [ ] | [ ] | |
| TC-002 | | [ ] | [ ] | |
| TC-003 | | [ ] | [ ] | |
| TC-004 | | [ ] | [ ] | |
| TC-005 | | [ ] | [ ] | |
| TC-006 | | [ ] | [ ] | |
| TC-007 | | [ ] | [ ] | |
| TC-008 | | [ ] | [ ] | |
| TC-009 | | [ ] | [ ] | |
| TC-010 | | [ ] | [ ] | |
| TC-011 | | [ ] | [ ] | |
| TC-012 | | [ ] | [ ] | |

**Overall Test Result**: [ ] PASS / [ ] FAIL / [ ] CONDITIONAL

**Tester Name**: ____________________________  
**Date**: ____________________________  
**Platform(s) Tested**: Windows [ ] | Mac [ ] | Linux [ ]

---

## Known Issues / Observations

(To be filled during testing)

_______________________________________________________________________________

_______________________________________________________________________________

_______________________________________________________________________________

---

## Recommendations for Developer

1. Before submitting PR, ensure TC-001 through TC-005 pass on Windows
2. If submitting for cross-platform testing, ensure TC-008 through TC-010 pass on at least one other OS
3. If any test fails, document the failure and create a follow-up work item
4. Update emoji rendering code comment to explain the color mapping for future maintainers
