# SFI-009 — Design Document

## Summary
Fetch KPI grid data in parallel using ThreadPoolExecutor to reduce refresh time from ~60s to ~10s.

## Problem Statement
Sequential KPI fetching with 15+ KPIs took 60+ seconds. Each KPI grid fetch is an independent API call — ideal for parallel I/O.

## Proposed Approach
- Use `concurrent.futures.ThreadPoolExecutor` with `MAX_KPI_WORKERS=25` (adjusted from original 8 based on testing)
- Thread-safe progress tracking via `status_lock` + `completed_count` mutable list
- Individual KPI failures caught per-worker — don't abort the batch
- `as_completed()` collects results as they finish

## Test Strategy
- Existing mock-based tests verify `get_detailed_action_items` returns data correctly
- `test_refresh_with_status_callback` verifies progress messages flow through
