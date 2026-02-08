# LLM-0008 Design Document

## Overview
Add `browser_auth="aad"` option for AAD-protected web apps that reject Bearer tokens and require full browser cookie-based authentication.

## Architecture

### Authentication Flow
```
User calls fetch_url(url, render_js=True, browser_auth="aad", auth=url_auth)
    │
    ├─ 1. Validate auth is user-based (not MSI) → AuthenticationError if MSI
    ├─ 2. Get access token from auth strategy
    ├─ 3. Decode JWT to extract upn (user principal name) and tid (tenant ID)
    ├─ 4. Launch Playwright headless browser
    ├─ 5. Navigate to target URL
    ├─ 6. Detect AAD redirect (login.microsoftonline.com)
    │     ├─ If no redirect → use existing token-based auth (LLM-0007 behavior)
    │     └─ If AAD redirect detected:
    │         ├─ 7. Extract authorize params (client_id, redirect_uri, scope, state, nonce)
    │         ├─ 8. Initiate MSAL device code flow for the target resource scope
    │         ├─ 9. Print device code instructions to stderr
    │         ├─ 10. Wait for user to authenticate (with timeout)
    │         ├─ 11. MSAL returns tokens
    │         └─ 12. Navigate browser back to target URL with fresh token
    └─ 13. Extract page content
```

### MSI Detection
- `ManagedIdentityAuth` → always rejected
- `AzureChainedAuth` → check if auth is user-based by inspecting credential type
- `EnvVarAuth`, `CallbackAuth` → allowed (user explicitly provided credentials)

### New Module: `llm_extender/auth/aad_browser.py`
- `is_user_credential(auth: AuthStrategy) -> bool` — returns False for MSI
- `decode_jwt_claims(token: str) -> dict` — extract upn/tid without verification
- `detect_aad_redirect(url: str) -> bool` — check if URL is login.microsoftonline.com
- `parse_aad_authorize_url(url: str) -> dict` — extract client_id, scope, etc.
- `run_device_code_flow(tenant_id, scope) -> dict` — MSAL device code flow wrapper

### Parameter Changes
- `fetch_url()` / `afetch_url()`: add `browser_auth: str | None = None`
- `complete_with_url()` / `acomplete_with_url()`: add `browser_auth: str | None = None`
- Valid values: `None` (default, no change), `"aad"` (AAD device code flow)

### Dependencies
- `msal>=1.20` — added to `[browser]` optional dependency group
- `playwright>=1.40` — already required by `[browser]`

## Constraints
- Headless only (no headed browser)
- No cookies persisted to disk
- Device code flow requires user interaction (print to stderr, user authenticates in own browser)
- Sites using auth code flow (PKCE) may still require cookie-based auth that device code tokens can't provide — clear error in that case

## Security
- JWT decoded without signature verification (for upn/tid only, not for auth)
- No tokens logged or persisted
- MSAL token cache is in-memory only
