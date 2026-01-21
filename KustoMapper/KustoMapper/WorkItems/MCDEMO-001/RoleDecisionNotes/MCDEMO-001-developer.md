# Developer Decision Notes: MCDEMO-001

## Date: Retrospective Documentation
## Role: Developer

---

## Decisions Made

### 1. Model Implementation
**Decision**: Use Python dataclasses for `TableInfo` and `ColumnInfo`
**Rationale**: Clean, minimal boilerplate, built-in `__init__`, `__eq__`, `__repr__`.

### 2. Adapter Base Class
**Decision**: Create abstract `DataSourceAdapter` base class
**Rationale**: Allows future adapters (SQL, Cosmos, etc.) to share interface.

### 3. Error Wrapping
**Decision**: Catch exceptions and wrap with user-friendly messages
**Rationale**: Raw exceptions from azure-identity/accia are not user-friendly.

### 4. Cache Directory Structure
**Decision**: Use MD5 hash of cluster URL + sanitized database name
**Rationale**: Prevents filesystem issues with special characters in URLs.

### 5. Serialization
**Decision**: Implement `to_dict()` / `from_dict()` on models
**Rationale**: Simple, explicit, no external serialization library needed.

## Alternatives Considered

| Option | Considered | Reason Not Chosen |
|--------|------------|-------------------|
| Pydantic models | Yes | Dataclasses are simpler, fewer dependencies |
| pickle for cache | Yes | JSON is human-readable, portable |
| attrs library | Yes | Dataclasses are built-in |

## Tradeoffs Accepted

1. **No type hints everywhere**: Some methods lack full type annotations
2. **datetime.utcnow() deprecation**: Using deprecated method (warning in Python 3.12+)

## Known Limitations

1. `datetime.utcnow()` is deprecated - should use `datetime.now(UTC)` in future
2. No connection pooling
3. No retry logic for transient failures

## Files Modified/Created

- `src/kustomapper/models/schema.py` - Data models
- `src/kustomapper/adapters/base.py` - Abstract base class
- `src/kustomapper/adapters/kusto_adapter.py` - Kusto implementation
- `src/kustomapper/cache/schema_cache.py` - Caching layer
- `tests/test_*.py` - Test files

## Outcome
Implementation complete, all tests passing (22/22).
