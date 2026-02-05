# SFI-013 Test Cases

## Test Strategy

Tests follow TDD principles - written before production code. Focus on unit testing the new functions with mocked S360 responses.

---

## TC1: Manager Detection

### TC1.1: is_manager_view returns True for TeamGroup
**Input**: Landing view with `[{"Group": "TeamGroup", "Id": "xxx", "Name": "Team"}]`
**Expected**: `is_manager_view()` returns `True`

### TC1.2: is_manager_view returns False for Services
**Input**: Landing view with `[{"Group": "Service", "Id": "xxx", "Name": "Svc"}]`
**Expected**: `is_manager_view()` returns `False`

### TC1.3: is_manager_view returns False for empty list
**Input**: Landing view with `[]`
**Expected**: `is_manager_view()` returns `False`

### TC1.4: is_manager_view handles mixed groups
**Input**: Landing view with both TeamGroup and Service entries
**Expected**: `is_manager_view()` returns `True` (TeamGroup takes precedence)

---

## TC2: Service Owner Lookup

### TC2.1: get_service_owners parses single owner
**Input**: Service name "TestService", search returns `{"Owners": "[\"John Doe\"]"}`
**Expected**: `{"TestService": ["John Doe"]}`

### TC2.2: get_service_owners parses multiple owners
**Input**: Service name "TestService", search returns `{"Owners": "[\"John Doe\",\"Jane Smith\"]"}`
**Expected**: `{"TestService": ["John Doe", "Jane Smith"]}`

### TC2.3: get_service_owners handles null owners
**Input**: Service name "TestService", search returns `{"Owners": null}`
**Expected**: `{"TestService": []}`

### TC2.4: get_service_owners handles empty search results
**Input**: Service name "TestService", search returns `[]`
**Expected**: `{"TestService": []}` (empty owners)

### TC2.5: get_service_owners handles search exception
**Input**: Service name "TestService", search raises exception
**Expected**: `{"TestService": []}` (graceful fallback)

---

## TC3: Owner Aggregation

### TC3.1: aggregate_by_owner groups single-owner items
**Input**: 
- Items: `[{S360_ServiceId: "svc1", ...}, {S360_ServiceId: "svc1", ...}]`
- Owners: `{"svc1": ["Brent Jensen"]}`
**Expected**: `{"Brent Jensen": {count: 2, sla: X, invalid_eta: Y}}`

### TC3.2: aggregate_by_owner handles multi-owner services
**Input**: 
- Items: `[{S360_ServiceId: "svc1", SlaType: "OutOfSLA"}]`
- Owners: `{"svc1": ["Owner A", "Owner B"]}`
**Expected**: Both owners get count=1, sla=1

### TC3.3: aggregate_by_owner handles unknown service
**Input**: 
- Items: `[{S360_ServiceId: "unknown", ...}]`
- Owners: `{}` (service not in map)
**Expected**: `{"Unknown Owner": {count: 1, ...}}`

### TC3.4: aggregate_by_owner handles empty owners list
**Input**: 
- Items: `[{S360_ServiceId: "svc1", ...}]`
- Owners: `{"svc1": []}` (no owners)
**Expected**: `{"No Owner": {count: 1, ...}}`

### TC3.5: aggregate_by_owner calculates SLA correctly
**Input**: 
- Items: 3 items for owner, 1 OutOfSLA, 1 invalid ETA
- Owners mapped correctly
**Expected**: `{owner: {count: 3, sla: 1, invalid_eta: 1}}`

---

## TC4: Integration / UI (Manual)

### TC4.1: IC user does not see owner section
**Steps**: Run app as `brentj`, observe UI
**Expected**: No "Service Summary (by Owner)" section visible

### TC4.2: Manager user sees owner section
**Steps**: Run app as `muralic`, observe UI
**Expected**: "Service Summary (by Owner)" section visible with team member names

### TC4.3: Owner drill-down shows filtered items
**Steps**: Click on an owner name in the summary
**Expected**: DetailModal opens with only that owner's items

### TC4.4: Owners sorted by count
**Steps**: Observe owner section ordering
**Expected**: Highest item count first

---

## Test Coverage Summary

| Acceptance Criteria | Test Cases |
|---------------------|------------|
| AC1: Manager detection | TC1.1, TC1.2, TC1.3, TC1.4 |
| AC2: Grouped stats | TC3.1, TC3.2, TC3.5 |
| AC3: Drill-down | TC4.3 |
| AC4: Sorted by count | TC4.4 |
| AC5: IC no section | TC4.1 |

All acceptance criteria have test coverage.
