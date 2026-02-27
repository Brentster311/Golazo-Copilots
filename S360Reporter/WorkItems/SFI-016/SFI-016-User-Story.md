# SFI-016 — Singleton Client & KPI Failure Retry

**Status**: IMPLEMENTED

## User Story

- **Title**: Singleton S360Client with KPI Failure Notification & Retry
- **As a**: S360Reporter desktop user
- **I want**: The app to reuse a single API client (avoiding redundant Azure token fetches) and to notify me when individual KPI fetches fail, offering a retry for just the failed ones
- **So that**: Refreshes are faster, I see fewer token-related log noise, and I don't lose visibility into partial failures during data fetch

## Out of Scope
- Retry logic for non-KPI API calls (service list, action item summary)
- Automatic retry without user interaction
- Persistent retry queue across sessions

## Assumptions
- **Assumption (explicit)**: The S360Client is thread-safe for concurrent read operations — confirmed by prior usage with 25 parallel workers.
- **Assumption (explicit)**: The existing tkinter UI is the target — no interface type question needed (established in prior work items).
- **Assumption (explicit)**: Windows desktop platform — established in prior items.
- **Assumption (explicit)**: Data is in-memory + JSON file cache — established pattern.

## Acceptance Criteria
- [ ] `get_client()` returns the same `S360Client` instance across all calls within a session (singleton)
- [ ] `get_detailed_action_items()` returns both successful rows and a list of failed KPIs with error details
- [ ] When KPI fetches fail, the UI displays an orange warning listing the failed KPI names
- [ ] A "Retry Failed KPIs" button appears only when there are failures
- [ ] Clicking retry fetches only the failed KPI IDs and merges recovered rows into the existing data
- [ ] All existing tests pass (84 tests) with updated mocks for the new return signature

## Non-Functional Requirements
- Singleton pattern must not break test isolation (tests reset the instance)
- Failed KPI list must be thread-safe (shared across worker threads)

## Telemetry / Metrics
- `logger.warning` emitted for each failed KPI during fetch
- `logger.info` emitted when retry succeeds or reports remaining failures
- All events written to rotating log file at `%TEMP%/GUI/sfi_reporter.log`

## Rollout / Rollback Notes
- Requires exe rebuild after code changes
- No database migrations or config changes needed
- Rollback: revert the 4 changed files
