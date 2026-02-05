# SFI-001 Test Cases

## Test Strategy

- **Framework**: pytest
- **Mocking**: pytest-mock, responses
- **Coverage target**: >80%
- **Test-first**: Tests written before implementation

---

## Test Case Mapping to Acceptance Criteria

| AC | Test Cases |
|----|------------|
| AC1 (Auth) | TC01-TC05 |
| AC2 (Known endpoints) | TC06-TC12 |
| AC3 (Discovery) | TC13-TC16 |
| AC4 (Cache) | TC17-TC22 |
| AC5 (Error handling) | TC23-TC28 |
| AC6 (Unit tests) | All TCs |
| AC7 (Documentation) | Manual review |

---

## Authentication Tests (AC1)

### TC01: Successful authentication
```python
def test_auth_success():
    """Given valid Azure CLI credentials, when getting token, then return valid bearer token"""
    # Arrange: Mock AzureCliCredential to return valid token
    # Act: Call auth.get_token()
    # Assert: Token is non-empty string, no exceptions raised
    # Expected: Returns token string starting with "eyJ"
```

### TC02: Authentication failure - not logged in
```python
def test_auth_failure_not_logged_in():
    """Given no Azure CLI login, when getting token, then raise S360AuthError"""
    # Arrange: Mock AzureCliCredential to raise CredentialUnavailableError
    # Act: Call auth.get_token()
    # Assert: Raises S360AuthError with message containing "az login"
```

### TC03: Authentication failure - wrong scope
```python
def test_auth_failure_wrong_scope():
    """Given invalid scope, when getting token, then raise S360AuthError"""
    # Arrange: Mock credential to raise error for S360 scope
    # Act: Call auth.get_token()
    # Assert: Raises S360AuthError with scope information
```

### TC04: Get current user info success
```python
def test_get_user_info_success():
    """Given valid auth, when getting user info, then return user dict with alias"""
    # Arrange: Mock Graph API response with user data
    # Act: Call auth.get_current_user()
    # Assert: Returns dict with 'displayName', 'alias', 'mail' keys
```

### TC05: Get current user info failure
```python
def test_get_user_info_failure():
    """Given Graph API error, when getting user info, then raise S360ApiError"""
    # Arrange: Mock Graph API to return 403
    # Act: Call auth.get_current_user()
    # Assert: Raises S360ApiError with status code
```

---

## Known Endpoint Tests (AC2)

### TC06: GetEtaHistoryById success
```python
def test_get_eta_history_success():
    """Given valid KPI and action item IDs, when calling get_eta_history, then return history list"""
    # Arrange: Mock API to return JSON array of history items
    # Act: Call client.get_eta_history(kpi_id, action_item_id)
    # Assert: Returns list of dicts with expected keys
```

### TC07: GetEtaHistoryById not found
```python
def test_get_eta_history_not_found():
    """Given invalid IDs, when calling get_eta_history, then raise S360ApiError with 404"""
    # Arrange: Mock API to return 404
    # Act: Call client.get_eta_history(invalid_id, invalid_id)
    # Assert: Raises S360ApiError, error.status_code == 404
```

### TC08: GetEtaHistoryById empty response
```python
def test_get_eta_history_empty():
    """Given valid IDs with no history, when calling get_eta_history, then return empty list"""
    # Arrange: Mock API to return empty array []
    # Act: Call client.get_eta_history(kpi_id, action_item_id)
    # Assert: Returns empty list, no exception
```

### TC09: SaveETAsByIds success
```python
def test_save_etas_success():
    """Given valid ETA data, when calling save_etas, then return True"""
    # Arrange: Mock API to return 200
    # Act: Call client.save_etas(eta_data)
    # Assert: Returns True
```

### TC10: SaveETAsByIds validation error
```python
def test_save_etas_validation_error():
    """Given invalid ETA data, when calling save_etas, then raise S360ApiError with 400"""
    # Arrange: Mock API to return 400 with validation message
    # Act: Call client.save_etas(invalid_data)
    # Assert: Raises S360ApiError, error.status_code == 400, error.message contains details
```

### TC11: SaveETAsByIds unauthorized
```python
def test_save_etas_unauthorized():
    """Given expired token, when calling save_etas, then raise S360AuthError"""
    # Arrange: Mock API to return 401
    # Act: Call client.save_etas(eta_data)
    # Assert: Raises S360AuthError with re-auth suggestion
```

### TC12: API timeout handling
```python
def test_api_timeout():
    """Given slow API, when timeout exceeded, then raise S360ApiError with timeout message"""
    # Arrange: Mock API to delay beyond timeout
    # Act: Call any API method with timeout=1
    # Assert: Raises S360ApiError with "timeout" in message
```

---

## Discovery Tests (AC3)

### TC13: Discover known endpoints
```python
def test_discover_returns_known_endpoints():
    """Given API access, when discovering, then return at least known endpoints"""
    # Arrange: Mock API to respond to known endpoints
    # Act: Call discovery.discover_endpoints()
    # Assert: Result contains 'ActionItems/GetEtaHistoryById', 'ActionItems/SaveETAsByIds'
```

### TC14: Discover finds new endpoints
```python
def test_discover_finds_new_endpoints():
    """Given API responds to probed paths, when discovering, then return new endpoints"""
    # Arrange: Mock API to return 200 for /Services
    # Act: Call discovery.discover_endpoints()
    # Assert: Result contains 'Services' endpoint info
```

