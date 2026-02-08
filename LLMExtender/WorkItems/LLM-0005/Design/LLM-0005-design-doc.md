# LLM-0005 Design Doc

## Summary
Add `AzureChainedAuth` — an `AuthStrategy` that resolves credentials via a predictable 3-step chain: Azure CLI → MSI → API key → fail. The `scope` parameter is configurable so the same class serves both LLM API auth (0005) and authenticated URL fetches (0006).

## Problem Statement
Today, using Azure AD auth with LLM Extender requires manually fetching tokens and wiring them through `CallbackAuth`. This is friction for local dev and error-prone in production.

## Proposed Approach
- New file: `llm_extender/auth/azure_chained.py`
- Class `AzureChainedAuth(AuthStrategy)` with `__init__(self, scope, api_key)`
- `resolve()` tries: AzureCliCredential → ManagedIdentityCredential → api_key → raise
- `aresolve()` uses `azure.identity.aio` async variants for steps 1-2
- `azure-identity` is lazily imported; if not installed, steps 1-2 are skipped and chain falls to step 3

## Alternatives Considered
1. **Use `DefaultAzureCredential`** — Rejected by PO. Opaque 8-step chain, unpredictable ordering.
2. **Separate classes per credential type** — Already exists (`ManagedIdentityAuth`). This story adds the chained combo.

## Risks & Mitigations
| Risk | Mitigation |
|------|-----------|
| `azure-identity` not installed | Steps 1-2 skipped gracefully, falls to API key |
| Token expiry mid-session | Azure-identity handles refresh internally |

## Dependencies
- `azure-identity` (optional, already established)
- No new required dependencies

## Test Strategy
- Unit tests mocking `AzureCliCredential`, `ManagedIdentityCredential`
- Tests for chain order (CLI first, then MSI, then key)
- Tests for missing `azure-identity` (fallback to key)
- Tests for all-fail error message
- Tests for custom scope
- Async tests
