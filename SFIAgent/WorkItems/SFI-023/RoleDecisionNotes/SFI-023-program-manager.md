# SFI-023 — Program Manager Decision Notes

## Key Design Decisions

1. **Manual vs Bulk scope split**: Manual gets all items, Bulk stays invalid-only. This preserves the safety of Bulk (auto-applying dates to known-bad items) while giving Manual the flexibility to update statuses on any item.

2. **Drill-down uses Manual only**: No Bulk option in the drill-down to keep the UX simple. Users drilling down are typically looking at specific items.

3. **SLA Status fix approach**: Normalize `SlaType` to int before lookup rather than expanding the map with string keys. Cleaner and handles all edge cases.

4. **Callback chain for refresh**: DetailModal needs a parent callback to trigger home screen refresh after ETA saves. This follows the existing pattern used by `ItemDetailsModal._on_eta_saved`.

5. **Sort order for Manual review**: Invalid ETAs sorted first when reviewing all items — most urgent first, matching user expectation.

## Implementation Sequencing

Recommended order: C → A → B
- **Story C first**: Fixes bugs (SLA Status) and adds ETA Status column — lowest risk, immediate value
- **Story A second**: Expands home button — changes dialog parameters but doesn't add new UI
- **Story B last**: Adds button to DetailModal — depends on patterns established in A
