# LLM-0007 Test Cases

## TC-1: render_js=False is default (no change)
- Call `fetch_url(url)` without render_js — uses httpx, not Playwright
- **Expected:** Same behavior as LLM-0006

## TC-2: render_js=True launches browser and extracts text
- Call `fetch_url(url, render_js=True)` with mocked Playwright
- **Expected:** Browser launched, page navigated, `inner_text("body")` returned

## TC-3: render_js=True async variant
- Call `afetch_url(url, render_js=True)` with mocked async Playwright
- **Expected:** Async browser launched, page navigated, text returned

## TC-4: Playwright not installed raises clear error
- Call `fetch_url(url, render_js=True)` when playwright is not importable
- **Expected:** `ProviderError` with message containing "pip install llm-extender[browser]"

## TC-5: Playwright not installed (async variant)
- Call `afetch_url(url, render_js=True)` when playwright is not importable
- **Expected:** `ProviderError` with message containing install instructions

## TC-6: Auth token injected into browser context
- Call `fetch_url(url, render_js=True, auth=mock_auth)` with mocked Playwright
- **Expected:** `browser.new_context()` called with `extra_http_headers` containing `Authorization: Bearer <token>`

## TC-7: Auth token injected (async variant)
- Call `afetch_url(url, render_js=True, auth=mock_auth)` 
- **Expected:** Async context created with auth header

## TC-8: Browser closed after fetch (resource cleanup)
- Call `fetch_url(url, render_js=True)` with mocked Playwright
- **Expected:** `browser.close()` called even if page navigation fails

## TC-9: Content truncated to max_length
- Call `fetch_url(url, render_js=True, max_length=50)` returning long content
- **Expected:** Returned text ≤ 50 characters

## TC-10: complete_with_url passes render_js through
- Call `client.complete_with_url(prompt, url, render_js=True)` with mocked provider
- **Expected:** `fetch_url` called with `render_js=True`

## TC-11: acomplete_with_url passes render_js through
- Call `client.acomplete_with_url(prompt, url, render_js=True)` with mocked provider
- **Expected:** `afetch_url` called with `render_js=True`

## TC-12: Timeout passed to browser
- Call `fetch_url(url, render_js=True, timeout=5.0)` with mocked Playwright
- **Expected:** Browser launch and page navigation use the timeout value

## TC-13: Docstrings present
- Verify updated `fetch_url`, `afetch_url` docstrings mention `render_js`
- **Expected:** Docstrings contain "render_js"
