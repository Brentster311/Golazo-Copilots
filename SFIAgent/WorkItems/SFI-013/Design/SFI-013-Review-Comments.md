# SFI-013 Review Comments

## Design Review

### Clarity and Completeness ✅
- Design clearly explains the data flow from landing view to owner aggregation
- Functional requirements are well-defined with FR1-FR5

### Feasibility and Sequencing ✅
- Phased approach (Data Layer → UI Layer) is appropriate
- Reuses existing patterns (ThreadPoolExecutor, SortableTreeview)

### Risk Coverage ✅
- API call volume risk identified with mitigation
- Unknown owner fallback defined
- Multi-owner behavior documented

### Recommendations

#### R1: Consider Batch Optimization (Low Priority)
The design calls for N search API calls for N services. Consider if S360 has a batch endpoint. 
- **Impact**: Performance improvement
- **Decision**: Accept as-is for MVP, optimize later if needed

#### R2: Clarify "Self" Handling
User story mentions "Self grouping for services owned by the logged-in user." Design should specify how to match current user to owner names.
- **Impact**: May need to parse user display name
- **Recommendation**: Use `get_default_landing_view()` which returns user info, or match against cached `user_alias`

#### R3: Error Handling for Search Failures
Design mentions "Unknown Owner" fallback but should specify:
- What if search returns empty results?
- What if search returns multiple services with same name?
- **Recommendation**: First result with Group='Service' wins, empty = Unknown Owner

### Edge Cases to Consider

1. **Service with no owners**: Owners field is null/empty → "No Owner"
2. **Service not found**: Search returns no matching service → "Unknown Service"
3. **User is both manager and IC**: Has TeamGroup AND owns services → Show owner section
4. **Empty team**: Manager with no action items → Show empty owner section with message

### Operability ✅
- No on-call impact (local desktop app)
- Debug logging planned for failures

### Naming Clarity ✅
- Function names are descriptive: `is_manager_view()`, `get_service_owners()`, `aggregate_by_owner()`

## Approval

✅ **Design Approved** with above recommendations noted for implementation.

---

## Architect Notes

### Architectural Alignment ✅
- Design follows existing patterns in the codebase
- New functions are isolated and testable
- UI changes are additive, not modifying existing components

### API and Data Contracts

#### Input Contracts
- `is_manager_view(landing_view: list[dict]) -> bool`
  - Input: List of SearchDataList items from `get_default_landing_view()`
  - Output: True if any item has `Group == "TeamGroup"`

- `get_service_owners(service_names: list[str], client: S360Client) -> dict[str, list[str]]`
  - Input: List of unique service names
  - Output: Dict mapping service name to list of owner names
  - Error: Empty list on lookup failure (no exceptions propagated)

- `aggregate_by_owner(items: list[dict], service_owners: dict[str, list[str]]) -> dict[str, OwnerStats]`
  - Input: Detailed action items, service-to-owner mapping
  - Output: Dict mapping owner name to stats (count, sla, invalid_eta)
  - Special keys: "Unknown Owner" (missing from map), "No Owner" (empty owners list)

### Security and Privacy ✅
- No new data stored or transmitted
- Uses existing authenticated S360 client
- Owner names are already visible in S360 web UI (no new exposure)

### Scalability Consideration
- N API calls for N services is O(N) complexity
- Parallel execution mitigates latency impact
- For very large teams (50+ services), consider caching in future iteration

### Dependency Choices ✅
- No new dependencies
- Reuses ThreadPoolExecutor (already in codebase)
- Reuses S360Client, SortableTreeview, DetailModal

### Failure Isolation ✅
- Owner lookup failures don't block main refresh
- Individual service lookup failures gracefully degrade to "Unknown Owner"
- UI displays regardless of partial failures

### Implicit Behaviors Reviewed

1. **JSON Parsing**: Owners field is a JSON string `"[\"Name\"]"` - must `json.loads()` it
2. **Threading**: ThreadPoolExecutor max_workers should match existing KPI fetch pattern (8)
3. **Search API**: May return multiple results - need to filter by `Group == "Service"`

### Rollback Safety ✅
- Feature is additive, can be disabled by removing conditional UI section
- No data migration or schema changes

### Approval

✅ **Architecturally Approved** - Design is sound and follows established patterns.

