# SFI-023 — Project Owner Assistant Decision Notes

## Decomposition Decision
The original request contained 3 independent user-observable outcomes:
1. Home screen ETA button works on all items (not just invalid)
2. Bulk action label clarification
3. KPI drill-down ETA button + SLA/ETA status fix

Split into 3 stories because each can be independently shipped, tested, and demonstrated.

**Stories A & B** are related (both expand ETA editing scope) but target different UI surfaces (home vs drill-down). **Story C** includes a bug fix (SLA Status empty) bundled with a feature (ETA Status column) because they both affect the same `DetailModal` columns and are best addressed together.

## Must-Ask Checklist Resolution
- **Interface type**: Tkinter desktop GUI (known from existing app)
- **Target platform**: Windows (PyInstaller --onefile exe)
- **Data persistence**: In-memory + API calls to S360 (existing pattern)
- **User type**: Technical (internal Microsoft team)

## Scope Decisions
- **Bulk stays invalid-only**: User confirmed Bulk should continue to only auto-fix invalid ETAs. The Manual path is what expands to all items.
- **KPI drill-down edits all items**: User confirmed the drill-down ETA button should allow editing all items in the filtered view (not just invalid).
- **SLA Status is a bug**: User confirmed this should already be showing data — it's a bug, not a new feature.

## Assumptions Made
- Manual review shows all items with invalid ones first (logical UX — most urgent first)
- Drill-down ETA uses `ManualEtaReviewDialog` (no Bulk option in drill-down to keep it simple)
- After ETA saves in drill-down, both the detail table and home screen refresh
