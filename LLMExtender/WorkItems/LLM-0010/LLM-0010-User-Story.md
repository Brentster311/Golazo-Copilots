# LLM-0010: Reusable AAD Login-Wait Helper

## Status: IMPLEMENTED

## User Story

- **Title:** Reusable AAD Login-Wait Helper
- **As a:** developer maintaining `llm_extender`'s browser-based URL fetching
- **I want:** a reusable helper function that waits for AAD login to complete in a Playwright browser page
- **So that:** the login-detection and wait logic is not duplicated across `browser_auth="aad"` and `browser_auth="cdp"` code paths, and future browser auth modes can reuse it

- **Out of scope:**
  - Non-AAD identity providers (Okta, Auth0, etc.)
  - Automating the login itself — this is only a wait/detect mechanism
  - Changing the behavior of `browser_auth="aad"` beyond refactoring to use the shared helper

- **Assumptions:**
  - **Assumption (explicit):** Python library feature — internal refactoring with a new utility function.
  - **Assumption (explicit):** AAD login pages are identifiable by URL patterns: `login.microsoftonline.com`, `login.windows.net`, `login.live.com`, and `devicelogin`.
  - **Assumption (explicit):** The helper is used internally by `url_fetcher.py` — it does not need to be part of the public API.

- **Acceptance Criteria (bulleted, testable):**
  - A `wait_for_aad_login(page, timeout)` function exists in `llm_extender/auth/aad_browser.py` that polls the page URL and returns once the URL no longer matches known AAD login domains
  - The function raises `AuthenticationError` with a clear message if the timeout expires while still on an AAD login page
  - `_fetch_with_browser` (sync) uses the helper for both `browser_auth="aad"` and `browser_auth="cdp"` paths
  - `_afetch_with_browser` (async) uses an async variant `await_for_aad_login(page, timeout)`
  - Existing tests for `browser_auth="aad"` continue to pass unchanged
  - The helper is unit-testable with a mocked Playwright page object

- **Non-functional requirements:**
  - Poll interval should be 1 second (not busy-wait)
  - No credentials or tokens are logged

- **Telemetry / metrics expected:**
  - None (library, not a service)

- **Rollout / rollback notes:**
  - Internal refactoring — no public API changes
  - Depends on LLM-0009 for the `browser_auth="cdp"` consumer, but can be implemented independently
