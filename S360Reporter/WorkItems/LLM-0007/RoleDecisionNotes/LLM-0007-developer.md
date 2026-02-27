# LLM-0007 Developer Notes

## Implementation Summary

### Files Modified
- **llm_extender/url_fetcher.py** — Added `render_js` parameter and headless browser support
- **llm_extender/client.py** — Added `render_js` passthrough to `complete_with_url` / `acomplete_with_url`
- **pyproject.toml** — Added `[browser]` optional dependency group

### Files Created
- **tests/test_render_js.py** — 15 test functions covering TC-1 through TC-13

### Design Decisions

1. **Lazy imports with patchable sentinels**: Playwright is imported lazily via `_import_sync_playwright()` / `_import_async_playwright()`. Module-level sentinels (`sync_playwright = None`, `async_playwright = None`) allow tests to inject mocks. The `_get_sync_playwright()` / `_get_async_playwright()` helpers check the sentinel first (non-None = test mock), then fall back to real import.

2. **Clear install message**: When Playwright is missing, `ProviderError` includes: `pip install llm-extender[browser] && playwright install chromium`.

3. **Auth injection**: Bearer tokens are injected via `extra_http_headers` on the Playwright browser context, matching how httpx sends Authorization headers.

4. **domcontentloaded + wait**: Uses `page.wait_for_load_state("domcontentloaded")` per architect review feedback (not `networkidle` which can hang on long-polling SPAs).

5. **Timeout in ms**: Playwright uses milliseconds; the function converts the `timeout` (seconds) parameter to `timeout_ms = timeout * 1000`.

6. **Resource cleanup**: `browser.close()` is always called in a `finally` block, whether fetch succeeds or fails.

### Test Results
- 15 new tests pass (test_render_js.py)
- 129 total unit tests pass (no regressions)
- 6 live integration tests pass separately
