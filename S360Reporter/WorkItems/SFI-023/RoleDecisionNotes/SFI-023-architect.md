# SFI-023 — Architect Decision Notes

## Architectural Review Summary
- **APPROVED** — No architectural concerns. All changes are UI-layer only.
- No new dependencies, no API changes, no schema changes.
- Follows existing callback patterns for cross-component refresh.

## Key Decisions
1. **SLA normalization at display time**: Convert `SlaType` to int with try/except at the point of rendering, not at data load. This avoids side effects on the shared item dicts and keeps the data layer pure.
2. **ETA Status column width**: Recommend `minwidth=80` for the new Treeview column to avoid truncation.
3. **No new architectural patterns**: Reuse existing `_on_eta_saved` callback pattern for DetailModal → parent refresh.

## No New User Stories Required
All changes fit within the existing stories. No scope expansion detected.
