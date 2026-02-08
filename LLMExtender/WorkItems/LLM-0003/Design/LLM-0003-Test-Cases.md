# Test Cases — LLM-0003

## Test Case Mapping to Acceptance Criteria

| AC# | Acceptance Criterion | Test Case(s) | File |
|-----|---------------------|--------------|------|
| AC-1 | AuthStrategy ABC with resolve() method | TC-1 | test_auth_base.py |
| AC-2 | EnvVarAuth resolves from env var | TC-2, TC-5 | test_auth_env_var.py |
| AC-3 | ManagedIdentityAuth acquires token via MSI | TC-6, TC-7 | test_auth_msi.py |
| AC-4 | CallbackAuth accepts user callable | TC-8, TC-9, TC-10 | test_auth_callback.py |
| AC-5 | Credentials never persisted/logged | TC-14 | test_auth_security.py |
| AC-6 | repr/str never expose secrets | TC-12, TC-13 | test_auth_security.py |
| AC-7 | Missing/invalid credentials raise clear error | TC-3, TC-4, TC-11 | test_auth_env_var.py, test_auth_callback.py |

## Additional Test Coverage

| Test ID | Description | File |
|---------|------------|------|
| A1 | Callback exceptions wrapped in AuthenticationError | test_auth_callback.py |
| — | Client + EnvVarAuth integration | test_auth_client_integration.py |
| — | Client + CallbackAuth integration | test_auth_client_integration.py |
| — | Client fallback to config.api_key | test_auth_client_integration.py |

## Coverage Summary

- **23 tests** across 6 test files
- All 7 acceptance criteria have direct test coverage
- Security tests cover repr, str, and logging across all strategy types
- Integration tests verify auth works end-to-end with LLMClient
