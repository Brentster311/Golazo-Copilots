# LLM-0008: Interactive AAD Browser Login for Authenticated URL Fetches

## Status: BACKLOG

## User Story

- **Title:** Interactive AAD Browser Login for Authenticated URL Fetches
- **As a:** developer using LLM Extender to fetch content from AAD-protected internal web apps
- **I want:** the headless browser to perform an interactive AAD login flow (PKCE/cookies) when Bearer token auth is insufficient
- **So that:** I can summarize content from sites like S360 that require full browser-based AAD authentication rather than just Authorization headers

- **Out of scope:**
  - Non-AAD identity providers (Okta, Auth0, etc.)
  - Storing/persisting refresh tokens across sessions
  - Multi-factor authentication prompts (user must pre-authenticate or use device code flow)
  - Headful (visible) browser mode — this is headless only
  - Managed Service Identity (MSI) — browser login is inherently a user-credential flow; MSI has no interactive session

- **Assumptions:**
  - **Assumption (explicit):** The target sites use standard Microsoft AAD login (login.microsoftonline.com) — this covers the vast majority of internal Microsoft web apps.
  - **Assumption (explicit):** Python library interface — consistent with all other LLM Extender features.
  - **Assumption (explicit):** Cross-platform (Windows, Mac, Linux) — Playwright already supports all three.
  - **Assumption (explicit):** Developers are the target users — they can provide tenant/client IDs and understand AAD scopes.
  - **Assumption (explicit):** Only user-credential auth strategies are valid for `browser_auth="aad"` (e.g., AzureChainedAuth resolving via Azure CLI or device code). If the resolved credential comes from MSI, an `AuthenticationError` is raised explaining that browser login requires user credentials.

- **Acceptance Criteria (bulleted, testable):**
  - When `render_js=True` and a new `browser_auth="aad"` option is provided, the headless browser performs an AAD login using device code flow or stored cookies before navigating to the target URL
  - AAD cookies/session are injected into the browser context so the target site sees an authenticated browser session
  - If AAD login fails or times out, a clear `AuthenticationError` is raised with actionable guidance
  - The feature works for sites that return 401/403 to Bearer tokens but accept AAD browser sessions (e.g., S360, SharePoint web UI)
  - Existing `render_js=True` behavior (Bearer token via `extra_http_headers`) is unchanged when `browser_auth` is not specified
  - Browser session cookies are not persisted to disk by default (security)
  - If the auth strategy resolves to a Managed Service Identity credential (not user credentials), an `AuthenticationError` is raised with a clear message that `browser_auth="aad"` requires user credentials (Azure CLI, device code, etc.)

- **Non-functional requirements:**
  - AAD login timeout should be configurable (default 60s)
  - No credentials or tokens should be logged or persisted to disk
  - Must not break existing `render_js=True` tests

- **Telemetry / metrics expected:**
  - None (library, not a service)

- **Rollout / rollback notes:**
  - Additive feature — new optional parameter, no breaking changes
  - Requires Playwright (`[browser]` extra) already installed from LLM-0007
  - May require `msal` or `azure-identity` for device code flow
