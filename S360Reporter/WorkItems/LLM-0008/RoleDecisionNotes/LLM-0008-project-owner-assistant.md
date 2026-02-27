# LLM-0008 Project Owner Assistant Notes

## Context
During live testing of `aka.ms/s360` with LLM-0007's `render_js=True`:
- **httpx + Bearer token** → HTTP 403
- **Playwright + Bearer token** → Page renders but shows "You do not have permission"
- S360 (and similar Microsoft internal apps like SharePoint web UI) require **interactive AAD login** that produces session cookies, not just an Authorization header

## Problem
Many internal Microsoft web apps use AAD for authentication but don't accept Bearer tokens via HTTP headers. They require the browser to go through the full AAD login flow (redirect to login.microsoftonline.com → authenticate → redirect back with cookies). This is a different auth model than API-style Bearer token auth.

## Approach Options Considered
1. **Device code flow** — User authenticates in a separate browser, token is exchanged for cookies. Works headless.
2. **Cookie persistence** — Cache AAD cookies from a previous manual login. Fast but security concern.
3. **MSAL browser auth** — Use MSAL's interactive flow to get tokens, then exchange for browser cookies.

## Decision
Created as BACKLOG. The story focuses on device code flow as the primary mechanism since it works in headless mode and doesn't require storing credentials. Cookie persistence is explicitly out of scope for security reasons.

**User-credential guard:** Per PO direction, `browser_auth="aad"` must only operate when user credentials are present (Azure CLI, device code flow, etc.). If the auth strategy resolves to MSI, an `AuthenticationError` is raised immediately — MSI is a service identity with no interactive session, so browser-based AAD login is impossible. This prevents confusing failures deep in the AAD login flow.

## Scope Justification
This is a single vertical slice: one new parameter (`browser_auth="aad"`) that enables AAD browser login before navigation. It builds on LLM-0007's Playwright infrastructure without modifying it.
