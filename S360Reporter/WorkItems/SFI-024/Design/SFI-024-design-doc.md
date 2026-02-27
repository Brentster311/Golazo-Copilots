# SFI-024 — Design Doc (Express)

## Summary
Two UX enhancements to ETA editing in S360Reporter:
1. "Update ETAs for N selected" button in DetailModal drill-down (selection-aware)
2. "View Details" button in ManualEtaReviewDialog to open ItemDetailsModal

## Approach
### Story A: Selected-item ETA in drill-down
- Bind `<<TreeviewSelect>>` event on `DetailModal.tree` to update a new `self.selected_eta_btn`
- Button text dynamically shows count: "📋 Update ETAs for N selected"
- Disabled when selection is empty; clicking opens `ManualEtaReviewDialog` with selected items only
- After save, existing refresh chain handles tree + home screen update

### Story B: View Details from Manual Review
- Add "🔍 View Details" button to `ManualEtaReviewDialog._show_current` button row
- Clicking opens `ItemDetailsModal(self, current_item)` — non-modal (no `grab_set`)
- No changes to ItemDetailsModal itself
