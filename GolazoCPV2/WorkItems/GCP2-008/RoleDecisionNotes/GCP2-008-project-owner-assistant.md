# GCP2-008: Project Owner Assistant Decision Notes

**Work Item**: GCP2-008 - Configuration System  
**Role**: Project Owner Assistant  
**Date**: 2026-01-31

---

## Work Item Created

During architecture review with the Project Owner, we identified a separation of concerns issue:

**Issue**: Retrospective role suggestions could modify Python source code, leading to divergent forks per user/team.

**Resolution**: Create GCP2-008 to add a configuration system so workflow customizations live in per-repo YAML files, not source code.

---

## Placement in Backlog

| Option | Decision |
|--------|----------|
| Implement before GCP2-001b | Deferred |
| Implement after GCP2-001b | **Selected** |

**Rationale**: GCP2-001a works correctly with hardcoded defaults. GCP2-008 is additive - it makes constants configurable without changing behavior. Safe to defer.

---

## Updated Implementation Order

```
Phase 1: Foundation
  GCP2-003 ? DONE
  GCP2-001a ? DONE
  GCP2-001b ? Next
  GCP2-008 ? After GCP2-001b (config system)

Phase 2: Integration  
  GCP2-001c
  GCP2-001d

Phase 3: IDE Support
  GCP2-005b ? GCP2-005a / GCP2-005c

Phase 4: Enhancements
  GCP2-006 ? GCP2-007
```

---

## Terminology Note

Per Project Owner direction:
- **Project Owner**: The human (user)
- **Project Owner Assistant**: The Golazo role that assists the Project Owner

This terminology must be used consistently across all documentation.
