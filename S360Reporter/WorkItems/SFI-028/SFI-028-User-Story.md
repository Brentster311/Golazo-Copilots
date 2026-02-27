# SFI-028 — Replace S360 Search Chain-Walking with MS Graph Org API in S360Reporter

**Status**: IMPLEMENTED

## User Story

- **Title**: Use MS Graph Org Hierarchy in S360Reporter's Owner Grouping
- **As a**: S360Reporter user (manager view)
- **I want**: the owner-to-org-hierarchy mapping to use the new `get_manager_chain()` from accia-s360's Graph API (SFI-027) instead of parallel S360 `search()` calls
- **So that**: multi-level owner grouping is accurate and doesn't suffer from the S360 chain-walking bugs (wrong manager_alias extraction, rate limiting, "Unknown Owner" for multi-team managers)

- **Out of scope**:
  - Changes to the accia-s360 library (already done in SFI-027)
  - Changes to OrgAncestry NamedTuple or aggregate_by_owner/aggregate_by_level2 signatures
  - Changes to cache serialization format 
  - UI layout changes

- **Assumptions**:
  - **Assumption (explicit)**: Interface is Tkinter desktop GUI (existing S360Reporter). No new interface.
  - **Assumption (explicit)**: Target platform is Windows (PyInstaller .exe). Existing.
  - **Assumption (explicit)**: Data persistence uses existing JSON file cache. No changes to cache format.
  - **Assumption (explicit)**: Users are technical (Microsoft managers viewing SFI data).
  - **Assumption (explicit)**: `get_client()` returns `S360Client` which now has `get_manager_chain()` available from SFI-027.
  - **Assumption (explicit)**: S360 `search()` calls for service owner lookup (`get_service_owners`) remain unchanged — only the org hierarchy resolution changes.
  - **Assumption (explicit)**: Owner names from S360 service data may not match Graph `display_name` exactly — matching should be done by alias when possible.

## Acceptance Criteria (bulleted, testable)

- [x] **AC-1**: `get_org_mapping()` uses `client.get_manager_chain(owner_alias)` instead of `client.search(owner_name)` for hierarchy resolution. No more S360 Managers JSON chain parsing.
- [x] **AC-2**: All existing OrgAncestry outputs remain the same: `OrgAncestry(level1, level2)` with the same semantics (level1 = viewer's direct report, level2 = sub-report or None).
- [x] **AC-3**: The `_resolve_display_name()` inner function is replaced with Graph API data (`OrgPerson.display_name`) — no more search-based name resolution.
- [x] **AC-4**: All 30 existing SFI-026 unit tests pass (TestGetOrgMappingMultiLevel updated to Graph API mocks; all other test classes unchanged).
- [x] **AC-5**: PyInstaller build succeeds and produces working .exe.

## Non-functional requirements
- Graph API calls should be parallelized per-owner (ThreadPoolExecutor) as before
- Status callback updates should continue to report progress

## Telemetry / metrics expected
- Logging at INFO for each Graph API call (handled by accia-s360 library)
- Existing owner lookup progress messages maintained

## Rollout / rollback notes
- Rollout: Rebuild PyInstaller .exe with updated tk_app.py
- Rollback: Revert tk_app.py to previous version (S360 chain-walking)
