# SFI-010: Design Review Comments

## Overall Assessment
✅ **APPROVED** - Design is clear and implementable with minor recommendations.

## Strengths
1. Good insight using `Columns` instead of `AllColumns` - addresses root cause of HTTP 500
2. Cache structure is simple and human-readable
3. Clear fallback strategy if caching fails
4. Essential columns guarantee ensures app functionality

## Recommendations

### R1: Handle Empty Columns Response
**Risk**: Some KPIs might return empty `Columns` array
**Recommendation**: If `Columns` is empty or missing, fall back to `REQUESTED_COLUMNS`

### R2: Add Retry Logic
**Risk**: First API call (discovery) might fail transiently
**Recommendation**: Single retry on discovery failure before falling back to static list

### R3: Cache Versioning
**Status**: Already addressed - version field included in cache format

### R4: Atomic Writes
**Recommendation**: Use write-to-temp-then-rename pattern to prevent corruption on crash

## Questions Addressed

| Question | Answer |
|----------|--------|
| What if `Columns` is empty? | Fall back to static REQUESTED_COLUMNS |
| Thread safety approach? | Atomic file writes (temp + rename) |
| Cache invalidation? | Manual via Clear Cache button |

## Edge Cases to Test

1. **Cache file doesn't exist** → Create new cache
2. **Cache file is corrupted JSON** → Delete and recreate
3. **KPI not in cache** → Discovery flow
4. **Cached columns cause HTTP 500** → Remove from cache, rediscover
5. **API returns empty Columns** → Use static fallback
6. **Concurrent writes** → Atomic writes prevent corruption

## Approved for Implementation
Design is sound. Proceed to Architect and Developer roles.

---

## Architect Notes

### Architectural Alignment
✅ **APPROVED** - Design aligns with existing architecture patterns.

### Data Contracts

**Column Metadata Cache Schema**:
```python
ColumnMetadataCache = TypedDict('ColumnMetadataCache', {
    'version': int,
    'kpis': dict[str, KpiColumnEntry]
})

KpiColumnEntry = TypedDict('KpiColumnEntry', {
    'columns': list[str],
    'discovered_at': str  # ISO 8601 timestamp
})
```

**Essential Columns Contract**:
```python
ESSENTIAL_COLUMNS: list[str] = ['S360_ProgramIds', 'url']
```

### API Contracts

| Function | Input | Output |
|----------|-------|--------|
| `get_column_cache_path()` | None | `str` (absolute path) |
| `load_column_cache()` | None | `ColumnMetadataCache` |
| `save_column_cache(cache)` | `ColumnMetadataCache` | None |
| `get_cached_columns(kpi_id)` | `str` | `list[str]` or `None` |
| `cache_kpi_columns(kpi_id, columns)` | `str`, `list[str]` | None |
| `merge_columns_with_essentials(columns)` | `list[str]` | `list[str]` |

### Security & Privacy
✅ No sensitive data in column metadata cache (just column names)
✅ Cache is local to user's machine ($TEMP)
✅ No credentials or PII stored

### Failure Isolation
- Cache failures must not crash the app
- Fallback to `REQUESTED_COLUMNS` on any cache issue
- Individual KPI failures don't affect others (existing pattern)

### Thread Safety Approach
Use atomic writes with temp file + rename:
```python
def save_column_cache(cache: dict) -> None:
    path = get_column_cache_path()
    temp_path = path + '.tmp'
    with open(temp_path, 'w') as f:
        json.dump(cache, f, indent=2)
    os.replace(temp_path, path)  # Atomic on Windows & POSIX
```

### Implicit Defaults to Surface
- `json.dump` default encoding: UTF-8 ✅ (correct for column names)
- `os.replace` behavior: overwrites existing file atomically ✅

### Recommendations
1. Add type hints to all new functions
2. Use `from __future__ import annotations` for forward references
3. Consider adding `max_age` to cache entries for future invalidation (defer to SFI-011)

