# GCP-0024: Architect Notes

## Session Date
2026-02-07

## Architecture Decisions

### 1. Evidence Type Routing
The existing `validate_evidence()` router pattern was extended:
- `FILE_EVIDENCE_ITEMS` now includes `refactorComplete` and `retroComplete`
- Removed special case for `NA_ALLOWED_ITEMS`
- Cleaner, more uniform validation

### 2. State Schema
`WorkItemState.dod` default dict extended with 8th item:
```python
"retroComplete": ChecklistItem()
```
Backward compatible - old state files missing this key will get default.

### 3. Role Transition Graph
Updated adjacency list in `TRANSITIONS`:
```
refactor-expert → [Documenter, developer]  # was [builder, developer]
Documenter → [builder, refactor-expert]     # was [retrospective, builder]
builder → [retrospective, Documenter]       # was [Documenter, refactor-expert]
```

## Design Patterns Used
- **Strategy pattern** - Evidence validators selected by item type
- **State machine** - Role transitions with phase tracking

## Technical Debt
None introduced. Removed N/A escape hatch reduces complexity.
