# LLM-0006 Design Doc

## Summary
Add URL content fetching to LLM Extender — `fetch_url()` retrieves a web page, strips HTML to text, and `complete_with_url()` / `acomplete_with_url()` inject that content as context for an LLM prompt.

## Problem Statement
LLMs hallucinate when asked about specific topics (e.g., the exact Modern Testing Principles). Feeding actual page content as context produces accurate, grounded answers. Today this requires manual copy-paste. This feature automates it.

## Proposed Approach

### New module: `llm_extender/url_fetcher.py`
- `fetch_url(url, auth=None, timeout=30.0, max_length=50000) -> str`
- Uses `httpx` to GET the URL
- If `auth` provided, resolves token and sends `Authorization: Bearer <token>`
- Strips HTML via stdlib `html.parser` (no new dependencies)
- Truncates to `max_length` characters
- Raises `ProviderError` on HTTP errors

### New methods on `LLMClient`
- `complete_with_url(prompt, url, url_auth=None, max_length=50000) -> str`
- `acomplete_with_url(prompt, url, url_auth=None, max_length=50000) -> str`
- Calls `fetch_url()` / `afetch_url()`, builds context prompt, delegates to provider

### Prompt template
```
Content from {url}:

{content}

{user_prompt}
```

## Alternatives Considered
1. **Add `beautifulsoup4` dependency** — Heavier extraction. Rejected to keep deps minimal. Can follow up.
2. **Separate fetcher class** — Overkill for a utility function. A module-level function is simpler.

## Risks & Mitigations
| Risk | Mitigation |
|------|-----------|
| HTML extraction misses content | stdlib `html.parser` is good enough for most pages; follow-up for BS4 |
| Huge pages blow token limits | `max_length` truncation (default 50K chars) |
| Slow page fetches | Respects `timeout` parameter |
| Auth token for wrong scope | `url_auth` is explicitly separate from LLM auth |

## Dependencies
- `httpx` (already a dependency)
- `html.parser` (stdlib)
- LLM-0005 `AzureChainedAuth` (for authenticated URL fetches)

## Test Strategy
- Mock httpx responses for fetch_url tests
- Test HTML stripping (scripts, styles, tags removed, text preserved)
- Test truncation
- Test auth header injection
- Test HTTP error handling
- Test complete_with_url prompt assembly
- Test async variants
