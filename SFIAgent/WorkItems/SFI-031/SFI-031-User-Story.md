# SFI-031: Cache org-tree in `get_org_mapping`

**Status**: IMPLEMENTED

## User Story

- **Title**: Cache the org-tree result inside `get_org_mapping`
- **As a**: SFI Reporter user (manager view)
- **I want**: The `get_org_mapping` function to cache the result of `client.get_org_tree(manager_alias)` to the existing file-based cache and check it before calling the Graph API
- **So that**: Repeated refreshes within a 24-hour window avoid redundant Graph API calls, reducing latency and API load

- **Out of scope**:
  - Changing the top-level `do_refresh` cache (the 1-hour main cache)
  - Exposing a UI control to clear only the org-tree cache
  - In-memory caching layer
  - Changing the `get_org_tree` implementation in `accia-s360`

- **Assumptions**:
  - **Assumption (explicit)**: Cache file stored in the existing `get_cache_dir()` directory (`tempdir/sfireporter/`) using a separate file from the main user-data cache (e.g., `{alias}_org_tree.json`). This avoids coupling with the main 1-hour cache lifecycle.
  - **Assumption (explicit)**: TTL is 24 hours. The org tree changes infrequently (personnel changes are rare day-to-day).
  - **Assumption (explicit)**: An empty/falsy cache result or a cache older than 24 hours triggers a fresh `get_org_tree` call.
  - **Assumption (explicit)**: The cache is keyed by `manager_alias` so different managers don't share stale data.

- **Acceptance Criteria (bulleted, testable)**:
  - [ ] When no org-tree cache file exists, `get_org_mapping` calls `client.get_org_tree()` and writes the result to a JSON cache file
  - [ ] When a valid (< 24 hr) org-tree cache exists, `get_org_mapping` reads from the cache file and does NOT call `client.get_org_tree()`
  - [ ] When the cache is older than 24 hours, `get_org_mapping` calls `client.get_org_tree()` and overwrites the stale cache
  - [ ] When the cache file exists but is empty or contains invalid JSON, `get_org_mapping` falls back to calling `client.get_org_tree()`
  - [ ] When `client.get_org_tree()` raises an exception, behavior is unchanged — all owners mapped to `("Unknown Owner",)` and no corrupt cache is written
  - [ ] Existing unit tests continue to pass with no changes

- **Non-functional requirements**:
  - Cache read/write must be atomic — no partial writes left on crash
  - No new external dependencies

- **Telemetry / metrics expected**:
  - Debug-level log message indicating cache hit vs. miss

- **Rollout / rollback notes**:
  - Internal library change; no user-visible config. Rolling back means reverting the single function change.
