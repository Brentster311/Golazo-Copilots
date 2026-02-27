# LLM-0010 Design Doc: Reusable AAD Login-Wait Helper

## Summary
Extract the AAD login polling loop into `wait_for_aad_login(page, timeout)` / `await_for_aad_login(page, timeout)` helpers in `aad_browser.py`. Refactor `_fetch_with_browser` and `_afetch_with_browser` to use them.

## Proposed Approach
1. Add `wait_for_aad_login(page, timeout)` (sync) to `aad_browser.py`
2. Add `await_for_aad_login(page, timeout)` (async) to `aad_browser.py`
3. Both poll `page.url` every 1s, return when URL leaves AAD domains
4. Raise `AuthenticationError` on timeout
5. Refactor `_fetch_with_browser` to use the helper after device-code flow
6. Refactor `_afetch_with_browser` similarly
7. LLM-0009 (CDP) will also use these helpers
