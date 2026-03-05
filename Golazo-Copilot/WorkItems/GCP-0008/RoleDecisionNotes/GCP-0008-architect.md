# GCP-0008: Architect Decision Notes

**Note**: This document was created retroactively to complete the artifact trail.

## Architecture Review

- Profile is immutable after creation
- Profile configuration centralized in core module
- Tools query profile to determine enforcement

## Profile Definitions

```python
PROFILES = {
    "complete": {...},  # All roles, all gates
    "express": {...},   # Reduced roles, optional reviewComments
    "spike": {...}      # Minimal, no DoR gate
}
```

## Approved

Design provides appropriate flexibility without compromising governance.
