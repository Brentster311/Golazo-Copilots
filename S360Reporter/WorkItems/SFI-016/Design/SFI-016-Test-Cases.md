# SFI-016 — Test Cases

## Mapping: Acceptance Criteria → Test Cases

### AC1: Singleton `get_client()`
| ID | Test | Expected | Type |
|----|------|----------|------|
| TC-01 | Call `get_client()` twice without reset | Same object identity (`is`) | Unit |
| TC-02 | Reset `_client_instance = None`, call `get_client()` | New instance created | Unit |
| TC-03 | Autouse fixture resets singleton between tests | Each test gets a fresh mock | Unit (fixture) |

### AC2: Tuple return from `get_detailed_action_items()`
| ID | Test | Expected | Type |
|----|------|----------|------|
| TC-04 | Call with valid KPIs, all succeed | `(rows, [])` — empty failed list | Unit |
| TC-05 | Call with one failing KPI | `(partial_rows, [{"kpi_id":…, "kpi_name":…, "error":…}])` | Unit |
| TC-06 | Call with all KPIs failing | `([], [failed1, failed2, …])` | Unit |

### AC3: Orange warning in UI
| ID | Test | Expected | Type |
|----|------|----------|------|
| TC-07 | `_on_refresh_complete` with non-empty `failed_kpis` | Status bar shows orange warning with KPI names | Manual/Integration |

### AC4: Retry button visibility
| ID | Test | Expected | Type |
|----|------|----------|------|
| TC-08 | Refresh with zero failures | Retry button hidden (`pack_forget`) | Manual/Integration |
| TC-09 | Refresh with failures | Retry button visible | Manual/Integration |

### AC5: Retry fetches only failed KPIs
| ID | Test | Expected | Type |
|----|------|----------|------|
| TC-10 | Click retry after 2/10 KPIs failed | Only 2 KPI IDs passed to `get_detailed_action_items` | Manual |

### AC6: Tests pass with updated mocks
| ID | Test | Expected | Type |
|----|------|----------|------|
| TC-11 | `test_refresh_success` | `mock_detailed.return_value = ([], [])` — passes | Unit |
| TC-12 | `test_refresh_with_status_callback` | Same tuple mock — passes | Unit |
| TC-13 | `test_handle_missing_azure_cli` | Singleton reset — returns `None` | Unit |
| TC-14 | `test_fetch_user_services` | Singleton reset — returns 2 services | Unit |
| TC-15 | `test_fetch_action_items` | Singleton reset — returns dict with `SummaryList` | Unit |
| TC-16 | `test_handle_api_timeout` | Singleton reset — returns `{}` on timeout | Unit |
| TC-17 | Full suite: `pytest GUI/tests/ -v` | 84 passed, 0 failed | Integration |

## Test Execution Plan
1. Run `python -m pytest GUI/tests/ -v --tb=short --rootdir=GUI`
2. Verify 84 passed, 0 failed
3. Manual: Launch app, trigger refresh, verify retry button behavior with real API
