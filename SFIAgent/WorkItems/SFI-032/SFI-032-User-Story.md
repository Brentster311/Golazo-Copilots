# SFI-032: Move org-tree cache into accia-s360 `_build_subtree`

**Status**: IN PROGRESS

## User Story

- **Title**: Move org-tree cache from SFIReporter into accia-s360's `_build_subtree`
- **As a**: developer using the accia-s360 SDK
- **I want**: `GraphEndpoint._build_subtree` to internally cache each subtree by alias (24-hr TTL, file-based) using `S360Config.get_cache_dir()`
- **So that**: any consumer of `get_org_tree()` benefits from caching automatically, and per-subtree caching is more granular than whole-tree caching

- **Out of scope**:
  - Changing the `S360Config` dataclass fields
  - Adding new public API methods to `GraphEndpoint`
  - Changing cache TTL from 24 hours

- **Assumptions**:
  - **Assumption (explicit)**: Cache files stored in `S360Config.get_cache_dir()` (already exists: `LOCALAPPDATA/accia_s360/cache/`). File pattern: `org_tree_{alias}.json`.
  - **Assumption (explicit)**: Respects `config.cache_enabled` flag — if False, no caching.
  - **Assumption (explicit)**: Each subtree is cached individually by alias. Fetching tree for a top-level manager also populates cache entries for every sub-manager in the tree.
  - **Assumption (explicit)**: The serialization format is the same as SFI-031 (OrgTree → nested dict with person + direct_reports).

- **Acceptance Criteria (bulleted, testable)**:
  - [ ] `_build_subtree` checks cache before making Graph API calls; on cache hit (< 24 hr), returns cached subtree without API calls
  - [ ] On cache miss, `_build_subtree` fetches from Graph API and writes the result to cache
  - [ ] `get_org_mapping` in `services.py` no longer contains org-tree cache logic (removed)
  - [ ] When `config.cache_enabled` is False, no caching occurs (API always called)
  - [ ] Existing accia-s360 tests pass unchanged; existing SFIReporter tests pass (including SFI-029, SFI-031 tests)
  - [ ] Stale/corrupt/empty cache files trigger a fresh API call

- **Non-functional requirements**:
  - Atomic writes (temp file + rename)
  - No new external dependencies

- **Telemetry / metrics expected**:
  - DEBUG log: cache HIT/MISS per alias

- **Rollout / rollback notes**:
  - Refactor of SFI-031. Revert by restoring services.py cache code and removing graph.py cache code.
