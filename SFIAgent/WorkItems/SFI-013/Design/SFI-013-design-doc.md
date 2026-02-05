# SFI-013 Design Document

## Summary

Add a "Service Summary (by Owner)" section to the SFI Reporter that groups services by their DevOwner, enabling managers to see action item distribution across their direct reports.

## Problem Statement

Currently, the SFI Reporter shows service-level and program-level summaries, but managers cannot easily see which team members are responsible for the most action items. To understand team member workload, managers must manually correlate services to people.

## Business Case

### Why Now
- Managers need accountability visibility at the person level
- S360 web UI shows "Accountable Owner" but doesn't aggregate by person
- Team leads reviewing SFI status need to quickly identify who needs help

### Impact
- Reduces manager time spent correlating data manually
- Improves visibility into team workload distribution
- Enables faster identification of team members with SLA issues

### KPIs
- Feature adoption: Do managers use the grouped view?
- Time saved: Qualitative feedback on workflow improvement

## Stakeholders

| Role | Stakeholder | Interest |
|------|-------------|----------|
| User | Engineering Managers | Primary users of grouped view |
| User | Individual Contributors | Existing functionality preserved |
| Developer | SFI Reporter Team | Implementation |

## Functional Requirements

### FR1: Detect Manager Mode
- Check if `get_default_landing_view()` returns `TeamGroup` instead of `Service` items
- If TeamGroup present, user is a manager → show owner grouping

### FR2: Build Service-to-Owner Mapping
- Collect all unique service names from `detailed_items`
- For each service, call `search(service_name)` to get `Owners` field
- Parse Owners JSON array to extract owner names
- Build mapping: `{service_id: [owner_names]}`

### FR3: Aggregate by Owner
- For each action item, look up its `S360_ServiceId` in the mapping
- Aggregate stats per owner: count, SLA, invalid_eta
- Handle multi-owner services: count item under each owner

### FR4: Display Owner Summary
- New Treeview section "Service Summary (by Owner)"
- Columns: Owner Name, Count, Out of SLA, Invalid ETA
- Sorted by count descending (busiest first)
- Clickable rows to drill down

### FR5: Drill Down by Owner
- When owner row clicked, filter action items to that owner's services
- Reuse existing `DetailModal` with filtered items

## Non-Functional Requirements

### Performance
- Owner lookups may require N API calls (one per unique service)
- Mitigate with parallel fetching using ThreadPoolExecutor
- Target: <5 seconds additional time for typical team size (10-20 services)

### Reliability
- If owner lookup fails for a service, categorize as "Unknown Owner"
- Don't block refresh if some lookups fail

### Maintainability
- Reuse existing UI patterns (SortableTreeview, DetailModal)
- New functions should be testable in isolation

## Proposed Approach

### Phase 1: Data Layer
1. Add `is_manager_view()` function to detect TeamGroup in landing view
2. Add `get_service_owners(service_names: list[str]) -> dict[str, list[str]]` function
3. Add `aggregate_by_owner(items, service_owners) -> dict[str, OwnerStats]` function

### Phase 2: UI Layer
4. Add "Service Summary (by Owner)" section conditionally (manager mode only)
5. Add click handler to filter and show owner's items

### Data Flow
```
landing_view → is_manager_view() → True
                                      ↓
detailed_items → unique service names → get_service_owners() → service_owner_map
                                      ↓
detailed_items + service_owner_map → aggregate_by_owner() → owner_stats
                                      ↓
                              UI: Owner Summary Treeview
```

## Alternatives Considered

### Alternative 1: Cache Owner Data
- **Pros**: Faster subsequent loads
- **Cons**: Stale data, more complex cache invalidation
- **Decision**: Defer to future iteration

### Alternative 2: Use Action Item's AssignedTo Field
- **Pros**: No additional API calls
- **Cons**: AssignedTo is the person working on it, not the service owner
- **Decision**: Rejected - doesn't match user's mental model

### Alternative 3: Show for All Users
- **Pros**: Simpler logic
- **Cons**: Confusing for ICs who don't have team visibility
- **Decision**: Rejected - only show for managers

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Many API calls slow refresh | Medium | Medium | Parallel fetching with ThreadPoolExecutor |
| Service not found in search | Low | Low | Default to "Unknown Owner" |
| Multi-owner services cause double-counting | Medium | Low | Documented behavior, consistent with S360 |

## Open Questions

1. **Resolved**: How to detect manager vs IC? → Check for TeamGroup in landing view
2. **Resolved**: Where to get owner data? → `search(service_name)` returns Owners field

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| S360 search API | External | Available |
| Existing Treeview components | Internal | Available |
| ThreadPoolExecutor pattern | Internal | Already used for KPI fetching |

## Migration / Rollout Plan

- Feature is additive, no data migration needed
- Enable for all users immediately
- Existing Service Summary and Program Summary unchanged

## Rollback Plan

- Remove the conditional UI section
- No data changes to revert

## Observability Plan

- None (local desktop app)
- Debug logging for owner lookup failures

## Test Strategy Summary

1. **Unit Tests**:
   - `is_manager_view()` with TeamGroup vs Service data
   - `get_service_owners()` with mock search results
   - `aggregate_by_owner()` with sample data

2. **Integration Tests**:
   - Full flow with mocked S360 client

3. **Manual Testing**:
   - Run as IC (brentj) → no owner section
   - Run as manager (muralic) → owner section visible
