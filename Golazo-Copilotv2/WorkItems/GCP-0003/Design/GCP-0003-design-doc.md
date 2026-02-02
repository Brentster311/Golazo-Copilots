# GCP-0003 Design Document: DoR/DoD Checklist Management

## Summary

Implement `gcp_mark_dor` and `gcp_mark_dod` MCP tools to mark checklist items as complete, enabling DoR gate enforcement for `gcp_transition`.

---

## Problem Statement

With `gcp_init` (GCP-0001) and `gcp_transition` (GCP-0002), users can initialize and move between roles. However, they cannot mark DoR items complete, so the DoR gate at `developer` always blocks.

**GCP-0003** solves: How does a user mark DoR/DoD items as complete?

---

## Business Case

### Why Now
- GCP-0002 DoR gate requires DoR items to be markable
- Without this, workflow is blocked at architect?developer

### Impact
- Enables full workflow progression
- Provides audit trail of checklist completion

---

## Functional Requirements

### FR1: Mark Single DoR Item
- Accept item name and complete flag
- Update state.dor[item] = complete
- Update updatedAt timestamp

### FR2: Mark Single DoD Item
- Same as FR1 for DoD items

### FR3: Bulk Update (Simplified)
- Accept dict of {item: complete} pairs
- Update all specified items

### FR4: Item Validation
- Reject unknown item names with clear error
- List valid items in error message

### FR5: Unmarking Support
- Allow setting complete=false
- Return warning about gate implications

### FR6: Status Return
- Return current checklist state after update
- Include overall "complete" flag (all items true)
- List missing items

---

## Non-Functional Requirements

### NFR1: Performance
- Completes in <50ms

### NFR2: Consistency
- Atomic state updates

---

## Proposed Approach

### Module Structure
```
golazo_copilot/
??? src/golazo_copilot/
?   ??? core/
?   ?   ??? checklists.py     # NEW: Validation logic
?   ??? tools/
?   ?   ??? gcp_mark_dor.py   # NEW
?   ?   ??? gcp_mark_dod.py   # NEW
?   ??? server.py             # MODIFY: Add tools
??? tests/
    ??? test_gcp_mark.py      # NEW
```

### Valid Items

```python
VALID_DOR_ITEMS = {"userStory", "designDoc", "reviewComments", "testCases"}
VALID_DOD_ITEMS = {"branchCreated", "testsWrittenFirst", "testsPass", 
                   "buildPasses", "docsUpdated", "refactorComplete", "committed"}
```

### Response Schema

```python
{
    "success": True,
    "checklist": "dor",
    "item_updated": "userStory",
    "new_value": True,
    "complete": False,  # All items done?
    "items": {
        "userStory": True,
        "designDoc": False,
        ...
    },
    "missing": ["designDoc", "reviewComments", "testCases"]
}
```

---

## Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| Per-item timestamps | Better audit | Schema change, complexity | **Deferred** |
| Combined tool | Single tool | Less clear API | **Rejected** |
| Separate tools | Clear separation | More code | **Accepted** |

---

## Test Strategy

### Unit Tests
- Mark single item
- Mark multiple items (bulk)
- Reject invalid item
- Unmark item with warning
- Complete flag calculation
- No active work item error

---

## Dependencies

### Internal
- GCP-0001: State persistence
- GCP-0002: Uses DoR status for gate (integration)
