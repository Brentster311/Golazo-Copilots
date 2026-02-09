# LLM-0009 Design Doc: CDP Browser Auth

## Summary
Add `browser_auth="cdp"` support to `fetch_url` / `afetch_url` that connects Playwright to the user's real Edge browser via Chrome DevTools Protocol, enabling content fetching from Conditional Access–protected sites.

## Architecture

### New Module: `llm_extender/cdp_browser.py`
Contains all Edge/CDP orchestration logic:
- `_find_edge_executable()` → returns Path to msedge.exe (Windows-specific)
- `_find_edge_user_data_dir()` → returns Path to Edge user profile directory
- `_launch_edge_with_cdp(port, restore_session)` → kills existing Edge, relaunches with `--remote-debugging-port`
- `_fetch_with_cdp_browser(url, timeout, max_length, cdp_port, login_timeout)` → sync fetch via CDP
- `_afetch_with_cdp_browser(...)` → async variant

### Changes to `url_fetcher.py`
- Add `"cdp"` to `_VALID_BROWSER_AUTH` frozenset
- In `fetch_url` / `afetch_url`, route `browser_auth="cdp"` to the new CDP fetcher
- New parameter `cdp_port: int = 9222` on `fetch_url` / `afetch_url`

### Flow
1. Kill existing Edge processes (`taskkill /F /IM msedge.exe`)
2. Relaunch Edge with `--remote-debugging-port={port}` + `--restore-last-session` + `--user-data-dir={profile}`
3. Wait for CDP endpoint to become available (poll `http://localhost:{port}/json/version`)
4. Connect Playwright via `chromium.connect_over_cdp(f"http://localhost:{port}")`
5. Open new tab, navigate to URL
6. If AAD redirect detected → call `wait_for_aad_login(page, login_timeout)` (from LLM-0010)
7. Wait for SPA render (`networkidle` or `domcontentloaded`)
8. Extract text via `page.inner_text("body")`
9. Close the CDP page (not the browser) — leave Edge running for the user
10. Return truncated text

### Dependencies
- Uses `wait_for_aad_login` / `await_for_aad_login` from `aad_browser.py` (LLM-0010)
- Playwright (`[browser]` extra)
- `subprocess` for Edge process management
- `httpx` for CDP endpoint polling
