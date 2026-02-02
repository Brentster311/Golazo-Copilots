# GCP-0004 Design Document: Workflow Status Display

## Summary

Implement `gcp_status` MCP tool that returns comprehensive workflow state including DoR/DoD status, role instructions, and next steps.

---

## Problem Statement

After init, transition, and mark tools (GCP-0001, 0002, 0003), users need a way to see their overall workflow status at a glance without making multiple tool calls.

---

## Functional Requirements

### FR1: Return Full Status
- Work item ID, profile, phase, role
- DoR/DoD state with completion flags
- Missing items list

### FR2: Include Role Instructions
- Load and return current role instructions

### FR3: Next Steps (Simplified)
- Basic suggestions based on current state

### FR4: No Work Item Handling
- Return clear message if no work item exists

---

## Proposed Approach

### Module Structure
```
golazo_copilot/
??? src/golazo_copilot/
?   ??? tools/
?   ?   ??? gcp_status.py   # NEW
?   ??? server.py           # MODIFY
??? tests/
    ??? test_gcp_status.py  # NEW
```

### Response Schema

```python
{
    "active": True,
    "work_item_id": str,
    "profile": str,
    "current_phase": str,
    "current_role": str,
    "dor": {
        "complete": bool,
        "items": dict[str, bool],
        "missing": list[str]
    },
    "dod": {
        "complete": bool,
        "items": dict[str, bool],
        "missing": list[str]
    },
    "role_instructions": str,
    "next_steps": list[str]
}
```

---

## Dependencies

- GCP-0001: State persistence
- GCP-0002: Phase/role info
- GCP-0003: DoR/DoD checklist logic
