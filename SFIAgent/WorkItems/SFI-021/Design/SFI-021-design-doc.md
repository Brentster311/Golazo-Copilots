# SFI-021 Design Doc: URL Content Enrichment for LLM Analysis

## Summary

Enhance the existing "Analyze with LLM" feature (SFI-020) to fetch web content from URLs embedded in action item fields before calling the LLM. This gives the model richer context — remediation wikis, asset details, grouping links — producing more accurate, actionable analyses.

## Problem Statement

Today the LLM analysis relies solely on structured data fields (title, SLA, dates, remediation text). Many action items contain URLs pointing to detailed remediation guides, asset inventories, and wiki pages. Without this content the LLM often produces generic advice rather than specific, context-aware remediation steps.

## Business Case

- **Why now**: SFI-020 (core LLM analysis) is shipped. The #1 user feedback is "the analysis doesn't know about the wiki content."
- **Impact**: More specific remediation steps → faster engineer triage → fewer SLA breaches.
- **KPI**: Reduction in re-analyze rate (users won't need to manually paste wiki content).

## Stakeholders

- SFI Engineers (end users)
- ACCIA Team (development)

## Functional Requirements

1. Extract non-empty URLs from action item fields: `ResourceURIs`, `ActionWikiLink`, `CustomGroupingLink`, `AssetTypeLink0`, `AssetTypeLink1`, `AssetTypeLink2`
2. Fetch each URL, strip HTML to plain text
3. Pass fetched content as additional context in the LLM prompt via the existing `url_content` parameter in `build_prompt()` / `analyze_item()`
4. Skip URLs that return 401/403 (auth-gated) or time out — log but don't block
5. Update progress modal status to show URL fetching phase

## Non-Functional Requirements

- Per-URL timeout: 10 seconds
- Total URL fetch phase: ≤ 30 seconds (parallel via `ThreadPoolExecutor`)
- No credentials sent to arbitrary URLs
- Per-URL content truncated to 1500 chars (existing `_truncate` in `build_prompt`)
- Windows primary platform

## Proposed Approach

### Technology Choice: `llm-extender` library

The `llm_extender.url_fetcher.fetch_url()` function from `C:\repos\Golazo-Copilots\LLMExtender` already provides:
- HTTP fetching with configurable timeout
- HTML-to-text stripping (stdlib `HTMLParser`, no external deps)
- Redirect following (up to 10 hops)
- `max_length` truncation
- Proper error handling via `ProviderError`

This avoids reimplementing URL fetching logic in SFIReporter.

### Architecture

```
_launch_llm_analysis(parent, item)
  ├── progress.update_status("Fetching URL content...")
  ├── url_content = fetch_action_item_urls(item)  ← NEW
  ├── progress.update_status("Calling Azure OpenAI...")
  ├── result = analyze_item(item, config, url_content=url_content)
  ├── save_analysis(result)
  └── AnalysisModal(root, result)
```

### New function: `fetch_action_item_urls(item, timeout_per_url=10, max_total=30)`

Located in `llm_client.py`:

1. Extract URLs from the 6 known fields
2. Filter out empty/None values
3. Use `ThreadPoolExecutor` to fetch in parallel (max 6 workers)
4. Each worker calls `llm_extender.url_fetcher.fetch_url(url, timeout=10, max_length=1500)`
5. Catch `ProviderError` per-URL — log and skip
6. Return `dict[str, str]` mapping URL → content (only successful fetches)

### Changes Required

| File | Change |
|------|--------|
| `SFIReporter/pyproject.toml` | Add `llm-extender>=0.1.0` dependency |
| `SFIReporter/src/sfi_reporter/llm_client.py` | Add `fetch_action_item_urls()` function |
| `SFIReporter/src/sfi_reporter/tk_app.py` | Wire URL fetching into `_launch_llm_analysis()` |

### Existing infrastructure already supports this

- `build_prompt(item, url_content=...)` already accepts `url_content` dict
- `analyze_item(item, config, url_content=...)` already passes it through
- No changes needed to prompt building or analysis result structure

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| Use `requests` directly | Duplicates HTML stripping, redirect handling already in `llm_extender` |
| Use `beautifulsoup4` for HTML | Adds a heavy dependency; stdlib `HTMLParser` in `llm_extender` is sufficient |
| Fetch URLs synchronously | Would exceed 30s budget with 6 URLs × 10s timeout each |
| Cache URL content | Out of scope per user story; adds complexity for minimal benefit |

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Most URLs are SSO-gated → empty enrichment | Best-effort by design; analysis still works with structured data alone |
| Slow URLs delay analysis UX | Per-URL timeout (10s) + parallel fetch + 30s total cap |
| Fetched content is garbage (JS-heavy pages) | `llm_extender` strips scripts/styles; worst case is low-quality text that LLM ignores |

## Dependencies

- `llm-extender` library (local, `C:\repos\Golazo-Copilots\LLMExtender`)
- SFI-020 must be implemented (it is)

## Rollout / Rollback

- **Rollout**: Add URL fetching to the analysis pipeline. Feature is additive.
- **Rollback**: Remove `fetch_action_item_urls()` call from `_launch_llm_analysis()`. LLM falls back to data-only analysis.

## Observability

- Log count of URLs attempted vs. successfully fetched per analysis
- Log per-URL fetch time and skip reason (timeout, 401/403, error)

## Test Strategy

- Unit test `fetch_action_item_urls()` with mocked `fetch_url`
- Test extraction of URLs from various action item field combos
- Test timeout/error handling (mocked `ProviderError`)
- Test that `build_prompt` includes URL content when provided (already tested in TC-4)
- Test `_launch_llm_analysis` integration with URL fetching (mocked)
