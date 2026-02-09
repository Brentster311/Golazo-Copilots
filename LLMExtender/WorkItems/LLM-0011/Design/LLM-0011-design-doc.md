# LLM-0011 Design Doc: Public Context-Prompt API for Pre-Fetched Content

## Summary
Add `LLMClient.complete_with_context()` / `acomplete_with_context()` methods and a public `build_context_prompt()` utility so consumers can send pre-fetched content to the LLM without importing private functions.

## Problem Statement
`complete_with_url()` bundles fetch + LLM into one call. When content is obtained outside the library (e.g., CDP browser, file read, custom scraper), there is no public API to construct the standard context-augmented prompt and send it to the LLM. Users must import the private `_build_context_prompt`.

## Proposed Approach
1. Rename `_build_context_prompt` → `build_context_prompt` (public) in `url_fetcher.py`
2. Keep `_build_context_prompt` as an alias for backward compat
3. Export `build_context_prompt` from `llm_extender.__init__`
4. Add `complete_with_context(prompt, content, source_url=None)` to `LLMClient`
5. Add async variant `acomplete_with_context`
6. Refactor `complete_with_url` to delegate to `complete_with_context`
7. Add unit tests

## Risks
- None significant — purely additive, no breaking changes

## Dependencies
- None — uses only existing code
