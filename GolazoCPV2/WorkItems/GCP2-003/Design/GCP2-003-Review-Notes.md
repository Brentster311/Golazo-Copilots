# GCP2-003: Architect Review Notes

**Work Item**: GCP2-003 - Structured State Management  
**Role**: Architect  
**Date**: 2026-01-27

---

## Review Summary

| Area | Status | Notes |
|------|--------|-------|
| Architectural Alignment | ? Pass | Simple, focused module with clear boundaries |
| APIs and Contracts | ? Pass | Schema well-defined; API surface minimal |
| Security/Privacy | ? Pass | Local files only; no sensitive data exposure |
| Scalability | ? Pass | Per-work-item files scale well |
| Resilience | ?? Minor | Add handling for partial writes |
| Dependencies | ? Pass | Standard library only |

**Overall**: Approved with minor recommendations

---

## Architectural Alignment

### Boundaries
- ? Clear boundary: State module only handles persistence
- ? No business logic in state layer (state machine is GCP2-001a)
- ? Single responsibility: read/write JSON state files

### Integration Points
- **Upstream**: None (foundational)
- **Downstream**: GCP2-001a (State Machine), GCP2-005 (IDE Extensions), GCP2-006 (Multi-Session)

### Layering
```
???????????????????????????????????????
?     GCP2-001a (State Machine)       ?  ? Business logic
???????????????????????????????????????
?     GCP2-003 (State Persistence)    ?  ? This module (data access)
???????????????????????????????????????
?     File System (JSON files)        ?  ? Storage
???????????????????????????????????????
```

**Assessment**: Clean separation. State module should NOT contain transition logic.

---

## APIs and Data Contracts

### Schema Contract
The JSON schema is well-defined. Explicit contract:

| Field | Type | Required | Default |
|-------|------|----------|---------|
| schemaVersion | string | Yes | "1.0" |
| workItemId | string | Yes | - |
| profile | string | Yes | "complete" |
| currentPhase | string | Yes | "design" |
| currentRole | string | Yes | "project-owner" |
| createdAt | ISO8601 | Yes | Now |
| updatedAt | ISO8601 | Yes | Now |
| dor | object | Yes | All false |
| dod | object | Yes | All false |
| roleHistory | array | Yes | [] |
| deviations | array | Yes | [] |

### API Contract
```python
# Input/Output contracts
load(work_item_id: str) -> State | None  # Returns None if not found
save(state: State) -> None               # Raises on failure
create(work_item_id: str, profile: str = "complete") -> State
exists(work_item_id: str) -> bool
```

**Recommendation**: Add explicit exception types:
- `StateNotFoundError`
- `StateCorruptedError`
- `StateSaveError`

---

## Security and Privacy

### Data Sensitivity
- ? No credentials stored in state
- ? No PII in state fields
- ? Work item IDs are not sensitive
- ? Local file storage (no network exposure)

### File Permissions
- ?? **Question**: Should state files have restricted permissions?
- **Assessment**: Not critical for single-user local tool. Standard file permissions sufficient.

### Injection Risks
- ? No SQL/command injection (file-based)
- ?? `workItemId` used in file path - validate to prevent path traversal
- **Recommendation**: Sanitize `workItemId` - reject characters like `..`, `/`, `\`

---

## Scalability and Resilience

### Scalability
- ? Per-work-item files: O(1) access per work item
- ? No contention between work items
- ? File system handles thousands of small files well

### Resilience

#### Failure Modes
| Failure | Impact | Mitigation |
|---------|--------|------------|
| File not found | Low | Return None, allow create |
| Corrupted JSON | Medium | Log error, offer to recreate |
| Disk full | Medium | Clear error message |
| Partial write | Medium | **Atomic write recommended** |

#### Atomic Writes
**Recommendation**: Use write-to-temp-then-rename pattern:
```python
def save(state: State) -> None:
    temp_path = state_path.with_suffix('.tmp')
    temp_path.write_text(json.dumps(...))
    temp_path.rename(state_path)  # Atomic on most file systems
```

This prevents corrupted state files from interrupted writes.

---

## Dependency Choices

| Dependency | Assessment |
|------------|------------|
| json | ? Standard library, stable |
| dataclasses | ? Standard library, appropriate for DTOs |
| pathlib | ? Standard library, cross-platform |
| datetime | ? Standard library, use ISO8601 format |

**No external dependencies** - excellent for a foundational module.

---

## Failure Isolation

- ? State file corruption affects only one work item
- ? Invalid state doesn't crash agent (defensive loading)
- ? Clear error messages with file paths

---

## Implicit Assumptions Surfaced

| Assumption | Question for PO | Default Behavior |
|------------|-----------------|------------------|
| JSON encoding | UTF-8 only? | `json.dumps` defaults to ASCII with escapes |
| Timestamp format | Always UTC? | Python datetime can be naive or aware |
| File overwrite | No confirmation? | Direct overwrite on save |
| Missing fields on load | Fail or use defaults? | Need to decide |

**Recommendations**:
1. Explicitly use `ensure_ascii=False` for proper Unicode
2. Always use UTC with `datetime.utcnow()` or `timezone.utc`
3. On load with missing fields: use defaults + log warning
4. On save: overwrite without confirmation (expected behavior)

---

## Architectural Decisions

### Decision 1: Dataclass vs TypedDict
**Decided**: Use `@dataclass` for State
- Provides type hints
- Supports default values
- Easy to serialize/deserialize

### Decision 2: Path Resolution
**Decided**: Relative to project root
- State path: `WorkItems/<id>/state.json`
- Project root determined by presence of `WorkItems/` directory or `.github/`

### Decision 3: Schema Migration Strategy
**Decided**: Version check on load
```python
if state["schemaVersion"] != CURRENT_VERSION:
    state = migrate(state)
```

---

## Recommendations Summary

| Priority | Recommendation | Rationale |
|----------|----------------|-----------|
| Medium | Atomic writes (temp + rename) | Prevent corruption on interrupted saves |
| Medium | Sanitize workItemId for path safety | Prevent path traversal |
| Low | Explicit exception types | Better error handling by consumers |
| Low | UTF-8 encoding explicit | Consistent Unicode handling |

---

## New User Stories Required

None. The recommendations above are implementation details within scope.

---

## Approval

**Status**: ? **Approved with recommendations**

The design is sound, well-bounded, and appropriate for the use case. Minor recommendations do not block implementation.
