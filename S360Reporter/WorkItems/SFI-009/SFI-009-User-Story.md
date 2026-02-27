# SFI-009: Parallel KPI Data Fetching

**Status**: IMPLEMENTED

## User Story

- **Title**: Parallel KPI Data Fetching for Faster Refresh
- **As a**: Security engineer using the S360Reporter
- **I want**: KPI data to be fetched in parallel during refresh
- **So that**: Data refresh completes faster (currently 15+ KPIs take ~60+ seconds sequentially)

## Out of Scope

- Caching individual KPI responses
- Retry logic for failed KPIs (current behavior: skip and continue)
- Progress bar (keep status updates showing which KPIs are being fetched)

## Assumptions

- **Assumption (explicit)**: Existing Tkinter desktop application
- **Assumption (explicit)**: Use Python's `concurrent.futures.ThreadPoolExecutor` for I/O-bound parallelism
- **Assumption (explicit)**: S360 API can handle concurrent requests (no rate limiting observed)
- **Assumption (explicit)**: Max 8 concurrent workers to avoid overwhelming the API

## Acceptance Criteria

- [ ] KPI grid fetches run in parallel using ThreadPoolExecutor
- [ ] Status updates show aggregate progress (e.g., "Fetching KPIs: 5/15 complete")
- [ ] All existing functionality preserved (data correctness, error handling)
- [ ] Refresh time reduced by at least 50% for users with multiple KPIs
- [ ] All existing tests continue to pass

## Non-functional Requirements

- Thread-safe status callback invocation
- Graceful handling of individual KPI failures (don't fail entire refresh)

## Telemetry / Metrics Expected

- None required

## Rollout / Rollback Notes

- No breaking changes, performance improvement only
