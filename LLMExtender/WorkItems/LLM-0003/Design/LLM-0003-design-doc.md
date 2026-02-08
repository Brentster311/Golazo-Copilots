# Design Document — LLM-0003

## Summary

Implement a pluggable authentication manager for the LLM Extender library that resolves credentials at runtime through multiple strategies (environment variable, Azure MSI, custom callback) with strict secret hygiene guarantees.

## Problem Statement

Developers need different auth mechanisms depending on deployment context: env vars for local dev/CI, Azure MSI for cloud deployments, custom callbacks for vault integration. Hardcoding `api_key` doesn't scale. Credentials must never leak through logs, repr, or disk persistence.

## Business Case

- **Why now:** Auth is required for any real-world LLM integration. LLM-0001 deferred this intentionally.
- **Impact:** Developers can securely connect to LLM providers in any deployment context.
- **KPIs:** All auth strategies testable, zero credential leaks in repr/str/logs.

## Stakeholders

- Python developers consuming the library
- LLM-0001 (client uses auth via `LLMClient(config, auth=...)`)

## Functional Requirements

1. `AuthStrategy` ABC with `resolve() -> str` and `aresolve() -> str`
2. `EnvVarAuth` — reads credential from named env var
3. `ManagedIdentityAuth` — acquires token via Azure MSI (`azure-identity`)
4. `CallbackAuth` — calls user-supplied `() -> str` callable (sync + optional async)
5. Safe repr/str on all auth objects — never exposes credential values
6. Clear `AuthenticationError` on missing/invalid credentials
7. Integration with `LLMClient` via `auth` parameter

## Non-Functional Requirements

- No secret value in repr, str, or logs under any circumstances
- `azure-identity` is an optional dependency (import-time check)
- Type hints on all public API surfaces

## Proposed Approach

- **Strategy pattern**: `AuthStrategy` ABC → concrete implementations
- **Safe repr**: Base class returns `ClassName(***)`, subclasses can show non-secret config (e.g., env var name)
- **Client integration**: `LLMClient.__init__` calls `auth.resolve()` and replaces config `api_key`
- **Async support**: Each strategy implements `aresolve()` — env var delegates to sync, MSI creates async credential, callback uses async_callback or falls back

## Alternatives Considered

| Alternative | Reason Rejected |
|---|---|
| Single auth class with mode parameter | Strategy pattern is more extensible and follows SRP |
| Auto-detect auth from config fields | Too implicit — explicit strategy selection is clearer |

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| azure-identity not installed | Import-time check with helpful error message |
| Credential leaked via exception message | Exceptions only reference strategy type, never the value |

## Dependencies

- `azure-identity` (optional, runtime — only for ManagedIdentityAuth)

## Test Strategy

- 23 tests across 6 test files covering all strategies, error paths, repr/str safety, logging safety, and client integration
