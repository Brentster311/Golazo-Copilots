# SFI-002 Test Cases

## Test Strategy
- **Approach:** TDD - tests written before refactoring
- **Framework:** pytest
- **Coverage Target:** 80% for new packaging code

---

## Test Categories

### 1. Package Structure Tests

#### TC-001: Package is importable
```python
def test_package_importable():
    """Verify package can be imported after installation."""
    import accia_s360
    assert accia_s360 is not None
```
- **Type:** Smoke test
- **Priority:** P0
- **Expected:** Import succeeds without error

#### TC-002: Public API exports
```python
def test_public_api_exports():
    """Verify all public classes are exported from package root."""
    from accia_s360 import S360Client
    assert S360Client is not None
```
- **Type:** Unit test
- **Priority:** P0
- **Expected:** S360Client is accessible from package root

#### TC-003: Version is defined
```python
def test_version_defined():
    """Verify package version is accessible."""
    import accia_s360
    assert hasattr(accia_s360, '__version__')
    assert accia_s360.__version__ == '0.1.0'
```
- **Type:** Unit test
- **Priority:** P1
- **Expected:** Version matches pyproject.toml

---

### 2. Backward Compatibility Tests

#### TC-004: S360Client initialization
```python
def test_client_initialization():
    """Verify S360Client can be instantiated."""
    from accia_s360 import S360Client
    client = S360Client()
    assert client is not None
```
- **Type:** Unit test
- **Priority:** P0
- **Expected:** Client initializes without error

#### TC-005: All endpoint methods exist
```python
def test_endpoint_methods_exist():
    """Verify all expected endpoint methods are available."""
    from accia_s360 import S360Client
    client = S360Client()
    
    expected_methods = [
        'get_current_user',
        'get_action_items',
        'get_action_items_grid',
        'get_kpi',
        'get_default_landing_view',
        'get_all_action_item_metadata',
    ]
    
    for method in expected_methods:
        assert hasattr(client, method), f"Missing method: {method}"
```
- **Type:** Unit test
- **Priority:** P0
- **Expected:** All documented methods exist

---

### 3. Authentication Tests

#### TC-006: Auth with valid credentials
```python
def test_auth_with_valid_credentials(mocker):
    """Verify authentication succeeds with valid Azure CLI credentials."""
    # Mock Azure CLI credential
    mock_cred = mocker.patch('accia_s360.auth.AzureCliCredential')
    mock_cred.return_value.get_token.return_value.token = 'test-token'
    
    from accia_s360 import S360Client
    client = S360Client()
    
    # Should not raise
    assert client._auth is not None
```
- **Type:** Unit test (mocked)
- **Priority:** P0
- **Expected:** Client authenticates successfully

#### TC-007: Auth failure raises clear error
```python
def test_auth_failure_raises_clear_error(mocker):
    """Verify authentication failure provides helpful error message."""
    mock_cred = mocker.patch('accia_s360.auth.AzureCliCredential')
    mock_cred.return_value.get_token.side_effect = Exception("CLI not logged in")
    
    from accia_s360 import S360Client
    
    with pytest.raises(Exception) as exc_info:
        S360Client()
    
    assert "Azure CLI" in str(exc_info.value) or "authentication" in str(exc_info.value).lower()
```
- **Type:** Unit test (mocked)
- **Priority:** P1
- **Expected:** Error message mentions Azure CLI

---

### 4. Build and Install Tests

#### TC-008: Package builds successfully
```bash
# Manual test - run in CI or locally
python -m build
# Expected: dist/ contains .whl and .tar.gz files
```
- **Type:** Build test
- **Priority:** P0
- **Expected:** Build completes without error, creates dist files

#### TC-009: Package installs in clean environment
```bash
# Manual test
python -m venv test_env
test_env/Scripts/activate  # or source test_env/bin/activate
pip install dist/accia_s360-0.1.0-py3-none-any.whl
python -c "from accia_s360 import S360Client; print('OK')"
```
- **Type:** Integration test
- **Priority:** P0
- **Expected:** Package installs and imports successfully

#### TC-010: Dependencies resolve correctly
```python
def test_dependencies_in_pyproject():
    """Verify required dependencies are listed in pyproject.toml."""
    import tomllib
    
    with open('pyproject.toml', 'rb') as f:
        config = tomllib.load(f)
    
    deps = config['project']['dependencies']
    assert any('azure-identity' in d for d in deps)
    assert any('requests' in d for d in deps)
```
- **Type:** Unit test
- **Priority:** P1
- **Expected:** Core dependencies are declared

---

### 5. Regression Tests (Existing Tests)

#### TC-011: All existing tests pass
```bash
pytest tests/ -v
```
- **Type:** Regression
- **Priority:** P0
- **Expected:** 100% of existing tests pass after import path changes

---

## Test Execution Plan

| Phase | Tests | Automation |
|-------|-------|------------|
| Pre-refactor | TC-011 (baseline) | pytest |
| Post-refactor | TC-001 to TC-011 | pytest |
| Pre-publish | TC-008, TC-009 | Manual/CI |
| Post-publish | TC-009 (from Artifacts) | Manual |

---

## Coverage Requirements
- **Minimum:** 80% line coverage on new packaging code
- **Excluded:** Integration tests requiring live API

---

## Sign-off
- **Author:** QA Role
- **Date:** 2026-02-04
