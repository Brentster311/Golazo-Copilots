# SFI-020 — Developer Decision Notes

## Work Item
**SFI-020**: Right-Click KPI Row → Analyze with LLM (Core)

## Implementation Summary

### Files Created
| File | Purpose |
|------|---------|
| `GUI/src/sfi_reporter/llm_client.py` | LLMConfig, build_prompt, analyze_item, AnalysisResult, _parse_sections |
| `GUI/src/sfi_reporter/llm_storage.py` | save_analysis, load_analysis, analysis_exists (atomic writes, %LOCALAPPDATA%) |
| `GUI/tests/test_llm_client.py` | 23 tests — config, prompt, analyze, parsing, truncation, security |
| `GUI/tests/test_llm_storage.py` | 10 tests — save, load, exists, atomic write, corruption, sanitization |

### Files Modified
| File | Changes |
|------|---------|
| `GUI/src/sfi_reporter/tk_app.py` | `<Button-3>` bindings on `tree_kpis` and `DetailModal` treeview; context menu handler; `AnalysisProgressModal`; `AnalysisModal`; `_analyze_with_llm()`, `_on_analysis_complete()`, `_on_analysis_error()` functions |
| `pyproject.toml` | Added `openai>=1.0.0` dependency |

### QA Review Items Addressed
1. ✅ **Concurrent analysis guard**: `_analysis_in_progress` flag prevents multiple simultaneous LLM calls
2. ✅ **Row selection on right-click**: `identify_row()` + `selection_set()` called before posting context menu
3. ✅ **Empty/missing field handling**: `_format_item_for_prompt` uses "N/A" for missing fields
4. ✅ **Progress modal dismissal**: `WM_DELETE_WINDOW` override prevents close while analysis running
5. ✅ **Config error UX**: `messagebox.showerror` with specific missing variable names

### Architect Review Items Addressed
1. ✅ **UTF-8 encoding**: All file I/O uses `encoding="utf-8"`
2. ✅ **Atomic writes**: Write-to-temp-then-rename pattern in `save_analysis()`
3. ⚠️ **Dependency pinning**: Left as `openai>=1.0.0` — upper bound pinning deferred to build step to avoid being overly restrictive during dev

### Test Results
- **33 LLM tests passed** (23 client + 10 storage)
- **180 total S360Reporter tests passed** (zero regressions)

### Design Deviations
None — implementation matches design doc exactly.
