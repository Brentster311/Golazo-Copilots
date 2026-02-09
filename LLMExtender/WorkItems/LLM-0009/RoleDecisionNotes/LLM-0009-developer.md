# LLM-0009 Developer Notes

## Changes Made

### New: `llm_extender/cdp_browser.py`
- `_find_edge_executable()` — locates msedge.exe via `shutil.which` + fallback paths
- `_find_edge_user_data_dir()` — returns `%LOCALAPPDATA%\Microsoft\Edge\User Data`
- `_launch_edge_with_cdp(port, url)` — kills existing Edge, relaunches with `--remote-debugging-port` + `--restore-last-session`
- `_wait_for_cdp_ready(port, timeout)` — polls CDP endpoint until responsive
- `_fetch_with_cdp_browser(url, timeout, max_length, cdp_port, login_timeout)` — sync CDP fetch
- `_afetch_with_cdp_browser(...)` — async variant
- `_find_target_page(browser, target_url)` — finds matching tab or falls back to last page
- Uses `wait_for_aad_login` / `await_for_aad_login` from LLM-0010

### Modified: `llm_extender/url_fetcher.py`
- `_VALID_BROWSER_AUTH` now includes `"cdp"`
- `fetch_url` routes `browser_auth="cdp"` to `_fetch_with_cdp_browser`
- `afetch_url` routes `browser_auth="cdp"` to `_afetch_with_cdp_browser`

### New: `tests/test_cdp_browser.py`
- 12 tests covering TC-1 through TC-10
- Edge discovery, CDP routing, AAD redirect handling, connection failure, regression

## Test Results
- 12/12 new tests pass
- 166/166 full suite passes (zero regressions)
