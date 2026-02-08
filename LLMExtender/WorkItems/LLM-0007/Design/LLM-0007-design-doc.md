# LLM-0007 Design Document

## Summary
Add optional client-side JavaScript rendering to the existing `fetch_url` / `afetch_url` functions via a `render_js=True` parameter, powered by Playwright as a headless browser engine.

## Problem Statement
LLM-0006 introduced URL content fetching, but SPAs (single-page applications) like SharePoint and Service360 return empty HTML shells — all content is rendered client-side via JavaScript. Without executing that JS, the fetcher returns no useful text.

## Business Case
- **Why now:** LLM-0006 live testing revealed the gap immediately — two of three test URLs failed because they were SPAs.
- **Impact:** Enables grounding LLM responses with content from any web page, not just server-rendered ones.
- **KPIs:** The existing live tests for `aka.ms/s360` should start returning real content when `render_js=True` is used.

## Stakeholders
- Library consumers who need to fetch SPA content for LLM context

## Functional Requirements
1. `fetch_url(url, render_js=True)` launches headless Chromium, navigates to URL, waits for content, extracts inner text
2. `afetch_url(url, render_js=True)` — async variant using Playwright's native async API
3. `render_js=False` (default) — behavior unchanged, no Playwright dependency needed
4. Missing Playwright raises `ProviderError` with install instructions
5. Auth: `auth` parameter resolves a Bearer token and injects it as a cookie or extra HTTP header in the browser context
6. `complete_with_url` / `acomplete_with_url` pass `render_js` through to fetcher

## Non-Functional Requirements
- Playwright is optional: `pip install llm-extender[browser]`
- Lazy import — Playwright not imported unless `render_js=True`
- Browser closed after each fetch (no resource leaks)
- Timeout applies to entire browser lifecycle

## Proposed Approach
1. Add `render_js: bool = False` parameter to `fetch_url` and `afetch_url`
2. When `True`, call new private functions `_fetch_with_browser` / `_afetch_with_browser`
3. These functions:
   - Lazy-import `playwright.sync_api` / `playwright.async_api`
   - Launch headless Chromium with `timeout` constraint
   - If `auth` provided, set `Authorization` header via `browser.new_context(extra_http_headers=...)`
   - Navigate to URL, wait for `networkidle` or `load` event
   - Extract `page.inner_text("body")`
   - Close browser
   - Apply `_html_to_text` if needed, truncate to `max_length`
4. Add `render_js` pass-through to `complete_with_url` / `acomplete_with_url` in `client.py`
5. Add `browser` optional dependency group in `pyproject.toml`

## Alternatives Considered
| Alternative | Why rejected |
|---|---|
| Selenium | Heavier, worse async support, requires separate driver management |
| pyppeteer | Unmaintained, Playwright is the successor |
| requests-html | Uses pyppeteer internally, same problem |
| Separate `fetch_url_js()` function | Adds API surface; single param is cleaner |

## Risks & Mitigations
| Risk | Mitigation |
|---|---|
| Playwright install is large (~100MB browsers) | Optional dependency, clear docs |
| Browser timeout on slow SPAs | Use existing `timeout` param, default 30s |
| Memory leak from unclosed browsers | `try/finally` ensures cleanup |
| Playwright not available in all CI environments | `render_js` defaults to `False`; unit tests mock Playwright |

## Dependencies
- `playwright>=1.40` (optional, in `[browser]` extra)
- Playwright browser binaries (`playwright install chromium`)

## Test Strategy
- Unit tests: mock Playwright, test render_js branching, error handling, auth injection
- Live tests: extend existing `test_live_urls.py` with `render_js=True` variants
- All existing tests must continue passing unchanged
