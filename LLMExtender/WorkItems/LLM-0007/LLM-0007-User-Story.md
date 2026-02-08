# LLM-0007: Client-Side Rendering Support for URL Fetcher

## Status: IMPLEMENTED

## User Story

- **Title:** Client-Side Rendering Support for URL Fetcher
- **As a:** developer using LLM Extender
- **I want:** `fetch_url` to optionally render JavaScript-heavy pages (SPAs) using a headless browser before extracting text
- **So that:** I can fetch content from single-page applications (e.g., Azure portals, SharePoint, React/Angular apps) that return empty HTML shells without JavaScript execution

## Out of Scope
- Automating browser login flows (Azure AD interactive auth) — the caller provides cookies or tokens
- Rendering pages that require multi-step user interaction (form fills, clicks)
- Long-running browser sessions or browser pooling
- PDF or image content extraction

## Assumptions
- **Assumption (explicit):** Playwright will be used as the headless browser engine — it has the best async support and cross-browser coverage for Python
- **Assumption (explicit):** Playwright is an optional dependency (`pip install llm-extender[browser]`) — not required for basic `fetch_url` usage
- **Assumption (explicit):** This is a Python library feature, cross-platform (Windows/Mac/Linux), no persistence needed, for developer use
- **Assumption (explicit):** The existing `fetch_url` / `afetch_url` API will gain a `render_js=True` parameter rather than creating new functions

## Acceptance Criteria
- [ ] `fetch_url("https://spa-app.com", render_js=True)` launches a headless browser, waits for JS to render, then extracts text
- [ ] `afetch_url` async variant also supports `render_js=True`
- [ ] When `render_js=False` (default), behavior is unchanged from LLM-0006 — no browser dependency required
- [ ] When `render_js=True` and Playwright is not installed, raises a clear error with install instructions
- [ ] Auth tokens/cookies can be injected into the browser context for authenticated SPA fetches
- [ ] Headless browser is closed and resources released after each fetch

## Non-Functional Requirements
- Playwright dependency is optional — core library must not import it unless `render_js=True`
- Browser launch + render + close should complete within the existing `timeout` parameter
- No browser state persisted between calls

## Telemetry / Metrics Expected
- None (library, not a service)

## Rollout / Rollback Notes
- Additive feature — `render_js` defaults to `False`, fully backward compatible
- New optional dependency group: `pip install llm-extender[browser]`

## Context: Why This Is Needed
During LLM-0006 live testing, we discovered that:
- `aka.ms/msw` → redirects to SharePoint (SPA, returns empty shell + JS bundles)
- `aka.ms/s360` → redirects to Service360 (SPA, React app, API-driven content)

Both returned no meaningful text content because the HTML is just a JavaScript bootstrap. A headless browser would execute the JS and produce the rendered DOM for text extraction.
