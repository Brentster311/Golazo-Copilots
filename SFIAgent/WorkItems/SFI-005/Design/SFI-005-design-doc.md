# SFI-005 — Design Document

## Summary
Add real-time status messages during data fetch so users know the app isn't frozen.

## Problem Statement
During refresh, the app makes multiple sequential API calls (services, action items, KPI grids) taking 10-60+ seconds. Without progress feedback, users assume the app has hung.

## Proposed Approach
- Pass an `on_status` callback through `do_refresh()` → `get_user_team_info()` → `get_detailed_action_items()`
- Each phase updates the status bar: "Connecting...", "Retrieved N services", "Fetching KPIs: X/Y complete"
- Status updates happen on the calling thread; UI updates via `root.after()` for thread safety

## Alternatives Considered
| Alternative | Why Rejected |
|---|---|
| Progress bar with percentage | Harder to calculate total; status text is sufficient |
| Spinner animation | Less informative than text messages |

## Test Strategy
- `test_refresh_with_status_callback`: verify callback receives ≥2 messages including "Connecting"
