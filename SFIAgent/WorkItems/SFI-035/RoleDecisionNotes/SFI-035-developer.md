# SFI-035 — Developer Decision Notes

## Implementation Summary

### New code in `kpi_analyzer.py`
- **`FetchResult` dataclass**: Typed container for individual URL fetch results with `url`, `ok`, `chars`, `error` fields
- **`AnalysisResult` dataclass**: Structured return type from `analyze_kpi` with `prompt`, `urls_found`, `fetch_results`. Includes `__str__` for backward compatibility.
- **`_fetch_with_provenance()`**: Internal helper that calls existing `fetch_all_urls()` and builds `FetchResult` list from the returned content mapping
- **`format_sources_card()`**: Pure function that formats `AnalysisResult` into a human-readable provenance summary string

### Modified code
- **`analyze_kpi()`** return type changed from `str` to `AnalysisResult`
- **`dialogs.py` `_bg_analyze()`**: Unpacks `AnalysisResult`, passes `sources_metadata` to `send_analysis_prompt`
- **`copilot_panel.py` `send_analysis_prompt()`**: Added optional `sources_metadata` kwarg
- **`copilot_panel.py` `_do_send_analysis()`**: Calls `_show_sources_card()` before LLM streaming if metadata provided
- **`copilot_panel.py` `_show_sources_card()`**: New method that renders the provenance card via `_append_message("system", ...)`

### Test results
- 15 new tests in `test_sfi_035.py` — all pass
- 15 existing tests in `test_sfi_034.py` — all pass (no regressions)
- 37 pre-existing failures in `test_sfi_026.py` / `test_sfi_029.py` (unrelated `OrgAncestry` import errors)

### TDD compliance
- Tests written first (red phase: import errors confirmed)
- Production code implemented to make tests pass (green phase: 30/30 pass)
