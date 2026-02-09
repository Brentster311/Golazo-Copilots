# SFI-021 Developer Role Decision Notes

## Implementation Summary

### TDD Red Phase
- Wrote 9 test cases in `SFIReporter/tests/test_llm_client.py`:
  - `TestFetchActionItemUrls` (7 tests): TC-21-1,2,4,5,6,8,9
  - `TestBuildPromptURLContentTruncation` (1 test): TC-21-7
  - `TestAnalyzeItemURLContent` (1 test): TC-21-10
- Confirmed 7 tests failed with `ImportError: cannot import name 'fetch_action_item_urls'`
- 2 tests passed (testing existing `build_prompt`/`analyze_item` with `url_content` param)

### TDD Green Phase
- Added `fetch_action_item_urls()` to `SFIReporter/src/sfi_reporter/llm_client.py`
- Added helper `_extract_urls()` for URL extraction from 6 fields
- Added `llm-extender>=0.1.0` dependency to `SFIReporter/pyproject.toml`
- Wired URL fetching into `_launch_llm_analysis()` in `tk_app.py`
- All 188 tests pass, 1 skipped, 0 failures

## Files Changed

| File | Change |
|------|--------|
| `SFIReporter/src/sfi_reporter/llm_client.py` | Added imports (`fetch_url`, `ProviderError`, `re`, `ThreadPoolExecutor`), `_extract_urls()`, `fetch_action_item_urls()` |
| `SFIReporter/src/sfi_reporter/tk_app.py` | Added `fetch_action_item_urls` import, wired URL fetching before `analyze_item()` call |
| `SFIReporter/pyproject.toml` | Added `llm-extender>=0.1.0` to dependencies |
| `SFIReporter/tests/test_llm_client.py` | Added 9 SFI-021 test cases |

## Key Design Decisions

1. **`_extract_urls()` as separate helper**: Keeps URL extraction testable and separate from the fetch logic.
2. **`_RESOURCE_URI_SPLIT_RE = re.compile(r"[;\s,]+")`**: Splits ResourceURIs on semicolons, commas, and whitespace as per design doc.
3. **Dedup via `seen` set**: Prevents fetching the same URL twice if it appears in multiple fields.
4. **`ThreadPoolExecutor(max_workers=6)`**: Concurrent fetching with cap at 6 threads per design.
5. **`fetch_url(url, timeout=10, max_length=1500)`**: Short timeout (10s) and limited content (1500 chars) per design to avoid prompt bloat.
6. **Catch `ProviderError` + generic `Exception`**: Graceful degradation — failed URLs are silently skipped with debug logging.
7. **Progress modal status**: Added "Fetching URL context..." step before "Calling Azure OpenAI..." for user feedback.

## Test Verification

```
python -m pytest tests/ -v --tb=short
======================= 188 passed, 1 skipped in 3.24s ========================
```
