# Test Cases: LLM-0003

**Work Item:** LLM-0003  
**Author:** Quality Assurance  
**Date:** 2026-02-07

---

## Test Framework
- `pytest` + `pytest-asyncio`
- `monkeypatch` for env vars
- `unittest.mock` for azure-identity

## Test File Structure
```
tests/
├── test_auth_env_var.py       # EnvVarAuth tests
├── test_auth_msi.py           # ManagedIdentityAuth tests
├── test_auth_callback.py      # CallbackAuth tests
├── test_auth_base.py          # AuthStrategy ABC tests
└── conftest.py                # Shared fixtures
```

---

## TC-1: AuthStrategy is abstract and cannot be instantiated (AC-1)

| Field | Value |
|---|---|
| **Type** | Unit — Structural |
| **Given** | `AuthStrategy` class |
| **When** | Attempting `AuthStrategy()` |
| **Then** | Raises `TypeError` |
| **Failure message** | `"AuthStrategy should not be directly instantiable"` |

## TC-2: EnvVarAuth resolves API key from env var (AC-2)

| Field | Value |
|---|---|
| **Type** | Unit — Happy Path |
| **Given** | Env var `LLM_API_KEY` set to `"test-key-123"` |
| **When** | `EnvVarAuth("LLM_API_KEY").resolve()` |
| **Then** | Returns `"test-key-123"` |
| **Failure message** | `"EnvVarAuth should return the value of the named env var"` |

## TC-3: EnvVarAuth raises on missing env var (AC-7)

| Field | Value |
|---|---|
| **Type** | Unit — Error Case |
| **Given** | Env var `MISSING_VAR` is not set |
| **When** | `EnvVarAuth("MISSING_VAR").resolve()` |
| **Then** | Raises `AuthenticationError` mentioning `"MISSING_VAR"` |
| **Failure message** | `"EnvVarAuth should raise AuthenticationError for missing env var"` |

## TC-4: EnvVarAuth raises on empty env var (AC-7)

| Field | Value |
|---|---|
| **Type** | Unit — Edge Case |
| **Given** | Env var `EMPTY_VAR` set to `""` |
| **When** | `EnvVarAuth("EMPTY_VAR").resolve()` |
| **Then** | Raises `AuthenticationError` |
| **Failure message** | `"EnvVarAuth should raise AuthenticationError for empty env var"` |

## TC-5: EnvVarAuth.aresolve() works async (AC-2)

| Field | Value |
|---|---|
| **Type** | Unit — Happy Path (async) |
| **Given** | Env var `LLM_API_KEY` set to `"test-key-123"` |
| **When** | `await EnvVarAuth("LLM_API_KEY").aresolve()` |
| **Then** | Returns `"test-key-123"` |
| **Failure message** | `"EnvVarAuth.aresolve() should return the value of the named env var"` |

## TC-6: ManagedIdentityAuth calls azure-identity (AC-3)

| Field | Value |
|---|---|
| **Type** | Unit — Happy Path |
| **Given** | Mocked `ManagedIdentityCredential.get_token()` returning token `"msi-token-456"` |
| **When** | `ManagedIdentityAuth().resolve()` |
| **Then** | Returns `"msi-token-456"` |
| **Failure message** | `"ManagedIdentityAuth should return token from azure-identity"` |

## TC-7: ManagedIdentityAuth raises ImportError without azure-identity (AC-3)

| Field | Value |
|---|---|
| **Type** | Unit — Error Case |
| **Given** | `azure.identity` is not importable (mocked) |
| **When** | `ManagedIdentityAuth()` |
| **Then** | Raises `ImportError` mentioning `azure-identity` |
| **Failure message** | `"ManagedIdentityAuth should raise ImportError with install instructions"` |

## TC-8: CallbackAuth calls user function (AC-4)

| Field | Value |
|---|---|
| **Type** | Unit — Happy Path |
| **Given** | `CallbackAuth(callback=lambda: "callback-key-789")` |
| **When** | `auth.resolve()` |
| **Then** | Returns `"callback-key-789"` |
| **Failure message** | `"CallbackAuth should return value from user-supplied callback"` |

## TC-9: CallbackAuth.aresolve() uses async callback when provided (AC-4)

| Field | Value |
|---|---|
| **Type** | Unit — Happy Path (async) |
| **Given** | `CallbackAuth(callback=..., async_callback=async_fn)` where `async_fn` returns `"async-key"` |
| **When** | `await auth.aresolve()` |
| **Then** | Returns `"async-key"` |
| **Failure message** | `"CallbackAuth.aresolve() should use async_callback when provided"` |

## TC-10: CallbackAuth.aresolve() falls back to sync callback (AC-4)

| Field | Value |
|---|---|
| **Type** | Unit — Edge Case (async) |
| **Given** | `CallbackAuth(callback=lambda: "sync-key")` — no async_callback |
| **When** | `await auth.aresolve()` |
| **Then** | Returns `"sync-key"` |
| **Failure message** | `"CallbackAuth.aresolve() should fall back to sync callback when no async_callback"` |

## TC-11: CallbackAuth raises on empty result (AC-7)

| Field | Value |
|---|---|
| **Type** | Unit — Error Case |
| **Given** | `CallbackAuth(callback=lambda: "")` |
| **When** | `auth.resolve()` |
| **Then** | Raises `AuthenticationError` |
| **Failure message** | `"CallbackAuth should raise AuthenticationError on empty credential"` |

## TC-12: repr() never contains credential values (AC-5, AC-6)

| Field | Value |
|---|---|
| **Type** | Unit — Security |
| **Given** | Instances of `EnvVarAuth`, `ManagedIdentityAuth`, `CallbackAuth` |
| **When** | `repr(auth)` is called on each |
| **Then** | No credential value appears in the output |
| **Failure message** | `"repr() must never expose credential values"` |

## TC-13: str() never contains credential values (AC-5, AC-6)

| Field | Value |
|---|---|
| **Type** | Unit — Security |
| **Given** | Instances of all auth strategies |
| **When** | `str(auth)` is called |
| **Then** | No credential value appears |
| **Failure message** | `"str() must never expose credential values"` |

## TC-14: Credentials are not logged at any level (AC-5)

| Field | Value |
|---|---|
| **Type** | Unit — Security |
| **Given** | Auth module logging captured |
| **When** | `resolve()` is called successfully |
| **Then** | No log message at any level contains the resolved credential |
| **Failure message** | `"Credentials must never appear in log output"` |

---

## Acceptance Criteria Coverage Matrix

| AC | Test Cases |
|---|---|
| AC-1: AuthStrategy ABC | TC-1 |
| AC-2: EnvVarAuth | TC-2, TC-5 |
| AC-3: ManagedIdentityAuth | TC-6, TC-7 |
| AC-4: CallbackAuth | TC-8, TC-9, TC-10 |
| AC-5: Never persisted/logged | TC-12, TC-13, TC-14 |
| AC-6: repr/str mask secrets | TC-12, TC-13 |
| AC-7: Clear error on failure | TC-3, TC-4, TC-11 |
