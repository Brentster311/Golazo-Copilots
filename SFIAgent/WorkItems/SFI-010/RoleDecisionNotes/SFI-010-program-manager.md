# SFI-010: Program Manager Notes

## Design Decisions

### 1. Use `Columns` not `AllColumns`

The key insight from HAR file analysis: the API response includes two column fields:
- `AllColumns`: Full list of 134-158 possible columns
- `Columns`: The KPI's configured default columns (20-25)

The S360 portal uses specific column sets per-KPI. The response `Columns` field tells us what columns the API is actually configured to return for each KPI.

### 2. Separate Cache File

Column metadata is not user-specific - all users see the same columns for the same KPI. Therefore, we use a separate `column_metadata.json` file that's shared, rather than embedding in each user's data cache.

### 3. Two-Pass Discovery

On cache miss, we need two API calls:
1. `columns=[]` → Get response with `Columns` metadata
2. `columns=[discovered + essentials]` → Get actual data

This is acceptable because:
- Only happens once per KPI
- Subsequent refreshes are single-pass
- Background refresh makes this transparent

### 4. Essential Columns Guarantee

Always add these to any column request, even if not in discovered columns:
- `S360_ProgramIds` - Required for Program Summary
- `url` - Required for hyperlinks

This ensures core app functionality works regardless of KPI configuration.

## Sequencing

1. **Phase 1**: Create cache infrastructure (load/save functions)
2. **Phase 2**: Integrate with `fetch_kpi_grid()` 
3. **Phase 3**: Update Clear Cache to clear both caches
4. **Phase 4**: Add tests

## Fallback Strategy

If cached columns cause HTTP 500 (e.g., API changed):
1. Log warning
2. Clear that KPI from cache
3. Retry with discovery
4. If still fails, fall back to static REQUESTED_COLUMNS

This ensures the app remains functional even if the caching strategy has issues.
