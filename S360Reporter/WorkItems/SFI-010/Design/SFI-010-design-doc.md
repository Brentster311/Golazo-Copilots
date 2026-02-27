# SFI-010: Design Document - Column Metadata Cache

## Summary

Implement a local JSON cache for KPI column metadata that enables dynamic per-KPI column discovery while avoiding the S360 API's HTTP 500 error when requesting too many columns.

## Problem Statement

The S360 API has contradictory behaviors:
1. **AllColumns** returns 134-158 available column names per KPI
2. Requesting all these columns causes **HTTP 500**
3. Different KPIs have different default column configurations

The current solution uses a static curated list of 32 columns, which works but doesn't capture all available data per-KPI. The S360 portal handles this by requesting specific column sets per-KPI.

## Business Case

**Why now**: Users expect full data parity with S360 portal. The current static column list may miss KPI-specific columns.

**Impact**: 
- Better data completeness per-KPI
- Faster subsequent refreshes (single API call vs two)
- Foundation for column toggle UI (SFI-011)

**KPIs**:
- Cache hit rate after initial discovery
- Time saved on subsequent refreshes

## Stakeholders

- **End Users**: Benefit from more complete data per-KPI
- **Developer**: Simpler maintenance than static column list

## Functional Requirements

| ID | Requirement |
|----|-------------|
| FR1 | Store column metadata in separate cache file from user data |
| FR2 | On cache miss: discover columns, add essentials, cache, fetch |
| FR3 | On cache hit: use cached columns directly |
| FR4 | Always include S360_ProgramIds and url in column requests |
| FR5 | Clear Cache button clears both data cache and metadata cache |

## Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR1 | Metadata cache must be thread-safe for parallel KPI fetching |
| NFR2 | Cache file must be human-readable JSON |
| NFR3 | Cache operations must not block UI thread |

## Proposed Approach

### Cache Structure

```
$TEMP/GUI/
├── {alias}_cache.json          # Existing user data cache
└── column_metadata.json        # NEW: Shared column metadata cache
```

### Cache File Format

```json
{
  "version": 1,
  "kpis": {
    "09c3aade-339c-403b-b1c1-33b4526768ee": {
      "columns": ["id", "title", "dueDate", ...],
      "discovered_at": "2026-02-04T18:00:00Z"
    }
  }
}
```

### Discovery Flow

```
fetch_kpi_grid(kpi_id):
    cached = load_cached_columns(kpi_id)
    if cached:
        columns = cached + ESSENTIAL_COLUMNS  
        return fetch_with_columns(kpi_id, columns)
    else:
        # Discovery: fetch with empty columns to get defaults
        response = fetch_with_columns(kpi_id, [])
        discovered_columns = response["Columns"]  # NOT AllColumns
        save_to_cache(kpi_id, discovered_columns)
        columns = discovered_columns + ESSENTIAL_COLUMNS
        return fetch_with_columns(kpi_id, columns)  # Second call with discovered columns
```

### Key Insight

Use the response's `Columns` field (not `AllColumns`):
- `AllColumns`: All possible columns (134+) - causes HTTP 500
- `Columns`: The KPI's configured default columns (20-25) - API can handle

### Thread Safety

Use a global lock for cache file access:
- Read operations: shared lock
- Write operations: exclusive lock

Or use atomic file writes with temp file + rename.

## Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| Keep static REQUESTED_COLUMNS | Simple, works | May miss KPI-specific columns | Reject |
| Use AllColumns with chunking | Gets all data | Complex, many API calls | Reject |
| Use response Columns + cache | Simple, per-KPI | Requires 2-pass on first use | **Accept** |

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Cached columns become invalid | Low | Medium | Clear Cache provides manual invalidation |
| Race condition on cache writes | Medium | Low | Use atomic writes or locking |
| API changes column behavior | Low | Medium | Fallback to static list if cache columns fail |

## Open Questions

1. ~~Should we version the cache format?~~ Yes, include "version" field
2. ~~Should cache be per-user or global?~~ Global, column metadata is not user-specific

## Dependencies

- Existing cache infrastructure in `data.py`
- Existing `get_action_items_grid()` API wrapper

## Migration / Rollout / Rollback

**Rollout**: 
- Cache is created on first use
- No migration needed

**Rollback**:
- Delete `column_metadata.json`
- App will rediscover columns on next refresh
- Can also fall back to static REQUESTED_COLUMNS if needed

## Observability Plan

- Log: "Discovering columns for KPI {name}..." on cache miss
- Log: "Using cached columns for KPI {name}" on cache hit
- Log: "Column metadata cache saved with {n} KPIs"

## Test Strategy

1. **Unit Tests**:
   - `test_load_column_cache_empty` - returns empty dict when no cache
   - `test_save_and_load_column_cache` - roundtrip save/load
   - `test_essential_columns_always_included` - S360_ProgramIds and url are always in request

2. **Integration Tests**:
   - Mock API: first call returns Columns, second uses them
   - Clear cache clears both files

3. **Manual Tests**:
   - Fresh start: verify 2-pass discovery
   - Second refresh: verify single-pass with cache
   - Clear Cache: verify column_metadata.json is deleted
