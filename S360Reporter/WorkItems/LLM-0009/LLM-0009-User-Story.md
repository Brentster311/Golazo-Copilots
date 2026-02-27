# LLM-0009: CDP Browser Auth for Conditional Access–Protected Sites

## Status: IMPLEMENTED

## User Story

- **Title:** CDP Browser Auth for Conditional Access–Protected Sites
- **As a:** developer using LLM Extender to fetch content from AAD-protected internal web apps that enforce Conditional Access (managed/compliant device) policies
- **I want:** `fetch_url` / `complete_with_url` to support a `browser_auth="cdp"` mode that connects Playwright to the user's real browser (Edge) via Chrome DevTools Protocol
- **So that:** I can fetch and summarize content from sites like S360 that reject device-code flow and fresh browser instances due to Conditional Access error 530033/53000

- **Out of scope:**
  - Non-Chromium browsers (Firefox, Safari) — CDP is Chromium-only
  - macOS/Linux support in this iteration — Edge user-data-dir paths are Windows-specific (cross-platform can follow)
  - Keeping the user's browser open after fetch — the library disconnects via CDP, it does not manage the browser lifecycle beyond the fetch
  - Automating the AAD login itself — user is expected to already be signed in or will sign in interactively in the browser window
  - Browser process pooling or reuse across multiple calls

- **Assumptions:**
  - **Assumption (explicit):** Microsoft Edge is installed and is the user's primary browser with device compliance — this covers the vast majority of Microsoft internal developer workstations.
  - **Assumption (explicit):** Python library feature — consistent with all other LLM Extender features.
  - **Assumption (explicit):** Windows-first — Edge paths and user-data-dir location are Windows-specific. Cross-platform support is a future enhancement.
  - **Assumption (explicit):** The library will kill existing Edge instances and relaunch with `--remote-debugging-port` because Edge ignores CDP flags when already running. The user is warned and `--restore-last-session` preserves their tabs.
  - **Assumption (explicit):** Playwright (`[browser]` extra) is already installed from LLM-0007.

- **Acceptance Criteria (bulleted, testable):**
  - `fetch_url(url, render_js=True, browser_auth="cdp")` launches Edge with the user's real profile and `--remote-debugging-port`, connects via CDP, navigates to the URL, waits for the SPA to render, and returns extracted text
  - `complete_with_url(prompt, url, render_js=True, browser_auth="cdp")` works end-to-end: fetches via CDP + sends to LLM
  - If Edge is already running, it is gracefully closed (with `--restore-last-session` on relaunch) and a warning is printed to stderr
  - If the page redirects to an AAD login URL, the library polls (up to configurable timeout) for the user to complete interactive login before extracting content
  - If CDP connection fails, a clear `ProviderError` is raised with actionable guidance
  - Existing `browser_auth="aad"` (device-code flow) and `browser_auth=None` paths are unchanged
  - Async variant `afetch_url` also supports `browser_auth="cdp"`

- **Non-functional requirements:**
  - CDP port is configurable (default 9222)
  - Login wait timeout is configurable (default 120s)
  - No credentials or tokens are logged or persisted
  - Edge user-data-dir is never modified — the library only reads from it

- **Telemetry / metrics expected:**
  - None (library, not a service)

- **Rollout / rollback notes:**
  - Additive feature — new `browser_auth="cdp"` value, no breaking changes
  - Requires Playwright (`[browser]` extra) already installed from LLM-0007
  - Windows-only initially; cross-platform paths can be added later
