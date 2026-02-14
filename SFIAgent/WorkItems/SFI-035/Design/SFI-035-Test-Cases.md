# SFI-035 — Test Cases

## Mapping to Acceptance Criteria

| AC # | Acceptance Criterion | Test Cases |
|------|---------------------|------------|
| AC-1 | Sources summary appears before LLM streaming | TC-6 (integration) |
| AC-2 | Shows total URLs, successes, failures | TC-1, TC-2, TC-3 |
| AC-3 | Each URL listed with ✅/❌, chars/error | TC-1, TC-2, TC-4 |
| AC-4 | Zero URLs shows "No documentation URLs found" | TC-3 |
| AC-5 | `analyze_kpi` returns structured `AnalysisResult` | TC-5 |
| AC-6 | Existing tests pass; new tests cover structured return | TC-1–TC-7 |

---

## TC-1: AnalysisResult contains successful fetch metadata

**Type**: Unit  
**Module**: `kpi_analyzer.py`  
**Setup**: Call `analyze_kpi` with items that have 2 fetchable URLs (mock `fetch_url_content` to return success).  
**Assert**:
- `result` is an `AnalysisResult` instance
- `result.urls_found` contains both URLs
- `result.fetch_results` has 2 entries
- Each entry with `ok=True`, `chars > 0`, `error=""`
- `result.prompt` is a non-empty string containing the KPI name

**Failure message**: "AnalysisResult did not contain expected fetch metadata for successful URLs"

---

## TC-2: AnalysisResult captures failed fetch metadata

**Type**: Unit  
**Module**: `kpi_analyzer.py`  
**Setup**: Call `fetch_url_content` with a URL that returns HTTP 403 (mock).  
**Assert**:
- Result entry has `ok=False`, `chars=0`, `error` containing "403"

**Failure message**: "Failed fetch not captured in fetch_results with correct error"

---

## TC-3: Zero URLs produces correct AnalysisResult

**Type**: Unit  
**Module**: `kpi_analyzer.py`  
**Setup**: Items with no URL fields populated.  
**Assert**:
- `result.urls_found` is empty list
- `result.fetch_results` is empty list
- `result.prompt` still contains item data and the four analysis questions

**Failure message**: "Zero-URL AnalysisResult not constructed correctly"

---

## TC-4: Mixed success/failure fetch results

**Type**: Unit  
**Module**: `kpi_analyzer.py`  
**Setup**: 3 URLs — 2 succeed, 1 fails with timeout.  
**Assert**:
- `result.fetch_results` has 3 entries
- 2 entries have `ok=True`
- 1 entry has `ok=False` with error message

**Failure message**: "Mixed fetch results not captured correctly"

---

## TC-5: AnalysisResult.prompt matches legacy format

**Type**: Unit  
**Module**: `kpi_analyzer.py`  
**Setup**: Same items and docs as existing `test_sfi_034.py::TestBuildAnalysisPrompt::test_includes_all_items`.  
**Assert**:
- `result.prompt` contains all item IDs
- `result.prompt` contains the four questions
- `str(result)` returns the same as `result.prompt`

**Failure message**: "AnalysisResult.prompt does not match expected prompt format"

---

## TC-6: format_sources_card output correctness

**Type**: Unit  
**Module**: `kpi_analyzer.py` (or `copilot_panel.py` helper)  
**Setup**: Call the sources-card formatting function with known `AnalysisResult`.  
**Assert**:
- Output contains "Sources" header
- Output contains "✅" for successes and "❌" for failures
- Output contains URL strings
- Output contains character counts for successes
- Output contains error messages for failures
- With zero URLs, output contains "No documentation URLs found"

**Failure message**: "Sources card text does not contain expected provenance information"

---

## TC-7: Existing test_sfi_034 tests still pass

**Type**: Regression  
**Module**: `test_sfi_034.py`  
**Assert**: All existing tests in `test_sfi_034.py` pass without modification (or with minimal adapter changes if `build_analysis_prompt` signature changes).

**Failure message**: "Regression: existing kpi_analyzer tests broken by SFI-035 changes"
