# SFI-010: Architect Notes

## Architectural Review

### Alignment
The column metadata cache follows the same patterns as the existing user data cache:
- JSON file in `$TEMP/GUI/`
- Load/save functions with error handling
- Clear cache functionality

### Key Contracts Defined

1. **Cache Schema**: TypedDict with version and kpis dict
2. **API Functions**: 6 new functions with clear input/output contracts
3. **Thread Safety**: Atomic writes via temp file + os.replace()

### Security Assessment
- ✅ No sensitive data stored (just column names)
- ✅ Local storage only
- ✅ No network exposure of cache

### Resilience Patterns
- Corrupt cache → return empty cache
- Missing cache → return empty cache
- HTTP 500 with cached columns → remove from cache, retry discovery
- All failures → fall back to static REQUESTED_COLUMNS

### Dependencies
No new dependencies. Uses:
- `json` (stdlib)
- `os` (stdlib)
- `datetime` (stdlib)

### Blast Radius
- **Low**: Cache failures only affect column discovery
- **Fallback**: Static REQUESTED_COLUMNS ensures app always works
- **Rollback**: Delete cache file, app rediscovers

## Approved for Development
Architecture is sound and aligns with existing patterns.
