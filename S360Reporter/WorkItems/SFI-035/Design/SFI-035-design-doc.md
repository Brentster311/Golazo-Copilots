# SFI-035 Design Doc — LLM Analysis Sources Provenance Card

## Summary
Add a visible "Sources" provenance summary to the Copilot Chat panel that appears **before** the LLM streaming response when the user triggers "Analyze with LLM". This tells the user exactly which documentation URLs were extracted and whether each was successfully fetched, enabling them to trust (or question) the LLM's analysis.

## Problem Statement
When a user right-clicks a KPI and selects "Analyze with LLM", the system silently collects URLs from action-item fields, fetches their content, embeds it into a prompt, and streams the LLM response. The user sees only the LLM's summary — they have no visibility into:
1. **Which URLs** the system extracted from the action items
2. **Whether each URL was actually fetched** vs. returned an error (HTTP 403, timeout, non-text content, etc.)

This lack of transparency undermines trust in the analysis. A summary based on 0 successfully fetched docs is qualitatively different from one based on 5.

## Business Case
- **Why now**: Users are actively using the LLM analysis feature and reporting trust concerns.
- **Impact**: Directly improves user confidence in an existing feature with zero new infrastructure.
- **KPIs**: Feature already exists; this is a UX quality improvement.

## Stakeholders
- S360Reporter end users (security/compliance engineers)
- Feature maintainers (S360Reporter codebase owners)

## Functional Requirements
1. `analyze_kpi()` returns a structured result containing: `prompt` (str), `urls_found` (list of URLs), `fetch_results` (list of {url, status, content_length, error})
2. Before the LLM response streams, a "Sources" card is rendered in the chat panel
3. The Sources card shows: total URLs found, successes, failures
4. Each URL is listed with ✅/❌ status, content length (if success), error message (if failure)
5. If zero URLs found, display "No documentation URLs found in action items"

## Non-Functional Requirements
- Sources card renders in < 100 ms (local data only, no I/O)
- No additional network requests beyond existing fetch phase
- Backward-compatible: if any caller still passes a bare string, handle gracefully

## Proposed Approach

### Data Model Change (kpi_analyzer.py)
Add a `dataclass` for structured results:

```python
@dataclass
class AnalysisResult:
    prompt: str
    urls_found: list[str]
    fetch_results: list[dict]  # [{url, ok, chars, error}]
```

Refactor `fetch_all_urls()` to return richer metadata (not just `{url: content}`). Refactor `analyze_kpi()` to return `AnalysisResult` instead of `str`.

### UI Change (copilot_panel.py)
Add `_show_sources_card(result: AnalysisResult)` method that inserts a formatted "system" message with the provenance summary before `_do_send_analysis` fires the LLM prompt.

### Caller Change (dialogs.py)
Update `_bg_analyze()` to unpack `AnalysisResult`, pass metadata to `send_analysis_prompt()`.

### API Update (copilot_panel.py)
Update `send_analysis_prompt()` signature to accept optional `sources_metadata` parameter. If present, render the sources card before streaming.

## Alternatives Considered

| Alternative | Reason for rejection |
|---|---|
| Embed provenance inside the LLM prompt | Would consume tokens and not guarantee the LLM surfaces it in its response |
| Add provenance to a separate log file | Users wouldn't check a log; needs to be in-context |
| Pop up a separate dialog | Disruptive UX; the chat panel is the natural home |

## Risks & Mitigations
| Risk | Mitigation |
|---|---|
| Breaking existing callers of `analyze_kpi` | Return `AnalysisResult` with a `.prompt` property; callers that used `str(result)` still get the prompt via `__str__` |
| Sources card is too verbose for many URLs | Already capped at `_MAX_URLS=10`; no change needed |

## Open Questions
None — scope is well-defined.

## Dependencies
- No new external dependencies
- Builds on existing `kpi_analyzer.py`, `copilot_panel.py`, `dialogs.py`

## Migration / Rollout / Rollback
- **Rollout**: Replace in-place; no feature flag needed (small, self-contained change)
- **Rollback**: Revert the 3 files to restore previous behavior
- **Data migration**: None

## Observability Plan
- Existing `logger.info` in `analyze_kpi` already logs URL counts
- No new telemetry endpoints needed

## Test Strategy Summary
- **Unit tests**: Test `AnalysisResult` construction, `fetch_url_content` metadata shape, `build_analysis_prompt` with structured data
- **Integration test**: Mock URL fetches, verify `analyze_kpi` returns correct `AnalysisResult` with expected fields
- **UI test**: Verify `_show_sources_card` formats output correctly (can be tested by calling the method with mock data and checking the chat display widget text)