### TC15: Discover handles 404 gracefully
```python
def test_discover_handles_not_found():
    """Given API returns 404 for probed path, when discovering, then skip without error"""
    # Arrange: Mock API to return 404 for unknown paths
    # Act: Call discovery.discover_endpoints()
    # Assert: No exception, returns partial results
```

### TC16: Discover respects rate limits
```python
def test_discover_rate_limit_backoff():
    """Given API returns 429, when discovering, then back off and retry"""
    # Arrange: Mock API to return 429 then 200
    # Act: Call discovery.discover_endpoints()
    # Assert: Eventually succeeds, logs retry
```

---

## Cache Tests (AC4)

### TC17: Cache miss loads from API
```python
def test_cache_miss_calls_api():
    """Given empty cache, when requesting data, then call API and cache result"""
    # Arrange: Empty cache directory, mock API response
    # Act: Call client.get_eta_history() with use_cache=True
    # Assert: API called, cache file created
```

### TC18: Cache hit returns cached data
```python
def test_cache_hit_returns_cached():
    """Given cached data exists, when requesting, then return cached without API call"""
    # Arrange: Pre-populate cache file
    # Act: Call client.get_eta_history() with use_cache=True
    # Assert: API not called, returns cached data
```

### TC19: Cache expiry triggers refresh
```python
def test_cache_expiry_refreshes():
    """Given expired cache, when requesting, then call API and update cache"""
    # Arrange: Create cache file with old timestamp
    # Act: Call with cache_expiry_minutes=0
    # Assert: API called, cache updated
```

### TC20: Cache disabled bypasses cache
```python
def test_cache_disabled():
    """Given use_cache=False, when requesting, then always call API"""
    # Arrange: Pre-populate cache
    # Act: Call with use_cache=False
    # Assert: API called despite cache existing
```

### TC21: Cache write failure non-fatal
```python
def test_cache_write_failure_continues():
    """Given cache directory not writable, when caching, then log warning but return data"""
    # Arrange: Mock cache write to raise IOError
    # Act: Call API method
    # Assert: Returns data, logs warning, no exception
```

### TC22: Cache corruption recovery
```python
def test_cache_corruption_recovery():
    """Given corrupted cache file, when reading, then delete and fetch fresh"""
    # Arrange: Create cache file with invalid JSON
    # Act: Call API method with use_cache=True
    # Assert: API called, corrupted file deleted, new cache created
```

---

## Error Handling Tests (AC5)

### TC23: Network error handling
```python
def test_network_error():
    """Given no network, when calling API, then raise S360ApiError with network message"""
    # Arrange: Mock requests to raise ConnectionError
    # Act: Call any API method
    # Assert: Raises S360ApiError with "network" or "connection" in message
```

### TC24: Server error handling (5xx)
```python
def test_server_error():
    """Given API returns 500, when calling, then raise S360ApiError with status"""
    # Arrange: Mock API to return 500
    # Act: Call any API method
    # Assert: Raises S360ApiError, error.status_code == 500
```

### TC25: Malformed JSON response
```python
def test_malformed_json_response():
    """Given API returns invalid JSON, when parsing, then raise S360ApiError"""
    # Arrange: Mock API to return non-JSON text
    # Act: Call API method
    # Assert: Raises S360ApiError with "parse" or "JSON" in message
```

### TC26: Empty response body
```python
def test_empty_response_body():
    """Given API returns empty body, when parsing, then handle gracefully"""
    # Arrange: Mock API to return 200 with empty body
    # Act: Call API method
    # Assert: Returns None or empty dict, no exception
```

### TC27: Forbidden (403) error
```python
def test_forbidden_error():
    """Given user lacks permission, when calling API, then raise S360AuthError"""
    # Arrange: Mock API to return 403
    # Act: Call API method
    # Assert: Raises S360AuthError with permission message
```

### TC28: Error includes request details
```python
def test_error_includes_context():
    """Given any API error, error object includes endpoint and status"""
    # Arrange: Mock API to return 400
    # Act: Call API method, catch exception
    # Assert: Exception has endpoint, status_code, response_body attributes
```

---

## Integration Test Scenarios (require az login)

### IT01: Full auth flow
```python
@pytest.mark.integration
def test_full_auth_flow():
    """End-to-end authentication test (requires az login)"""
    # Skip if no Azure CLI session
    # Act: Authenticate and get user info
    # Assert: Returns valid user info
```

### IT02: Full API roundtrip
```python
@pytest.mark.integration
def test_full_api_roundtrip():
    """End-to-end API call (requires az login and valid IDs)"""
    # Skip if no Azure CLI session
    # Act: Call get_eta_history with known IDs
    # Assert: Returns valid response structure
```

---

## Test Data / Fixtures

```python
# conftest.py fixtures

@pytest.fixture
def mock_token():
    return "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.mock_payload.mock_signature"

@pytest.fixture
def sample_eta_history():
    return [
        {"id": "1", "eta": "2026-03-01", "status": "InProgress", "notes": "Working on it"},
        {"id": "2", "eta": "2026-02-15", "status": "Complete", "notes": "Done"}
    ]

@pytest.fixture
def sample_user_info():
    return {
        "displayName": "Test User",
        "alias": "testuser",
        "userPrincipalName": "testuser@microsoft.com",
        "mail": "testuser@microsoft.com"
    }

@pytest.fixture  
def temp_cache_dir(tmp_path):
    return tmp_path / "s360_cache"
```

---

## Test Execution Commands

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/s360_client --cov-report=html

# Run only unit tests (no az login required)
pytest tests/ -v -m "not integration"

# Run integration tests (requires az login)
pytest tests/ -v -m integration
```
