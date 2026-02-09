# LLM-0010 Developer Notes

## Changes Made

### `llm_extender/auth/aad_browser.py`
- Added `import asyncio, time` at module level
- Added `wait_for_aad_login(page, timeout, *, poll_interval)` — sync helper that polls `page.url` every `poll_interval` seconds, returns when URL leaves AAD domains, raises `AuthenticationError` on timeout
- Added `await_for_aad_login(page, timeout, *, poll_interval)` — async equivalent using `asyncio.sleep`
- Both share `detect_aad_redirect()` for host matching

### `llm_extender/url_fetcher.py`
- `_fetch_with_browser`: imports `wait_for_aad_login`, calls it after device-code re-navigation
- `_afetch_with_browser`: imports `await_for_aad_login`, calls it after device-code re-navigation

### `tests/test_aad_login_wait.py` (new)
- 9 tests covering TC-1 through TC-4
- TC-1: sync returns when URL leaves AAD (3 variants: normal, immediate, all AAD hosts)
- TC-2: sync raises on timeout (2 variants: basic + error message check)
- TC-3: async variants (3 tests: return, timeout, immediate)
- TC-4: regression — `_fetch_with_browser` calls `wait_for_aad_login` after refactor

## Test Results
- 9/9 new tests pass
- 154/154 full suite passes (zero regressions)

## Design Decisions
- `poll_interval` is keyword-only with a default of 1.0s for production use; tests use 0.01s for speed
- Helpers accept `Any` for the page parameter to avoid tight coupling to Playwright types
- Placed in `aad_browser.py` since these are AAD-specific login detection utilities
- LLM-0009 (CDP) will reuse these helpers for its own AAD login wait loop
