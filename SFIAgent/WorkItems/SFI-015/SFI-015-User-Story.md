# SFI-015: Detail Page Color Indicators Not Rendering

**Status**: BACKLOG

---

## User Story

**Title**: Fix colored section indicators in detail modal

**As a**: End user viewing SFI action item details  
**I want**: Section headers (Status, Dates, Ownership, Service & Program) to display with colored circle indicators, just like in the list view  
**So that**: The detail view is visually consistent with the sidebar list and I can quickly scan section types by color

---

## Out of Scope

- Changes to color scheme or palette
- Adding new section types
- Accessibility compliance (will be handled separately)
- Mobile/responsive layout

---

## Assumptions

- **Assumption (explicit)**: The color scheme should match the sidebar list view (Status=🔴, Dates=🔵, Ownership=🟣, Service & Program=⚫)
- **Assumption (explicit)**: The detail modal is rendered using tkinter Label widgets
- **Assumption (explicit)**: The issue is in the tkinter implementation, not the data layer

---

## Acceptance Criteria

- [ ] Status section header shows a red/colored circle indicator (not black/text)
- [ ] Dates section header shows a blue/colored circle indicator  
- [ ] Ownership section header shows a purple/colored circle indicator
- [ ] Service & Program section header shows a gray/colored circle indicator
- [ ] All colored indicators are visually identical to those in the sidebar list view
- [ ] Detail modal renders correctly in both popup and embedded modes

---

## Non-Functional Requirements

- No performance degradation when opening detail view
- Colored indicators must scale correctly with different font sizes
- Should work on Windows and any other supported platform

---

## Telemetry / Metrics Expected

- None - this is a UI rendering fix

---

## Rollout / Rollback Notes

- Change is cosmetic; no breakage risk
- Can be deployed directly in next release
- If needed, can be reverted by removing color rendering code from detail modal builder

---

## Root Cause Analysis

The detail modal (`SFIReporter/src/sfi_reporter/tk_app.py`, likely around `DetailWindow` or detail modal functions) constructs section headers but likely:
1. Does not include the Unicode emoji/circle characters used in the sidebar
2. Or applies different formatting/font to header labels

The sidebar list view successfully renders colored indicators, so the approach should be copied to the detail view.

---

## Related Files

- `SFIReporter/src/sfi_reporter/tk_app.py`: Detail modal construction
- `SFIReporter/src/sfi_reporter/flet_app.py`: Flet version (if applicable)

---

## Priority

Low - Cosmetic issue; does not impact functionality

---

## Created

2026-02-05
