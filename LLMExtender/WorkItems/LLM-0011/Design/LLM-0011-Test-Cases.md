# LLM-0011 — Test Cases

## TC-1: build_context_prompt is public and exported
- `from llm_extender import build_context_prompt` succeeds
- Returns `"Content from {url}:\n\n{content}\n\n{prompt}"` format

## TC-2: _build_context_prompt alias still works
- `from llm_extender.url_fetcher import _build_context_prompt` succeeds
- Returns same result as `build_context_prompt`

## TC-3: complete_with_context sends augmented prompt to provider
- Call `client.complete_with_context("summarize", "page text", source_url="https://example.com")`
- Verify provider receives prompt in context format
- Verify response is returned

## TC-4: complete_with_context without source_url
- Call `client.complete_with_context("summarize", "page text")`
- Verify prompt uses "Content:\n\n{content}\n\n{prompt}" format (no URL)

## TC-5: acomplete_with_context async variant
- Call `await client.acomplete_with_context("summarize", "page text", source_url="https://example.com")`
- Verify async provider receives augmented prompt

## TC-6: complete_with_url delegates to complete_with_context
- Verify that complete_with_url internally uses complete_with_context (via mock)
