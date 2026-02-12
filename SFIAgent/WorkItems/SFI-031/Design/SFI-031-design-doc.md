# SFI-031 Design Doc — Cache org-tree in `get_org_mapping`

## Summary
Add a 24-hour file-based cache for the `client.get_org_tree()` call inside `get_org_mapping()` in `services.py`. The cache reuses the existing `get_cache_dir()` infrastructure and is keyed by `manager_alias`.

## Problem Statement
Every time `do_refresh()` runs for a manager, `get_org_mapping()` calls `client.get_org_tree(manager_alias)` which makes a Graph API call that recursively fetches the entire org hierarchy. This is slow (~2-5s) and the data changes infrequently (org transfers are rare). Caching the result avoids redundant API calls within 24 hours.

## Business Case
- **Why now**: Manager view refresh is the most common user action; removing a multi-second API call improves the experience noticeably.
- **Impact**: Faster refresh for managers (skip the slowest single API call on cache hit).
- **KPIs**: Org-tree cache hit rate (logged at DEBUG level).

## Stakeholders
- SFI Reporter end users (managers using the desktop app)

## Functional Requirements
1. Before calling `client.get_org_tree()`, check for a cached org-tree file for the given `manager_alias`.
2. If cache exists and is < 24 hours old, deserialize and use it (skip API call).
3. If cache is missing, empty, corrupted, or > 24 hours old, call `get_org_tree()` and write the result to cache.
4. Cache file: `{cache_dir}/{manager_alias}_org_tree.json` with a `timestamp` field.

## Non-Functional Requirements
- No new dependencies.
- Atomic writes (write to temp, rename) to avoid partial/corrupt files.
- Existing tests must pass unchanged.

## Proposed Approach
1. Add two private functions in `services.py`:
   - `_read_org_tree_cache(manager_alias)` → returns deserialized `OrgTree` or `None`
   - `_write_org_tree_cache(manager_alias, tree)` → serializes `OrgTree` to JSON with timestamp
2. Modify `get_org_mapping()` to call `_read_org_tree_cache` before `client.get_org_tree()`, and `_write_org_tree_cache` on a fresh fetch.
3. `OrgTree` / `OrgPerson` serialization: convert the recursive dataclass to nested dicts for JSON, and reconstruct on read.

## Alternatives Considered
- **In-memory caching**: Rejected — app restarts lose the cache, and the desktop app is frequently restarted.
- **Extend main cache**: The main user-data cache has a 1-hour TTL. Coupling the org tree to it would force more frequent refetches. Separate file is cleaner.

## Risks & Mitigations
| Risk | Mitigation |
|------|-----------|
| Stale org tree (employee transfers) | 24-hr TTL limits staleness; acceptable trade-off |
| Corrupt cache file | Validation on read + fallback to API call |
| Disk write failure | `try/except` around write; log warning, proceed without cache |

## Dependencies
- `accia-s360` `OrgTree` / `OrgPerson` dataclasses (read-only dependency for ser/deser)
- Existing `cache.py` for `get_cache_dir()`

## Migration / Rollout / Rollback
- No migration needed. Cache files are created on first use.
- Rollback: revert the function change; stale cache files are harmless (ignored).

## Observability
- `logger.debug("Org-tree cache HIT for %s (age: %d min)", ...)`
- `logger.debug("Org-tree cache MISS for %s — fetching from Graph API", ...)`

## Test Strategy
- Unit tests mocking `client.get_org_tree`, `get_cache_dir`, and filesystem ops.
- Test cache hit path (no API call).
- Test cache miss path (API called, file written).
- Test stale cache path (API called, file overwritten).
- Test corrupt/empty cache file (fallback to API).
- Test API failure (no cache written, existing error behavior preserved).
