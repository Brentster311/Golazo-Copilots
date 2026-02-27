# SFI-016 — Design Document

## Summary
Introduce a singleton `S360Client` pattern and a "Retry Failed KPIs" UI feature to improve resilience and user visibility during KPI data fetching in S360Reporter.

## Problem Statement
Two issues exist in the KPI fetch pipeline:

1. **Redundant token acquisition**: `get_client()` creates a new `S360Client()` on every call. With 25 parallel KPI workers, this means 25+ calls to `az account get-access-token`, producing excessive log noise and unnecessary latency.
2. **Silent KPI failures**: When individual KPI grid fetches fail (timeout, transient API error), the rows are silently dropped. The user sees a smaller dataset with no indication that data is missing.

## Business Case
- **Why now**: Users reported confusing logs full of repeated token messages and missing KPI data without explanation.
- **Impact**: Every refresh is affected — this is the hot path.
- **KPIs**: Reduced token acquisition calls from ~25 to 1 per refresh; zero-to-one user-visible failure notifications.

## Stakeholders
- S360Reporter end users (Microsoft engineers using S360 dashboards)
- S360Reporter maintainers

## Functional Requirements
1. `get_client()` returns the same instance for the lifetime of the process
2. `get_detailed_action_items()` returns `(rows, failed_kpis)` tuple
3. Failed KPIs list contains `{kpi_id, kpi_name, error}` dicts
4. UI shows orange warning banner listing failed KPI names
5. "Retry Failed KPIs" button appears only when failures exist
6. Retry fetches only the failed KPI IDs, not all KPIs
7. Recovered rows merge into existing cached data
8. If retry still fails, button remains visible with updated failure list

## Non-Functional Requirements
- Thread safety: `failed_kpis` list protected by existing `status_lock`
- Test isolation: Singleton resets via `_client_instance = None` in test fixtures
- No new dependencies

## Proposed Approach

### Component 1: Singleton Client (`data.py`)
- Add module-level `_client_instance: Any = None`
- `get_client()` checks `_client_instance is None` before creating new instance
- Simple, no locking needed (Python GIL protects single assignment)

### Component 2: Failed KPI Tracking (`data.py`)
- Change `get_detailed_action_items()` return type to `tuple[list[dict], list[dict]]`
- In the worker function, catch exceptions per-KPI and append to thread-safe `failed_kpis` list
- Return `(rows, failed_kpis)` at the end

### Component 3: Retry UI (`tk_app.py`)
- Add `self.retry_btn` (hidden by default) to controls frame
- `_on_refresh_complete()` checks if `failed_kpis` is non-empty, shows button + warning
- `_on_retry_failed()` runs retry in background thread using only failed KPI IDs
- `_on_retry_complete()` merges recovered rows, recomputes stats, updates UI

### Component 4: Test Updates
- `test_data.py`: autouse fixture resets `_client_instance = None`
- `test_tk_app.py`: update `mock_detailed.return_value` from `[]` to `([], [])`

## Alternatives Considered
| Alternative | Why Rejected |
|---|---|
| Auto-retry without user action | Users may want to investigate failures; silent retry hides problems |
| Connection pooling instead of singleton | Overkill for a desktop app with one user |
| Retry all KPIs | Wasteful; only failed ones need re-fetch |

## Risks & Mitigations
| Risk | Mitigation |
|---|---|
| Singleton persists stale credentials across long sessions | Azure SDK handles token refresh internally |
| Retry merges stale data | Retry uses same audience_ids/kpi_names from original fetch |
| Breaking change to return type | All callers updated; tests verify new signature |

## Dependencies
- No new packages
- Existing `accia-s360` library, `threading.Lock`

## Migration / Rollout / Rollback
- **Rollout**: Rebuild exe, redistribute zip
- **Rollback**: Revert 4 files, rebuild exe
- **No data migration**: Cache format unchanged

## Observability
- `logger.warning` per failed KPI
- `logger.info` on retry success/failure
- All in existing rotating log at `%TEMP%/GUI/sfi_reporter.log`

## Test Strategy
- Unit tests for singleton reset isolation
- Unit tests for tuple return type
- Mock-based tests for `do_refresh` unpacking
- Manual verification of retry button behavior
