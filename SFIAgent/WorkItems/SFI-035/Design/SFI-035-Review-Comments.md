# SFI-035 — Design Review Comments

## Overall Assessment
Design is clear, small, and well-scoped. The approach of adding an `AnalysisResult` dataclass and rendering a "Sources" card in the existing chat panel is sound. A few items to tighten.

## Comments

### 1. `AnalysisResult.__str__` for backward compatibility (Low)
Good idea to add `__str__` returning `.prompt`. Verify that `_send_prompt` receives a `str` — if the panel calls `len(prompt)` or slices it, `AnalysisResult` must handle that gracefully. **Recommendation**: Keep it simple — always extract `.prompt` at the caller boundary (in `_bg_analyze`) rather than relying on duck typing.

### 2. `fetch_results` shape (Medium)
The design doc says `list[dict]` with keys `{url, ok, chars, error}`. Pin this down:
- `ok: bool` — was the fetch successful?
- `chars: int` — character count of extracted text (0 if failed)
- `error: str` — empty string if success, error message if failure
- `url: str` — the URL

This should be a `dataclass` or `TypedDict` to avoid magic-string keys.

### 3. Zero-URL edge case (Low)
Design says "No documentation URLs found in action items" — confirm the Sources card still renders (not skipped) so the user knows the system looked and found nothing, rather than wondering if it ran.

### 4. Ordering of URLs (Low)
`collect_urls` returns a `set` — the Sources card should display URLs in a stable order (sorted). Already done in `fetch_all_urls` with `sorted(urls)[:max_urls]`.

### 5. No scope changes identified
The design stays within the user story scope. No new features or behavioral changes beyond the provenance display.
