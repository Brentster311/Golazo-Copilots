# SFI-026 — Multi-Level Owner Grouping in Services Table

**Status**: BACKLOG — Implementation reverted (2026-02-10). Root cause fix for multi-team manager_alias extraction did not hold in production. Will restart.

## User Story

- **Title**: Extend Services Table from 1-Level to N-Level Hierarchical Owner Grouping
- **As a**: skip-level manager (e.g. alexhowells) viewing SFI Reporter
- **I want**: the Services table to group services by my direct reports, and under each direct report further group by *their* direct reports (sub-grouping)
- **So that**: I can see a clear two-level org hierarchy in the services table instead of every service being lumped under "Unknown Owner" or flattened into a single level
- **Out of scope**:
  - Grouping deeper than 2 levels (3+ nesting)
  - Changes to the KPI Trends or Action Items tables
  - Changes to the Streamlit web UI — Tkinter desktop only
  - New S360 API endpoints or authentication changes
  - Changing how IC (non-manager) views render — they stay flat
- **Assumptions**:
  - **Assumption (explicit)**: The S360 management-chain API (`/api/v2/user/{alias}`) already returns the full chain from any owner up to the CEO, so no new API calls are needed — just different traversal logic. This was confirmed during SFI-013 implementation.
  - **Assumption (explicit)**: A "2-level manager" is someone whose directs also have directs. The viewer (e.g. alexhowells) is at the top, their directs (e.g. muralic) form level 1, and muralic's directs form level 2.
  - **Assumption (explicit)**: When the viewer is only 1 level deep (e.g. muralic), behavior is unchanged — the current 1-level grouping continues to work as-is.
  - **Assumption (explicit)**: The `is_manager_view` detection (line ~780 in `do_refresh()`) already correctly identifies both 1-level and 2-level managers, so no changes are needed there.

## Acceptance Criteria (bulleted, testable)

- [ ] **AC-1**: When alexhowells (a 2-level manager) views the Services table, services are grouped under Level-1 parent rows (👤 direct reports like muralic), each expandable to reveal Level-2 sub-rows (👤 muralic's directs), which in turn expand to show individual services.
- [ ] **AC-2**: When muralic (a 1-level manager) views the Services table, the existing 1-level grouping behavior is fully preserved — direct reports shown as parent rows with services nested directly beneath.
- [ ] **AC-3**: When brentj (an IC / non-manager) views the Services table, the flat list behavior is fully preserved — no grouping rows appear.
- [ ] **AC-4**: Owner parent rows at both levels display the correct aggregated counts (total action items, SLA violations, invalid ETAs) rolled up from their children.
- [ ] **AC-5**: Double-clicking a Level-1 or Level-2 owner row drills into the Action Items table filtered to services owned by that subtree.
- [ ] **AC-6**: Double-clicking a leaf service row continues to drill into that specific service's action items (existing behavior preserved).
- [ ] **AC-7**: No regression in the "Unknown Owner" bucket — services whose owners can't be resolved to the org hierarchy are still grouped under "Unknown Owner" at the top level.

## Non-functional Requirements

- Management-chain lookups should remain parallelized (currently 8 workers in `get_org_mapping()`); adding a second level must not serialize lookups or significantly increase refresh time.
- The treeview must remain responsive — no blocking the Tkinter event loop during hierarchy computation.
- Memory footprint increase should be negligible (storing one extra level of mapping data).

## Telemetry / Metrics Expected

- No new telemetry required. Existing refresh-time logging covers the additional computation.

## Rollout / Rollback Notes

- **Rollout**: Ship as part of next SFI Reporter PyInstaller build. No config changes needed — the algorithm auto-detects hierarchy depth.
- **Rollback**: Revert to previous build. No data migration or config cleanup needed.

---

## Technical Context (from research)

### Current Algorithm (1-Level)
1. `do_refresh()` calls `get_org_mapping(manager_alias, owner_aliases)` (lines 283-400 of tk_app.py)
2. For each owner, the function queries the S360 management-chain API to get their full chain
3. It finds `manager_alias` in the chain, then maps the owner to the person **immediately after** `manager_alias` in the chain — this is the direct-report ancestor
4. This creates a flat `{owner_alias → direct_report_alias}` mapping that collapses the entire org to 1 level
5. `aggregate_by_owner()` rolls up stats using this mapping
6. `_update_tables()` inserts parent rows (👤 direct report) with child rows (services) in the treeview

### What Needs to Change for 2-Level
1. **`get_org_mapping()`** must return **two levels of ancestry** when the viewer is 2+ levels deep. Instead of mapping every owner to a single direct-report ancestor, it should return a structure like `{owner_alias → (level1_ancestor, level2_ancestor)}` where level1 is the viewer's direct and level2 is the sub-report under that direct.
2. **`aggregate_by_owner()`** must produce two-tier rollup stats — totals per level-1 ancestor and per level-2 ancestor.
3. **`_update_tables()`** must insert a 3-tier treeview: Level-1 parent → Level-2 parent → service rows.
4. **`_on_service_double_click()`** must handle drill-down for both Level-1 and Level-2 owner rows.

### Prior Work Items
- **SFI-013**: Original 1-level grouping implementation
- **SFI-014**: Bug fixes — "Unknown Owner" appearing for manager's own items, service drill-down filter fix
