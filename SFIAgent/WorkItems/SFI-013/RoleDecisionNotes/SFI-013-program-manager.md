# SFI-013 Program Manager Notes

## Design Decisions

### Manager Detection Strategy
Chose to detect managers by checking for `TeamGroup` in the landing view response. This is how S360 itself distinguishes managers from ICs - managers get a team group, ICs get individual services.

### Owner Data Source
The `search()` API returns an `Owners` field for each service. This is the most reliable source of ownership data from S360. Alternative was `AssignedTo` field on action items, but that's the person working on the item, not the service owner.

### Performance Consideration
With N services, we need N API calls to look up owners. Mitigated by:
1. Using ThreadPoolExecutor for parallel fetching (pattern already established for KPI fetching)
2. Typical team size is 10-20 services → acceptable latency

### Multi-Owner Handling
Services can have multiple owners. Decided to count items under each owner. This matches user expectation that "my items" includes items I co-own with others.

## Scope Boundaries

### In Scope
- Manager detection
- Service-to-owner mapping via search API
- Aggregation and display
- Drill-down to owner's items

### Explicitly Deferred
- Caching owner data
- Multi-level hierarchy
- Owner vs Contributor distinction

## Risk Assessment

Primary risk is API call volume. For a team with 30 unique services, we'd make 30 additional search() calls. With parallel execution and S360's typical response time (~500ms), this adds ~2-3 seconds.

Acceptable for MVP. Future optimization could cache owner data with TTL.
