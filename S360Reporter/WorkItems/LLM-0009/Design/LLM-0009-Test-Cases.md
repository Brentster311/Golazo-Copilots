# LLM-0009 Test Cases

## TC-1: _find_edge_executable returns path on Windows
- Mock `shutil.which` to return a path
- Verify returns Path object

## TC-2: _find_edge_executable raises when Edge not found
- Mock `shutil.which` to return None, mock registry/fallback paths to not exist
- Verify ProviderError raised with guidance

## TC-3: _find_edge_user_data_dir returns correct path
- Mock `os.environ` with LOCALAPPDATA set
- Verify returns expected Edge profile path

## TC-4: fetch_url routes browser_auth="cdp" to CDP fetcher
- Mock `_fetch_with_cdp_browser`
- Call `fetch_url(url, render_js=True, browser_auth="cdp")`
- Verify CDP fetcher called with correct args

## TC-5: afetch_url routes browser_auth="cdp" to async CDP fetcher
- Same as TC-4 but async path

## TC-6: "cdp" is in _VALID_BROWSER_AUTH
- Verify `"cdp" in _VALID_BROWSER_AUTH`

## TC-7: CDP fetch calls wait_for_aad_login when AAD redirect detected
- Mock Playwright CDP connection, mock page.url to return AAD host then target
- Verify `wait_for_aad_login` is called

## TC-8: CDP fetch raises ProviderError when CDP connection fails
- Mock Playwright `connect_over_cdp` to raise
- Verify ProviderError raised

## TC-9: Existing browser_auth="aad" unchanged
- Run existing test_browser_aad.py tests — all must still pass

## TC-10: browser_auth="cdp" does not require auth parameter
- Call with `browser_auth="cdp"` and `auth=None`
- Verify no error (CDP uses browser session, not token)
