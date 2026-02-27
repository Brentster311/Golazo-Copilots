# SFI-010: Quality Assurance Notes

## Review Summary

Reviewed User Story and Design Doc. Both are clear and implementable.

## Key Decisions

### 1. Fallback to Static List
If the API returns empty `Columns` or cached columns cause HTTP 500, fall back to the existing `REQUESTED_COLUMNS` static list. This ensures the app always works.

### 2. Test-First Approach
Defined 8 test cases covering:
- Cache file operations (create, load, save, corrupt recovery)
- Essential columns guarantee
- Clear cache integration
- Existing test regression

### 3. Edge Cases Identified
- Empty Columns response
- Corrupt JSON cache file
- Concurrent thread access
- HTTP 500 with cached columns

## Test Coverage

| Category | Count |
|----------|-------|
| Unit tests | 6 |
| Integration tests | 2 |
| Manual tests | 5 |

## Risks Mitigated

1. **Cache corruption**: Test for corrupt JSON, recover gracefully
2. **Missing essential columns**: Always merge with ESSENTIAL_COLUMNS
3. **Clear Cache incomplete**: Test that metadata cache is also cleared

## Approved for Development
Test cases are complete and map to acceptance criteria.
