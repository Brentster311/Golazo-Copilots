# SFI-021 — Program Manager Decision Notes

## Work Item
**SFI-021**: URL Content Enrichment for LLM Analysis

## Decisions Made

### Technology: Use `llm-extender` library
- User explicitly requested using `llm-extender` from `C:\repos\Golazo-Copilots\LLMExtender`
- Library already provides `fetch_url()` with HTML stripping, timeout, redirect handling, and `max_length` truncation
- Avoids duplicate implementation in SFIReporter

### Architecture: Parallel fetch with ThreadPoolExecutor
- Up to 6 URLs fetched concurrently (one per known field)
- Per-URL timeout of 10 seconds, total phase capped at 30 seconds
- Results collected as `dict[str, str]` and passed to existing `url_content` parameter

### Scope: Minimal changeset
- Only 3 files need modification: `pyproject.toml`, `llm_client.py`, `tk_app.py`
- Existing `build_prompt()` and `analyze_item()` already support `url_content` parameter
- No changes needed to the analysis modal or result format

### Risk acceptance
- Most enterprise URLs likely auth-gated — accepted as "best-effort" per user story
- Analysis quality degrades gracefully to data-only when URLs are unfetchable

## Open Questions
- None — all design choices confirmed by user story scope and existing codebase patterns
