# LLM-0006 Developer Notes

## Files Created
- `llm_extender/url_fetcher.py` — `fetch_url`, `afetch_url`, `_html_to_text`, `_build_context_prompt`
- `tests/test_url_fetcher.py` — 14 test cases (TC-1 through TC-14)

## Files Modified
- `llm_extender/client.py` — Added `complete_with_url()` and `acomplete_with_url()` methods to `LLMClient`
- `llm_extender/__init__.py` — Added `fetch_url`, `afetch_url` to `__all__`

## Key Decisions
- Used stdlib `html.parser.HTMLParser` for HTML-to-text (no extra dependency)
- Reused `ProviderError` for HTTP fetch failures (consistent with rest of library)
- `url_auth` parameter accepts `AuthStrategy` — reuses AzureChainedAuth with custom scope for authenticated URL fetches
- Default `max_length=50_000` characters — enough for most pages, avoids token overflow
- `User-Agent: LLMExtender/1.0` sent on all requests

## Test Results
- 111 tests passed, 0 failed
- 19 new tests for URL fetcher + client integration
