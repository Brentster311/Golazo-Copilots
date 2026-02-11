# SFI-023 — Expand ETA/Status Editing Across All Views

> Decomposition rationale: The original request touches three independent UI surfaces (home button behavior, bulk label clarity, KPI drill-down). Each represents a distinct user-observable outcome and can be shipped/tested independently. Split into 3 stories.

---

## Story A: Home Screen "Update ETAs" Works on All Items

**Status**: IMPLEMENTED

**User Story**
- **Title**: Expand home-screen Update ETAs to all action items
- **As a**: SFI Reporter user
- **I want**: The "Update ETAs" button on the home screen to let me edit ETA dates and statuses for **all** my action items, not just those with invalid ETAs
- **So that**: I can update the status/notes on any item without needing to drill down into the item detail modal
- **Out of scope**:
  - Changing the Bulk auto-apply logic (it should continue to only target invalid ETAs)
  - Adding new fields to the ETA edit dialog
- **Assumptions**:
  - **Assumption (explicit)**: The Manual review dialog will show all items, with invalid ETAs shown first for convenience
  - **Assumption (explicit)**: The `EtaModeDialog` text will be updated to clarify Bulk vs Manual scope
- **Acceptance Criteria**:
  - [ ] Clicking "Update ETAs" opens `EtaModeDialog` even when there are zero invalid ETAs
  - [ ] Choosing "Manual" opens `ManualEtaReviewDialog` with **all** action items (not just invalid)
  - [ ] Choosing "Bulk" still only auto-applies proposed dates to items with invalid ETAs (existing behavior preserved)
  - [ ] The `EtaModeDialog` clearly states that Bulk only applies to invalid ETAs (e.g., "⚡ Bulk — auto-fix N invalid ETAs")
  - [ ] The "Update ETAs" button is enabled whenever `detailed_items` is non-empty (not gated on invalid count > 0)
  - [ ] Existing tests for `get_items_needing_eta_update` continue to pass unchanged
- **Non-functional requirements**: No additional API calls; works on in-memory data
- **Telemetry / metrics expected**: None
- **Rollout / rollback notes**: Rebuild exe via BUILD_MANIFEST after merge

---

## Story B: Add ETA Button to KPI Drill-Down (DetailModal)

**Status**: IMPLEMENTED

**User Story**
- **Title**: Enable ETA editing from KPI drill-down view
- **As a**: SFI Reporter user
- **I want**: An "Update ETAs" button inside the `DetailModal` (the table I see when I double-click a service, program, or KPI row)
- **So that**: I can update ETAs/statuses for the filtered subset of items without going back to the home screen
- **Out of scope**:
  - Bulk auto-apply from within the drill-down (Manual review only for this view)
  - Changes to `ItemDetailsModal` (single-item view already has an ETA button)
- **Assumptions**:
  - **Assumption (explicit)**: The drill-down ETA button opens `ManualEtaReviewDialog` with all items currently displayed in the `DetailModal` (not just invalid ones), consistent with Story A
  - **Assumption (explicit)**: After saving ETAs, the `DetailModal` table refreshes to reflect updated dates/statuses
- **Acceptance Criteria**:
  - [ ] `DetailModal` has an "Update ETAs" button in its toolbar/button row
  - [ ] Clicking it opens `ManualEtaReviewDialog` with the items currently shown in the detail table
  - [ ] After completing the ETA review, the detail table rows refresh with updated ETA dates and statuses
  - [ ] The home screen summary tables also refresh after drill-down ETA saves
  - [ ] The button is disabled when the detail table is empty
- **Non-functional requirements**: No additional API calls; operates on in-memory data already loaded
- **Telemetry / metrics expected**: None
- **Rollout / rollback notes**: Rebuild exe via BUILD_MANIFEST after merge

---

## Story C: Fix SLA Status Empty + Add ETA Status Column in Drill-Down

**Status**: IMPLEMENTED

**User Story**
- **Title**: Fix empty SLA Status and add ETA Status column in DetailModal
- **As a**: SFI Reporter user
- **I want**: The SLA Status column in the drill-down to show actual values ("In SLA", "Approaching", "Out of SLA") and a new ETA Status column to be visible
- **So that**: I can see at a glance which items are out of SLA and what their current ETA status is without opening each item individually
- **Out of scope**:
  - Changing SLA calculation logic
  - Making ETA Status editable inline in the table
- **Assumptions**:
  - **Assumption (explicit)**: SLA Status being empty is a bug — the `SlaType` field exists on items but the lookup via `item.get('SlaType')` is returning `None` or a value not in the map. Investigation needed during development.
  - **Assumption (explicit)**: ETA Status column displays the `EtaStatus` field value as-is (text string)
- **Acceptance Criteria**:
  - [ ] SLA Status column in `DetailModal` displays correct values for all items (not empty)
  - [ ] Root cause of empty SLA Status is identified and fixed (likely a field name casing/mapping issue)
  - [ ] A new "ETA Status" column is added to `DetailModal` showing the `EtaStatus` field value
  - [ ] ETA Status column updates in real-time after ETA edits within the same session
  - [ ] Existing unit tests pass; new tests cover SLA status mapping edge cases
- **Non-functional requirements**: No performance impact — uses existing in-memory data
- **Telemetry / metrics expected**: None
- **Rollout / rollback notes**: Rebuild exe via BUILD_MANIFEST after merge
