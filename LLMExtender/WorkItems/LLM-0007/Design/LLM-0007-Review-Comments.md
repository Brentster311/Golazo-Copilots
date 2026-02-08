# LLM-0007 Review Comments

## Design Review

### Approved With Notes
The design is clear and feasible. Notes:

1. **networkidle vs load:** Prefer `load` with a short `wait_for_timeout` fallback rather than `networkidle` — some SPAs never reach network idle due to polling/websockets. Use `domcontentloaded` + a configurable wait.
2. **Auth injection:** `extra_http_headers` is correct for Bearer tokens. For cookie-based auth, a future story could add cookie injection.
3. **Redirect handling:** Playwright handles redirects natively (browser follows them), so the manual redirect loop in the httpx path is not needed for `render_js=True`.
4. **Text extraction:** `page.inner_text("body")` is better than `page.content()` + `_html_to_text` — it gives already-rendered visible text.

### No Scope Changes Required
All feedback is implementation guidance, not scope changes.
