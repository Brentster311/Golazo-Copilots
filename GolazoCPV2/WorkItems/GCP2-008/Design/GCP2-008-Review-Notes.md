# GCP2-008: Architect Review Notes

**Work Item**: GCP2-008 - Configuration System  
**Role**: Architect  
**Date**: 2026-01-31

---

## Review Summary

| Area | Status | Notes |
|------|--------|-------|
| Architectural Alignment | ? Pass | Clean separation |
| APIs and Contracts | ?? Issue | Config mutability |
| Security/Privacy | ? Pass | No secrets in config |
| Scalability | ? Pass | Per-instance loading |
| Dependencies | ? Pass | PyYAML is standard |

**Overall**: Approved with required changes

---

## Architectural Alignment

### Layering
```
???????????????????????????????????????
?     CLI / MCP (future)              ?
???????????????????????????????????????
?     ConsentEnforcer                 ?  ? Uses config via machine
???????????????????????????????????????
?     GolazoStateMachine              ?  ? Receives config
???????????????????????????????????????
?     GolazoConfig                    ?  ? NEW: Loads config
???????????????????????????????????????
?     State Persistence               ?
???????????????????????????????????????
```

? Config sits at foundation level, used by layers above.

---

## Design Issues

### Issue 1: Config Should Be Immutable

**Recommendation**: Use `@dataclass(frozen=True)` or properties without setters.

```python
@dataclass(frozen=True)
class GolazoConfig:
    roles: tuple[str, ...]  # Immutable
    transitions: ...
```

### Issue 2: ConsentEnforcer Config Access

**Design Doc unclear**: How does `ConsentEnforcer` get quality_gates?

**Options**:
1. Pass config to ConsentEnforcer constructor
2. ConsentEnforcer reads from machine._config
3. ConsentEnforcer has its own config reference

**Recommendation**: Option 1 - explicit dependency injection.

```python
class ConsentEnforcer:
    def __init__(self, machine: GolazoStateMachine, config: GolazoConfig = None):
        self._config = config or machine._config
```

### Issue 3: Validation Strategy

**Recommendation**: Lenient loading with warnings, not errors.
- Unknown keys: warn, ignore
- Missing keys: use defaults
- Invalid types: error with clear message

---

## Schema Versioning

Add migration support for future changes:

```python
def _migrate_config(data: dict) -> dict:
    version = data.get("version", "1.0")
    if version == "1.0":
        return data
    # Future: migration logic
    raise ValueError(f"Unknown config version: {version}")
```

---

## Required Changes Before Implementation

| Priority | Change | Rationale |
|----------|--------|-----------|
| **High** | Make GolazoConfig immutable | Prevent accidental mutation |
| **High** | Pass config to ConsentEnforcer | Explicit dependency |
| **Medium** | Add schema version check | Future-proofing |
| **Low** | Warn on unknown keys | User feedback |

---

## Approval

**Status**: ? **Approved with required changes**
