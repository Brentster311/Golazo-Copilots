# SFI-034 Developer Decision Notes

## Overview
Implemented the "Analyze with LLM" feature per the approved design. Right-clicking a KPI row triggers analysis of all items for that KPI, fetches documentation from embedded URLs, and sends a structured prompt to the Copilot Chat panel asking four questions (What, Why, Where, How).

## Implementation Summary

### New Module: `kpi_analyzer.py`
- **`collect_urls(items)`** — Extracts and deduplicates HTTP/HTTPS URLs from 7 item fields (`url`, `ActionWikiLink`, `Remediation`, `AssetTypeLink0/1/2`, `CustomGroupingLink`)
- **`fetch_url_content(url)` / `fetch_all_urls(urls)`** — Fetches URL content with `urllib.request`, strips HTML via `_HTMLTextExtractor(HTMLParser)`, uses `ThreadPoolExecutor(5)` for parallelism
- **`build_analysis_prompt(items, fetched_docs)`** — Builds structured prompt with item summaries (capped at 30) and fetched documentation, poses the 4 required questions
- **`analyze_kpi(app, kpi_id)`** — Main entry point: filters items by KPI, collects URLs, fetches content, builds prompt
- Constants: `_MAX_CONTENT_PER_URL=4000`, `_MAX_ITEMS_IN_PROMPT=30`, `_URL_FETCH_TIMEOUT=10`, `_MAX_URLS=10`

### Modified: `copilot_panel.py`
- **`send_analysis_prompt(prompt)`** — Thread-safe method to inject an analysis prompt into the Copilot Chat. Marshals to Tk main thread via `self.after(0, ...)`
- **`_do_send_analysis(prompt)`** — Shows prompt as user message, sets "Analyzing…" status, sends to Copilot session

### Modified: `dialogs.py`
- **`_launch_llm_analysis(parent, item)`** — Replaced stub (was `messagebox.showinfo "not yet implemented"`) with real implementation:
  - Validates `_kpi_id` present on item (shows `showwarning` if missing)
  - Finds app via `_find_app(parent)` → `widget.winfo_toplevel()._sfi_app`
  - Opens Copilot panel if closed
  - Shows "Fetching KPI docs…" status
  - Runs `analyze_kpi()` on background thread to avoid UI freeze
  - On completion, sends prompt to Copilot panel via `send_analysis_prompt()`
- **`_find_app(widget)`** — New helper: discovers `SFIReporterApp` instance via `root._sfi_app` attribute

### Modified: `app.py`
- Added `self.root._sfi_app = self` in `__init__` so widgets can discover the app instance

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| `urllib.request` instead of `requests` | Zero new dependencies; `requests` is not in project deps |
| `html.parser.HTMLParser` subclass for HTML stripping | stdlib only; avoids BeautifulSoup dependency |
| `ThreadPoolExecutor(max_workers=5)` | Balances parallelism with being a polite HTTP citizen |
| Content truncation at 4000 chars per URL | Prevents prompt bloat; most docs convey intent in first 4K |
| Cap items at 30 in prompt | Keeps prompt within token limits for LLM |
| Background thread for URL fetching | Prevents Tk main loop freeze during network I/O |
| `root._sfi_app` pattern for app discovery | `SFIReporterApp` is not a widget — can't use Tk widget tree traversal. Attribute on root is simple and reliable |
| `session.idle` for response finalization | Avoids premature finalization on `assistant.turn_end` during multi-turn tool calls (established in SFI-033) |

## Test Results

### New Tests: `test_sfi_034.py` — 15/15 PASSED
- `TestCollectUrls` (4 tests): URL extraction, deduplication, HTTP-only filtering, empty input
- `TestExtractText` (3 tests): HTML stripping, plain text passthrough, script/style removal
- `TestTruncateContent` (3 tests): no-op when short, truncation with ellipsis, exact boundary
- `TestBuildAnalysisPrompt` (5 tests): 4-question structure, item cap at 30, doc inclusion, no-docs handling, empty items

### Updated Tests: `test_sfi_033.py` — 26 passed, 1 skipped
- Updated `TestLLMAnalysisStub` → `test_analyze_with_llm_no_kpi_id_shows_warning`: verifies `showwarning` when item lacks `_kpi_id`
- `test_stub_has_no_llm_imports`: still passes (confirms no old LLM module imports)

### Pre-existing Failures (not related to SFI-034)
- `test_sfi_029`: 10 failures due to `OrgAncestry` import issue (pre-existing)

## Risk Notes
- URL fetching depends on network availability; timeouts and errors are handled gracefully (logged, skipped)
- Large KPIs with many items may produce long prompts; mitigated by 30-item cap and content truncation
- HTML extraction is best-effort; some pages may not yield useful text (handled by fallback regex stripping)
