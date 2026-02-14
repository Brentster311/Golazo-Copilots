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

---

## Architect Notes

### Architectural alignment
- Change is confined to the `kpi_analyzer` → `dialogs` → `copilot_panel` call chain. No new modules, no new dependencies, no new I/O paths. Well-contained.

### API contract: `AnalysisResult`
The `AnalysisResult` dataclass is the primary new contract:
```python
@dataclass
class FetchResult:
    url: str
    ok: bool
    chars: int
    error: str

@dataclass
class AnalysisResult:
    prompt: str
    urls_found: list[str]
    fetch_results: list[FetchResult]
```
**Recommendation**: Use typed `FetchResult` dataclass instead of `dict` for each fetch result. This makes the contract self-documenting and catches key typos at construction time.

### Backward compatibility
- `analyze_kpi` return type changes from `str` to `AnalysisResult`. Only one caller exists (`_bg_analyze` in `dialogs.py`), which we control. No external API surface.
- `build_analysis_prompt` signature is unchanged — it still returns `str`. The wrapping happens in `analyze_kpi`.
- `send_analysis_prompt` gains an optional `sources_metadata` kwarg — additive, no breaking change.

### Security review
- No new network calls, no new user inputs, no new file I/O. URL content is already sanitized by `extract_text`. Provenance display uses `_append_message` which inserts into a disabled Tk Text widget — no injection risk.

### Failure isolation
- If `AnalysisResult` construction fails, the existing `except` block in `_bg_analyze` handles it. No new failure modes introduced.

### No architectural escalation needed
No new User Stories required — the change is purely additive within existing boundaries.
