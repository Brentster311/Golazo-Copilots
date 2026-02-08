# LLM-0007 Architect Notes

## Architectural Review — Approved

### API Contract
- `render_js: bool = False` on `fetch_url` / `afetch_url` — clean, backward-compatible
- `complete_with_url` / `acomplete_with_url` pass `render_js` through — consistent

### Security
- Browser runs headless, no GUI exposure
- Auth via `extra_http_headers` — token never written to disk or browser storage
- Browser context destroyed after each call — no state leaks

### Dependency Isolation
- Playwright lazy-imported only when `render_js=True` — zero impact on non-browser users
- `[browser]` optional dep group — explicit opt-in

### Resource Management
- `try/finally` pattern ensures browser cleanup even on exceptions
- Timeout covers entire browser lifecycle (launch + navigate + extract + close)

### No Scope Changes
Design is architecturally sound. Proceed to implementation.
