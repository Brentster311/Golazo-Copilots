# SFI-013 Project Owner Assistant Notes

## Request Analysis

The user requested:
> "I would like #3 but specifically, the service summary should group by the owner of the service, where that owner is either the person we are investigating or one of their directs."

## Investigation Findings

### S360 API Capabilities
1. **`get_default_landing_view(alias)`**: Returns `TeamGroup` for managers, `Service` list for ICs
2. **`search(service_name)`**: Returns `Owners` field with list of owner names (e.g., `["Brent Jensen"]`)
3. **`query_people_hierarchy(audience)`**: Shows manager chain (e.g., `muralic_team` → `stzuehls_team`)

### Data Flow Discovery
- When viewing as `muralic` (a manager), S360 returns a `TeamGroup` instead of individual services
- The TeamGroup contains action items across all services owned by Murali's team
- Each action item has `S360_ServiceId` and `S360_ServiceTreeServiceName`
- We can call `search(service_name)` to get the `Owners` field for each service

### Example Data
```
brentj services:
  Azure Core Customer Insights and Analytics → Owners: ["Brent Jensen"]
  
muralic team services (from action items):
  Albus_GF_ AIOps Service → Owners: ["Ze Li","Ken Hsieh",...]
  TeamEuler → Owners: ["Rohit Pandey"]
```

## Scope Decisions

### In Scope
- New "Service Summary (by Owner)" section in UI
- Grouping services by owner name from S360 `Owners` field
- Aggregate stats per owner (count, SLA, invalid ETA)
- Drill-down to owner's items

### Out of Scope (Deferred)
- Caching owner data (increases complexity)
- Multi-level hierarchy (directs of directs)
- Owner vs Contributor distinction

## Checklist Verification

- [x] **Interface type**: Existing Tkinter desktop app (confirmed from context)
- [x] **Target platform**: Windows (existing app)
- [x] **Data persistence**: In-memory only for owner mapping (cache already exists for items)
- [x] **User type**: Technical (developers/managers viewing their team's SFI status)

## Story Sizing

Single story is appropriate:
- One user-observable outcome: new grouped summary section
- 5 acceptance criteria (within 3-7 limit)
- Can be independently implemented and tested
