# SFI-010: Project Owner Assistant Notes

## Request Analysis

The user requested a column metadata caching solution after the dynamic column discovery approach failed. Key observations:

1. **API Limitation**: The S360 API returns HTTP 500 when requesting all 134+ columns from AllColumns
2. **Portal Behavior**: HAR file analysis showed the S360 portal uses per-KPI column sets (20-25 columns each)
3. **Response Columns**: The API response includes a `Columns` field with the KPI's default configured columns

## Scope Decision

This work item focuses only on the **caching infrastructure**:
- Creating the column metadata cache
- Two-pass discovery on cache miss
- Single-pass fetch on cache hit
- Ensuring essential columns (S360_ProgramIds, url) are always included

The **column toggle UI** (ability to select/deselect columns for display) is explicitly out of scope and will be SFI-011.

## Key Assumptions Made

1. **Use `Columns` not `AllColumns`**: The response `Columns` field contains what the API can actually handle, while `AllColumns` is just metadata about what columns exist
2. **Stable Column Sets**: KPI column configurations don't change frequently, making caching viable
3. **Shared Cache**: Column metadata is not user-specific - all users share the same cache file

## Essential Columns

These must always be requested regardless of cache:
- `S360_ProgramIds` - Required for Program Summary feature
- `url` - Required for hyperlinks in details view

## Questions Answered (from prior context)

- **Interface type**: Tkinter desktop app (established in prior work items)
- **Target platform**: Windows (established in prior work items)
- **Data persistence**: Local JSON files in $TEMP/GUI/ (established pattern)
- **User type**: Technical (developers viewing their SFI action items)

## Risk Assessment

- **Low Risk**: Cache invalidation - columns rarely change, and Clear Cache provides manual invalidation
- **Low Risk**: Thread safety - will use file locking or atomic writes
- **Medium Risk**: API behavior may vary - need to handle case where cached columns cause HTTP 500 (fallback to rediscovery)
