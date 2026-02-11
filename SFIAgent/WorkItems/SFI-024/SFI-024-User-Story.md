# SFI-024 — Selected-Item ETA Updates & Manual Review Details Button

> Two enhancements to SFI-023's ETA editing features, shipped together as they both improve the ETA editing UX.

---

## Story A: Update ETAs for Selected Items in Drill-Down

**Status**: IMPLEMENTED

**User Story**
- **Title**: Update ETAs for multi-selected items in drill-down
- **As a**: SFI Reporter user
- **I want**: When I select multiple rows in the `DetailModal` drill-down, a new button appears: "Update ETAs for N selected item(s)"
- **So that**: I can update ETAs for just the items I care about without touching the rest
- **Out of scope**: Bulk auto-apply on selected items (Manual review only)
- **Assumptions**:
  - **Assumption (explicit)**: The button text updates dynamically with the selection count
  - **Assumption (explicit)**: If nothing is selected, the button is hidden or disabled
  - **Assumption (explicit)**: Uses existing `ManualEtaReviewDialog` with the selected subset
- **Acceptance Criteria**:
  - [ ] A "📋 Update ETAs for N selected" button appears in the `DetailModal` button bar
  - [ ] Button is disabled when no rows are selected; enabled and count updates when selection changes
  - [ ] Clicking it opens `ManualEtaReviewDialog` with only the selected items
  - [ ] After save, the detail tree and home screen refresh
- **Non-functional requirements**: No additional API calls
- **Telemetry / metrics expected**: None
- **Rollout / rollback notes**: Rebuild exe via BUILD_MANIFEST

---

## Story B: Open Item Details from Manual ETA Review

**Status**: IMPLEMENTED

**User Story**
- **Title**: View item details from within Manual ETA review dialog
- **As a**: SFI Reporter user
- **I want**: A button in the `ManualEtaReviewDialog` per-item view that opens the `ItemDetailsModal` for the current item
- **So that**: I can see all the item's fields/context before deciding on an ETA
- **Out of scope**: Editing the item from within ItemDetailsModal during manual review
- **Assumptions**:
  - **Assumption (explicit)**: Opens the existing `ItemDetailsModal` as a non-modal child (so user can view it side-by-side)
- **Acceptance Criteria**:
  - [ ] A "🔍 View Details" button appears in the ManualEtaReviewDialog button row
  - [ ] Clicking it opens `ItemDetailsModal` for the current item
  - [ ] The Manual ETA dialog remains usable after viewing details (not blocked)
- **Non-functional requirements**: None
- **Telemetry / metrics expected**: None
- **Rollout / rollback notes**: Rebuild exe via BUILD_MANIFEST
