# SFI-031 — Project Owner Assistant Decision Notes

## Work Item
**ID**: SFI-031
**Title**: Cache org-tree in `get_org_mapping`

## Decisions Made

1. **Interface type**: Library-internal change. The `get_org_mapping` function in `services.py` is modified — no new UI, CLI, or API surface.
2. **Data persistence**: Reuse existing file-based cache directory (`get_cache_dir()` → `tempdir/sfireporter/`). Separate file from the main user cache to avoid coupling lifecycles.
3. **Cache TTL**: 24 hours (time-based only). The user confirmed no on-demand invalidation is needed for this cache.
4. **Staleness handling**: Empty cache or cache older than 24 hrs → call `get_org_tree`. No manual refresh invalidation.
5. **Scope**: Single user story — the change is contained to one function, one file, one concern.
6. **Profile**: User requested express profile. Work item was created with complete; will move through roles efficiently.

## Alternatives Considered

- **In-memory caching**: Rejected by user. App restarts are common (desktop Tkinter app), so in-memory-only wouldn't survive restarts.
- **Combined memory + file**: Rejected; file-only is sufficient for the cadence of use.
- **Invalidation on manual Refresh**: User chose time-based only. The main `do_refresh` already handles full data refresh; the org tree is a slow-changing structure.

## Risks

- **Stale org tree**: If an employee transfers orgs, the cached tree will be stale for up to 24 hrs. Acceptable trade-off per user.
- **Disk space**: Org tree JSON files are small (a few KB). No concern.
