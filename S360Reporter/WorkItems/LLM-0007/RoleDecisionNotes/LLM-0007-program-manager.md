# LLM-0007 Program Manager Notes

## Design Decisions
- Single `render_js` parameter on existing functions rather than new API surface
- Playwright chosen for best Python async support and cross-browser coverage
- Optional dependency group `[browser]` keeps core library lightweight
- Auth injected via `extra_http_headers` in browser context — cleanest approach
