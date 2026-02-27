# SFI-026 — Project Owner Assistant Decision Notes

## Work Item
**ID**: SFI-026
**Title**: Multi-Level Owner Grouping in Services Table

## Scope Decisions

### Single Story — No Decomposition Needed
The feature has **one user-observable outcome**: the services table displays a 2-level hierarchy instead of 1-level. While the implementation touches multiple functions (`get_org_mapping`, `aggregate_by_owner`, `_update_tables`, `_on_service_double_click`), these are all internal to the same feature and cannot be shipped independently. A user cannot benefit from a half-implemented hierarchy.

### Out-of-Scope Rationale
- **3+ level nesting**: The current org depth between alexhowells and leaf ICs is at most 2 levels. Supporting arbitrary depth would add significant complexity (recursive treeview, recursive aggregation) for zero current benefit. Can be revisited if needed.
- **Streamlit UI**: The Streamlit web UI does not currently have the services table grouping feature at all. Adding it there is a separate work item.
- **Action Items / KPI Trends tables**: These tables are not grouped by owner and remain unaffected.

## Assumptions Log

| # | Assumption | Justification |
|---|-----------|---------------|
| 1 | S360 management-chain API returns full chain | Confirmed working in SFI-013; no API changes since |
| 2 | 2-level = viewer → directs → their directs | Matches user's screenshot showing alexhowells → muralic → muralic's reports |
| 3 | 1-level managers see no change | Backward compatibility is critical; muralic's view must not regress |
| 4 | `is_manager_view` already handles 2-level managers | The detection checks if the user has *any* reports, not just 1-level reports |

## Must-Ask Checklist Resolution

| Question | Answer | Source |
|----------|--------|--------|
| Interface type | Tkinter desktop GUI | Existing — S360Reporter is a Tkinter app |
| Target platform | Windows (PyInstaller) | Existing — already ships as Windows .exe |
| Data persistence | In-memory (API data cached per session) | Existing — no persistence changes needed |
| User type | Non-technical end users (managers) | Existing — S360Reporter targets engineering managers |

All must-ask items are resolved from existing project context. No ambiguity.

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Regression in 1-level grouping | Medium | AC-2 explicitly tests backward compatibility; SFI-014 bug fixes must be preserved |
| Performance degradation from extra API calls | Low | Same management-chain endpoint is queried; just different traversal of the returned chain |
| "Unknown Owner" edge cases | Medium | AC-7 covers this; SFI-014 already fixed a related bug — must verify the fix still applies at 2 levels |

## Prior Work Item References
- **SFI-013**: Original services table grouping (1-level). Contains the initial design and implementation of `get_org_mapping()`, `aggregate_by_owner()`, and the three-branch display logic.
- **SFI-014**: Bug fixes for 1-level grouping — "Unknown Owner" appearing for manager's own items, drill-down filter correction. These fixes must be preserved during the 2-level extension.
