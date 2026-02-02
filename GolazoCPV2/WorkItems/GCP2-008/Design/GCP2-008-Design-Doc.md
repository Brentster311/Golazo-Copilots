# GCP2-008: Configuration System - Design Document

**Work Item**: GCP2-008  
**Version**: 1.0  
**Created**: 2026-01-31  
**Author**: Program Manager

---

## Summary

Implement a `GolazoConfig` class that loads workflow configuration from a YAML file, providing sensible defaults when no file exists. Refactor `GolazoStateMachine` to read roles, transitions, and DoR/DoD items from config rather than hardcoded constants.

---

## Problem Statement

Current `machine.py` has hardcoded:
- `VALID_ROLES` - list of valid roles
- `TRANSITIONS` - role transition matrix
- `DOR_ITEMS` / `DOD_ITEMS` - checklist items
- `QUALITY_GATE_ROLES` - roles requiring warnings

Teams cannot customize without forking the package.

---

## Business Case

### Why Now?
Before CLI (GCP2-001c) and MCP (GCP2-001d), we need configuration so those layers can expose config options.

**Blocking**: Should complete before GCP2-007 (Workflow Profiles) which defines profile-specific overrides.

### Impact
| Metric | Before | After |
|--------|--------|-------|
| Customization | Fork package | Edit YAML |
| Maintenance | Divergent forks | Single package |
| Onboarding | Understand code | Edit config |

---

## Requirements

### Functional Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| FR-1 | `GolazoConfig` class with `load()` method | AC-1 |
| FR-2 | Defaults when no config file | AC-2 |
| FR-3 | `GolazoStateMachine` uses config | AC-3 |
| FR-4 | Config schema documented | AC-4 |

### Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1 | Config loading | < 50ms |
| NFR-2 | Clear error messages | Human-readable |

---

## Proposed Approach

### High-Level Design

```
???????????????????????????????????????????????????????????????
?                    GolazoConfig                             ?
???????????????????????????????????????????????????????????????
? + roles: list[str]                                          ?
? + transitions: dict[str, list[str]]                         ?
? + dor_items: list[str]                                      ?
? + dod_items: list[str]                                      ?
? + quality_gate_roles: list[str]                             ?
? + role_to_phase: dict[str, str]                             ?
???????????????????????????????????????????????????????????????
? + load(base_path) ? GolazoConfig                            ?
? + _find_config_file(base_path) ? Path | None                ?
? + _apply_defaults(data) ? dict                              ?
???????????????????????????????????????????????????????????????
           ?
           ? reads
           ?
    golazo.yaml (optional)
```

### Config File Locations (Priority Order)

1. `{base_path}/golazo.yaml`
2. `{base_path}/.golazo/config.yaml`
3. Fall back to defaults

### Config Schema

```yaml
# golazo.yaml
version: "1.0"

roles:
  - project-owner
  - program-manager
  - tester
  - architect
  - developer
  - refactor-expert
  - builder
  - documentor

phases:
  design:
    roles: [project-owner, program-manager, tester, architect]
  development:
    roles: [developer, refactor-expert, builder, documentor]

transitions:
  project-owner: [program-manager]
  program-manager: [tester]
  tester: [architect]
  architect: [developer]
  developer: [refactor-expert]
  refactor-expert: [builder]
  builder: [documentor]
  documentor: []

dor:
  items:
    - userStory
    - designDoc
    - reviewComments
    - testCases

dod:
  items:
    - branchCreated
    - testsWrittenFirst
    - testsPass
    - buildPasses
    - docsUpdated
    - refactorComplete
    - committed

quality_gates:
  - tester
  - architect
```

### Default Values

When no config file exists, use current hardcoded values:

```python
DEFAULT_CONFIG = {
    "version": "1.0",
    "roles": [
        "project-owner", "program-manager", "tester", "architect",
        "developer", "refactor-expert", "builder", "documentor"
    ],
    "transitions": {
        "project-owner": ["program-manager"],
        "program-manager": ["tester"],
        # ... current values
    },
    "dor": {"items": ["userStory", "designDoc", "reviewComments", "testCases"]},
    "dod": {"items": ["branchCreated", "testsWrittenFirst", ...]},
    "quality_gates": ["tester", "architect"],
}
```

---

## Implementation Phases

| Phase | Deliverable | Description |
|-------|-------------|-------------|
| 1 | `GolazoConfig` class | Config loading with defaults |
| 2 | Refactor `machine.py` | Use config instead of constants |
| 3 | Refactor `consent.py` | Use config for quality gates |
| 4 | Tests | Config loading + integration |

---

## Migration Strategy

### Backward Compatibility
- No config file = current behavior (defaults)
- Existing tests pass without changes
- Config is additive, not breaking

### Refactoring `machine.py`

**Before:**
```python
VALID_ROLES = ["project-owner", ...]

class GolazoStateMachine:
    def can_transition(self, target):
        if target not in VALID_ROLES:
            return (False, "Unknown role")
```

**After:**
```python
class GolazoStateMachine:
    def __init__(self, work_item_id, config=None, ...):
        self._config = config or GolazoConfig.load(base_path)
    
    def can_transition(self, target):
        if target not in self._config.roles:
            return (False, "Unknown role")
```

---

## Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| JSON config | Ubiquitous | No comments | Rejected |
| TOML config | Clean syntax | Less familiar | Rejected |
| YAML config | Comments, familiar | Dependency | **Selected** |
| Environment vars | Simple | Not structured | Rejected |

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Invalid YAML | Medium | Low | Clear error messages |
| Missing PyYAML | Low | Medium | Add to dependencies |
| Config drift | Low | Medium | Schema versioning |

---

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| GCP2-001a (State Machine) | Upstream | ? Complete |
| PyYAML | External | Add to pyproject.toml |

**Downstream dependents**:
- GCP2-007 (Profiles) - uses config for profile definitions
- GCP2-001c (CLI) - may expose config commands

---

## File Location

```
src/golazo/
??? __init__.py
??? state.py      # GCP2-003 (existing)
??? machine.py    # GCP2-001a (modify)
??? consent.py    # GCP2-001b (modify)
??? config.py     # GCP2-008 (new)
```
