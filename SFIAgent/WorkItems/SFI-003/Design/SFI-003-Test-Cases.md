# SFI-003 Test Cases

## Test Strategy
- **Approach:** TDD - tests written before implementation
- **Framework:** pytest for unit tests, manual for UI tests
- **Coverage Target:** 80% for data and cache modules

---

## Test Categories

### 1. User Detection Tests

#### TC-001: Auto-detect user from Azure CLI
```python
def test_auto_detect_user(mocker):
    """Verify user alias is auto-detected from Azure CLI credentials."""
    mock_client = mocker.patch('sfi_reporter.data.S360Client')
    mock_client.return_value.get_current_user.return_value.alias = 'brentj'
    
    from sfi_reporter.data import get_current_user_alias
    
    alias = get_current_user_alias()
    assert alias == 'brentj'
```
- **Type:** Unit test (mocked)
- **Priority:** P0
- **Expected:** Returns user alias from S360Client

#### TC-002: Handle missing Azure CLI
```python
def test_handle_missing_azure_cli(mocker):
    """Verify clear error when Azure CLI is not available."""
    mock_client = mocker.patch('sfi_reporter.data.S360Client')
    mock_client.side_effect = Exception("Azure CLI not found")
    
    from sfi_reporter.data import get_current_user_alias
    
    result = get_current_user_alias()
    assert result is None or 'error' in str(result).lower()
```
- **Type:** Unit test (mocked)
- **Priority:** P0
- **Expected:** Returns None or error indicator

---

### 2. Data Fetching Tests

#### TC-003: Fetch services for user
```python
def test_fetch_user_services(mocker):
    """Verify services are fetched for given user."""
    mock_client = mocker.patch('sfi_reporter.data.S360Client')
    mock_client.return_value.get_default_landing_view.return_value = {
        'SearchDataList': [
            {'Id': 'svc1', 'Name': 'Service A', 'Group': 'Service'},
            {'Id': 'svc2', 'Name': 'Service B', 'Group': 'Service'},
        ]
    }
    
    from sfi_reporter.data import get_user_services
    
    services = get_user_services('brentj')
    assert len(services) == 2
    assert services[0]['Name'] == 'Service A'
```
- **Type:** Unit test (mocked)
- **Priority:** P0
- **Expected:** Returns list of services

#### TC-004: Fetch action items for services
```python
def test_fetch_action_items(mocker):
    """Verify action items are fetched for given services."""
    mock_client = mocker.patch('sfi_reporter.data.S360Client')
    mock_client.return_value.get_action_items.return_value = [
        {'id': 'ai1', 'kpiName': 'KPI 1', 'dueDate': '2026-03-01'},
        {'id': 'ai2', 'kpiName': 'KPI 2', 'dueDate': '2026-04-01'},
    ]
    
    from sfi_reporter.data import get_action_items
    
    items = get_action_items(['svc1', 'svc2'])
    assert len(items) == 2
```
- **Type:** Unit test (mocked)
- **Priority:** P0
- **Expected:** Returns list of action items

#### TC-005: Handle API timeout
```python
def test_handle_api_timeout(mocker):
    """Verify timeout is handled gracefully."""
    mock_client = mocker.patch('sfi_reporter.data.S360Client')
    mock_client.return_value.get_action_items.side_effect = TimeoutError()
    
    from sfi_reporter.data import get_action_items
    
    items = get_action_items(['svc1'])
    assert items == [] or items is None
```
- **Type:** Unit test (mocked)
- **Priority:** P1
- **Expected:** Returns empty list, does not crash

---

### 3. Cache Tests

#### TC-006: Cache write and read
```python
def test_cache_write_and_read(tmp_path):
    """Verify data can be cached and retrieved."""
    from sfi_reporter.cache import write_cache, read_cache
    
    data = {'items': [{'id': 1}], 'timestamp': '2026-02-04T10:00:00'}
    
    write_cache('brentj', data, cache_dir=tmp_path)
    result = read_cache('brentj', cache_dir=tmp_path)
    
    assert result == data
```
- **Type:** Unit test
- **Priority:** P0
- **Expected:** Cache round-trip works

#### TC-007: Cache expiration
```python
def test_cache_expiration(tmp_path, mocker):
    """Verify cache is considered expired after 1 hour."""
    from sfi_reporter.cache import is_cache_valid
    from datetime import datetime, timedelta
    
    # Create cache from 2 hours ago
    old_time = datetime.now() - timedelta(hours=2)
    data = {'timestamp': old_time.isoformat()}
    
    result = is_cache_valid(data)
    assert result is False
```
- **Type:** Unit test
- **Priority:** P0
- **Expected:** Returns False for expired cache

#### TC-008: Cache valid within 1 hour
```python
def test_cache_valid(tmp_path):
    """Verify cache is valid within 1 hour."""
    from sfi_reporter.cache import is_cache_valid
    from datetime import datetime
    
    data = {'timestamp': datetime.now().isoformat()}
    
    result = is_cache_valid(data)
    assert result is True
```
- **Type:** Unit test
- **Priority:** P0
- **Expected:** Returns True for fresh cache

#### TC-009: Handle corrupted cache
```python
def test_corrupted_cache(tmp_path):
    """Verify corrupted cache is handled gracefully."""
    from sfi_reporter.cache import read_cache
    
    cache_file = tmp_path / 'brentj_cache.json'
    cache_file.write_text('not valid json {{{')
    
    result = read_cache('brentj', cache_dir=tmp_path)
    assert result is None
```
- **Type:** Unit test
- **Priority:** P1
- **Expected:** Returns None, does not crash

---

### 4. UI Acceptance Tests (Manual)

#### TC-010: Application launches successfully
- **Steps:**
  1. Run `streamlit run src/sfi_reporter/app.py`
  2. Observe browser opens
- **Expected:** Application displays without errors
- **Type:** Manual
- **Priority:** P0

#### TC-011: User alias auto-populated
- **Steps:**
  1. Launch application
  2. Observe user text box
- **Expected:** Text box contains current user's alias
- **Type:** Manual
- **Priority:** P0

#### TC-012: Change user and refresh
- **Steps:**
  1. Clear text box
  2. Enter different alias (e.g., "gowrin")
  3. Click Refresh button
- **Expected:** Table updates with new user's items
- **Type:** Manual
- **Priority:** P0

#### TC-013: Loading state displayed
- **Steps:**
  1. Click Refresh
  2. Observe UI while loading
- **Expected:** Spinner or "Loading..." message shown
- **Type:** Manual
- **Priority:** P1

#### TC-014: Empty state displayed
- **Steps:**
  1. Enter alias with no services
- **Expected:** "No action items found" message displayed
- **Type:** Manual
- **Priority:** P1

---

## Test Execution Plan

| Phase | Tests | Method |
|-------|-------|--------|
| Development | TC-001 to TC-009 | pytest (TDD) |
| Integration | TC-003, TC-004 (live API) | Manual |
| Acceptance | TC-010 to TC-014 | Manual |

---

## Coverage Requirements
- **Minimum:** 80% line coverage on data.py and cache.py
- **Excluded:** app.py (Streamlit UI code)

---

## Sign-off
- **Author:** QA Role
- **Date:** 2026-02-04
