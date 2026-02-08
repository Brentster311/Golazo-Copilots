# LLM-0006 — Test Cases

## TC-1: fetch_url returns text content from HTML (AC-1)
- Mock httpx to return HTML `<html><body><p>Hello world</p></body></html>`
- Verify returns `"Hello world"` (tags stripped)

## TC-2: fetch_url strips script and style tags (AC-1)
- Mock HTML with `<script>...</script>` and `<style>...</style>` blocks
- Verify script/style content is removed, other text preserved

## TC-3: fetch_url sends Bearer token when auth provided (AC-1)
- Provide a mock AuthStrategy
- Verify Authorization header is `Bearer <token>`

## TC-4: fetch_url with no auth sends no Authorization header (AC-1)
- No auth provided
- Verify no Authorization header sent

## TC-5: fetch_url raises on HTTP error (AC-4)
- Mock httpx to return 404
- Verify `ProviderError` raised with status code in message

## TC-6: fetch_url raises on 401/403 (AC-4)
- Mock httpx to return 401
- Verify `ProviderError` raised mentioning auth

## TC-7: fetch_url truncates to max_length (AC-5)
- Mock HTML with very long text content
- Call with max_length=100
- Verify returned string is <= 100 chars

## TC-8: fetch_url uses httpx (AC-6)
- Verify httpx.Client is used (not urllib or requests)

## TC-9: complete_with_url builds correct prompt (AC-2)
- Mock fetch_url and provider.complete
- Verify the prompt passed to provider includes URL content and user prompt

## TC-10: complete_with_url passes url_auth to fetch (AC-7)
- Provide url_auth
- Verify it's passed to fetch_url, not to the LLM provider

## TC-11: acomplete_with_url async variant (AC-3)
- Mock afetch_url and provider.acomplete
- Verify async flow works end-to-end

## TC-12: fetch_url sets User-Agent header (NFR)
- Verify User-Agent contains "LLMExtender"

## TC-13: fetch_url handles non-HTML content (plain text) (edge case)
- Mock response with Content-Type text/plain
- Verify returns raw text without HTML processing errors

## TC-14: Docstrings present
- Verify fetch_url, complete_with_url, acomplete_with_url have docstrings
