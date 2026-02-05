# SFI-010: Column Metadata Cache for Dynamic KPI Column Discovery

**Status**: IMPLEMENTED

## User Story

**Title**: Column Metadata Cache for Dynamic KPI Column Discovery

**As a**: SFI Reporter user

**I want**: The app to discover and cache available columns per-KPI, using the cached column list for data fetches

**So that**: 
- Each KPI fetches data with its full set of available columns (not a static curated list)
- S360_ProgramIds is always included for Program Summary functionality
- First-time discovery is transparent (2-pass: discover then fetch)
- Subsequent refreshes are faster (single-pass using cached column metadata)

## Out of Scope
- Column toggle UI (selecting which columns to display) - this is SFI-011
- User-specific column preferences
- Cross-user column sharing
- Column metadata versioning/invalidation

## Assumptions
- **Assumption (explicit)**: The S360 API returns HTTP 500 when requesting all 134+ columns at once, so we must use the portal's approach of requesting a subset
- **Assumption (explicit)**: The "Columns" field in the API response (not AllColumns) represents the KPI's default configured columns that the API can handle
- **Assumption (explicit)**: Column metadata is stable - a KPI's available columns don't change frequently, so caching is safe
- **Assumption (explicit)**: Metadata cache can be stored alongside the existing data cache in `$TEMP/sfireporter/`

## Acceptance Criteria

- [ ] **AC1**: Column metadata cache file exists at `$TEMP/sfireporter/column_metadata.json`
- [ ] **AC2**: When fetching a KPI not in the cache, the app:
  1. Fetches with `columns=[]` to get the "Columns" list from response
  2. Adds essential columns (`S360_ProgramIds`, `url`) if missing
  3. Stores this column list in the metadata cache
  4. Fetches data using the discovered columns
- [ ] **AC3**: When fetching a KPI already in the cache, the app uses cached columns directly (single API call)
- [ ] **AC4**: S360_ProgramIds is always in the column request, ensuring Program Summary works
- [ ] **AC5**: Clear Cache button also clears the column metadata cache
- [ ] **AC6**: Existing tests continue to pass

## Non-Functional Requirements
- Column metadata cache must be separate from user data cache (shared across users)
- Metadata file should be human-readable JSON
- Cache lookup must be thread-safe for parallel KPI fetching

## Telemetry / Metrics Expected
- Log message when column metadata is discovered for a new KPI
- Log message when column metadata is loaded from cache

## Rollout / Rollback Notes
- Rollback: Delete the column_metadata.json file; app will rediscover columns
- No migration needed - cache is additive

---

## Technical Notes

### Problem Analysis
The S360 API has a limitation:
- `AllColumns` returns 134-158 available column names per KPI
- Requesting all 134+ columns causes HTTP 500
- Different KPIs have different default column sets

### HAR File Analysis
The S360 portal handles this by:
1. Each KPI request includes a specific `Columns` array (20-25 columns)
2. Different KPIs request different columns based on their configuration
3. The API's response `Columns` field contains the KPI's configured defaults

### Solution Approach
Use the API's response `Columns` (not AllColumns) as the per-KPI column list:
1. First access: Fetch with `columns=[]`, get response `Columns`, add essentials, cache
2. Subsequent: Load from cache, fetch with cached columns

### Cache Structure
```json
{
  "version": 1,
  "kpis": {
    "<kpi-id>": {
      "columns": ["col1", "col2", ...],
      "discovered_at": "2026-02-04T18:00:00Z"
    }
  }
}
```
