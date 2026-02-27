# SFI-025 — Developer Decision Notes

## Work Item
**ID**: SFI-025  
**Title**: Configure LLM — GUI dialog with manual entry and auto-detect

## Implementation Summary

### Files Changed
- **`src/sfi_reporter/tk_app.py`**: Added `ConfigureLLMDialog` class (~170 lines), `_load_llm_config()` function, "Configure LLM" button in controls row, updated `_launch_llm_analysis()` to use `_load_llm_config()`.

### Files Created
- **`tests/test_sfi_025.py`**: 13 test cases covering all acceptance criteria.

### Implementation Decisions

1. **ConfigureLLMDialog placed before SFIReporterApp class**: Consistent with other modal classes in the file (ColumnSelectorDialog, DetailModal, etc.).

2. **`_load_llm_config()` as a module-level function**: Mirrors the existing `_load_setting`/`_save_setting` pattern. Used by both `_launch_llm_analysis()` and potentially other callers.

3. **LLMExtender → S360Reporter config mapping**: `discover_azure_configs()` returns `llm_extender.config.LLMConfig` with `base_url`. The dialog maps `base_url → endpoint` when populating fields. The combo display shows `endpoint — deployment (model)`.

4. **Lazy import of `discover_azure_configs`**: Imported inside `_on_auto_detect` thread to avoid import-time failures when Azure SDK isn't installed.

5. **Clear sets empty strings, not None**: `_save_setting("llm_endpoint", "")` rather than deleting the key. `_load_llm_config()` checks `endpoint.strip()` truthiness to determine if saved config exists.

6. **Endpoint validation**: Simple `startswith("https://")` check. More sophisticated URL validation not needed for this use case.

## Test Results
- 13/13 SFI-025 tests passing
- 230/231 total tests passing (1 pre-existing flaky test: `test_llm_storage.py::TestLoadAnalysis::test_round_trip` — file permission issue on Windows, unrelated)

## TDD Cycle
1. **Red**: Wrote all 13 tests first → all failed (no `ConfigureLLMDialog`, no `llm_config_btn`, no `_load_llm_config`)
2. **Green**: Implemented `ConfigureLLMDialog`, button, `_load_llm_config()`, updated `_launch_llm_analysis()` → all 13 pass
3. **Refactor**: No refactoring needed — implementation is clean and minimal
