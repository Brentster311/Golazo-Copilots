# SFI-035 — Builder Decision Notes

## Build verification
- **Command**: `python -m pytest tests/test_sfi_034.py tests/test_sfi_035.py -q --tb=short`
- **Result**: 30 passed in 0.05s
- **No build errors or warnings**

## Files changed
- **Modified**: `GUI/src/sfi_reporter/kpi_analyzer.py` — added `FetchResult`, `AnalysisResult`, `format_sources_card`, `_fetch_with_provenance`; refactored `analyze_kpi` return type
- **Modified**: `GUI/src/sfi_reporter/dialogs.py` — updated `_bg_analyze` to unpack `AnalysisResult`
- **Modified**: `GUI/src/sfi_reporter/copilot_panel.py` — added `sources_metadata` kwarg, `_show_sources_card` method
- **New**: `GUI/tests/test_sfi_035.py` — 15 tests
- **New**: 9 WorkItems documents (user story, design, review, test cases, 5 role notes)

## Git operations
Branch creation and commit deferred to user.
