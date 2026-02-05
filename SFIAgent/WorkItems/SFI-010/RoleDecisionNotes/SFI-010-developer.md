# SFI-010: Developer Notes

## Implementation Summary

Successfully implemented column metadata caching for dynamic per-KPI column discovery.

## Changes Made

### 1. `data.py` - Column Cache Infrastructure
Added new functions:
- `get_column_cache_path()` - Returns path to `$TEMP/sfireporter/column_metadata.json`
- `load_column_cache()` - Loads cache with corrupt file handling
- `save_column_cache()` - Atomic writes via temp file + rename
- `get_cached_columns(kpi_id)` - Returns cached columns or None
- `cache_kpi_columns(kpi_id, columns)` - Saves columns with timestamp
- `merge_columns_with_essentials(columns)` - Ensures S360_ProgramIds, url, id are always included

### 2. `data.py` - Modified `get_detailed_action_items()`
Changed from static `REQUESTED_COLUMNS` to dynamic discovery:
- On cache miss: Discovery call → extract identifiers → cache → data call
- On cache hit: Single data call with cached columns

Key fix: The API returns `Columns` as list of objects with `Identifier` field, not strings. Had to extract identifiers: `[col.get("Identifier") for col in columns_raw]`

### 3. `cache.py` - Updated `clear_cache()`
Now also clears `column_metadata.json` when user clicks Clear Cache.

### 4. Constants
- `ESSENTIAL_COLUMNS = ['S360_ProgramIds', 'url', 'id']`
  - `S360_ProgramIds` - Program Summary feature
  - `url` - Hyperlinks in details view
  - `id` - Required by API (HTTP 400 without it)

## TDD Process
1. Wrote 8 column cache tests first (TC01-TC08)
2. Verified tests failed (TDD red)
3. Implemented cache functions
4. Verified tests passed (TDD green)
5. Integrated with `fetch_kpi_grid()`
6. Fixed bugs discovered during integration

## Bugs Fixed During Implementation

### Bug 1: HTTP 500 with AllColumns
**Symptom**: All KPI fetches failed with HTTP 500
**Root Cause**: Requesting all 134+ columns from AllColumns
**Fix**: Use response `Columns` (20-25 columns) instead of `AllColumns`

### Bug 2: HTTP 400 "Invalid request"
**Symptom**: Second API call failed with "should contain at least one or more audience and action item id"
**Root Cause**: `id` column missing from discovered columns
**Fix**: Added `id` to ESSENTIAL_COLUMNS

### Bug 3: Columns as Objects
**Symptom**: Cached columns were objects, not strings
**Root Cause**: `Columns` field contains `[{Identifier: "name", ...}]` not `["name"]`
**Fix**: Extract identifiers: `[col.get("Identifier") for col in columns_raw]`

## Test Results
- 54 tests pass (1 flaky tcl environment failure)
- 9 new tests for column caching

## Verified Behavior
- Fresh cache: 2-pass discovery (30 API calls for 15 KPIs)
- Cached: 1-pass fetch (15 API calls for 15 KPIs)
- Clear Cache removes both data and column caches
- 90 detailed items fetched with dynamic columns
- Program Summary shows 3 programs (S360_ProgramIds working)
