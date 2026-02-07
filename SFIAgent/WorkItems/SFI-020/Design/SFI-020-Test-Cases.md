# SFI-020 Test Cases

**Work Item**: SFI-020  
**Date**: 2026-02-06

---

## Test Strategy

- **Unit tests**: `llm_client.py` and `llm_storage.py` are fully testable with mocks (no GUI dependency).
- **Integration tests**: `tk_app.py` context menu and modal can be tested with the existing `test_tk_app.py` pattern (mock tk root).
- **All Azure OpenAI calls are mocked** — no real API calls in tests.

---

## TC-1: LLM Config Loads from Environment Variables

**Module**: `llm_client.py`  
**Function**: `LLMConfig.from_env()`

| Step | Action | Expected |
|------|--------|----------|
| 1 | Set `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY` in env | Config object created with correct values |
| 2 | Set `AZURE_OPENAI_DEPLOYMENT` to `"gpt-4o-mini"` | `config.deployment == "gpt-4o-mini"` |
| 3 | Omit `AZURE_OPENAI_DEPLOYMENT` | `config.deployment == "gpt-4o"` (default) |

---

## TC-2: LLM Config Raises on Missing Required Vars

**Module**: `llm_client.py`  
**Function**: `LLMConfig.from_env()`

| Step | Action | Expected |
|------|--------|----------|
| 1 | Unset `AZURE_OPENAI_ENDPOINT` | `LLMConfigError` raised with helpful message |
| 2 | Unset `AZURE_OPENAI_API_KEY` | `LLMConfigError` raised with helpful message |

---

## TC-3: Prompt Builder Includes Key Action Item Fields

**Module**: `llm_client.py`  
**Function**: `build_prompt(item)`

| Step | Action | Expected |
|------|--------|----------|
| 1 | Pass item dict with title, SLA, dates, ownership, remediation | System message contains structured instructions |
| 2 | Verify user message | Contains title, SLA type, due date, assigned to, remediation text |
| 3 | Pass item with empty `Remediation` field | Prompt still valid; field shown as "N/A" or omitted |
| 4 | Pass item with very large `Remediation` text (>5000 chars) | Text is truncated to fit token budget |

---

## TC-4: Prompt Builder Accepts Optional URL Content

**Module**: `llm_client.py`  
**Function**: `build_prompt(item, url_content=None)`

| Step | Action | Expected |
|------|--------|----------|
| 1 | Call with `url_content=None` | Prompt has no URL content section |
| 2 | Call with `url_content={"https://...": "page text"}` | Prompt includes URL content section (future SFI-021 use) |

---

## TC-5: Analyze Item Returns Structured Result

**Module**: `llm_client.py`  
**Function**: `analyze_item(item, config)`  
**Mocking**: Mock `AzureOpenAI.chat.completions.create`

| Step | Action | Expected |
|------|--------|----------|
| 1 | Mock returns well-formed response with 4 sections | `AnalysisResult` has non-empty `mission`, `steps_to_done`, `resources`, `risk_of_delay` |
| 2 | Verify `timestamp` is ISO 8601 format | Parseable datetime string |
| 3 | Verify `prompt_tokens` and `completion_tokens` populated from response usage | Matches mocked usage values |

---

## TC-6: Analyze Item Handles API Errors

**Module**: `llm_client.py`  
**Function**: `analyze_item(item, config)`

| Step | Action | Expected |
|------|--------|----------|
| 1 | Mock raises `openai.APIConnectionError` | `LLMError` raised with "connection" context |
| 2 | Mock raises `openai.RateLimitError` | `LLMError` raised with "rate limit" context |
| 3 | Mock raises `openai.AuthenticationError` | `LLMError` raised with "authentication" context |
| 4 | Mock returns response with no parseable sections | `AnalysisResult.analysis_text` has raw content; section fields are empty strings |

---

## TC-7: Save Analysis Writes Valid JSON

**Module**: `llm_storage.py`  
**Function**: `save_analysis(result)`

| Step | Action | Expected |
|------|--------|----------|
| 1 | Call with valid `AnalysisResult` | JSON file created at expected path |
| 2 | Read the file back | Valid JSON with `schema_version`, `action_item_id`, `timestamp`, all section fields |
| 3 | Call again with same `action_item_id` | File overwritten (not duplicated) |

---

## TC-8: Save Analysis Uses Atomic Write

**Module**: `llm_storage.py`  
**Function**: `save_analysis(result)`

| Step | Action | Expected |
|------|--------|----------|
| 1 | Mock `os.replace` to raise `OSError` | Original file (if any) is not corrupted; error propagated |
| 2 | Verify `.tmp` file is written first | Temp file created before rename |

---

## TC-9: Load Analysis Returns Saved Data

**Module**: `llm_storage.py`  
**Function**: `load_analysis(action_item_id)`

| Step | Action | Expected |
|------|--------|----------|
| 1 | Save an analysis, then load it | Returns `AnalysisResult` matching saved data |
| 2 | Load with non-existent `action_item_id` | Returns `None` |
| 3 | Write corrupted JSON to analysis file, then load | Returns `None` (graceful failure) |

---

## TC-10: Analysis Exists Check

**Module**: `llm_storage.py`  
**Function**: `analysis_exists(action_item_id)`

| Step | Action | Expected |
|------|--------|----------|
| 1 | No saved file | Returns `False` |
| 2 | After saving analysis | Returns `True` |

---

## TC-11: Context Menu Appears on Right-Click (KPI Treeview)

**Module**: `tk_app.py`  
**Scope**: `SFIReporterApp`

| Step | Action | Expected |
|------|--------|----------|
| 1 | Simulate `<Button-3>` event on a populated KPI row | `tk.Menu` created with "🤖 Analyze with LLM" command |
| 2 | Simulate `<Button-3>` on empty area (no row) | No menu shown |

---

## TC-12: Context Menu Appears on Right-Click (DrillDownModal)

**Module**: `tk_app.py`  
**Scope**: `DrillDownModal`

| Step | Action | Expected |
|------|--------|----------|
| 1 | Simulate `<Button-3>` event on a populated item row | `tk.Menu` created with "🤖 Analyze with LLM" command |
| 2 | Simulate `<Button-3>` on empty area | No menu shown |

---

## TC-13: Analyze Handler Sends Correct Data to LLM

**Module**: `tk_app.py`  
**Mocking**: Mock `llm_client.analyze_item`, mock `llm_storage.save_analysis`

| Step | Action | Expected |
|------|--------|----------|
| 1 | Trigger analysis on a KPI row | `analyze_item` called with the correct item dict from `detailed_items` |
| 2 | Verify item dict contains `_kpi_id` field | Present and matching the selected KPI |

---

## TC-14: Analysis Result Saved After Successful LLM Call

**Module**: `tk_app.py`  
**Mocking**: Mock `llm_client.analyze_item` (returns result), mock `llm_storage.save_analysis`

| Step | Action | Expected |
|------|--------|----------|
| 1 | Trigger analysis, mock returns `AnalysisResult` | `save_analysis` called with the result |
| 2 | Verify file path uses action item ID | Path matches `%LOCALAPPDATA%/sfireporter/analyses/<id>.json` |

---

## TC-15: Error Shown When LLM Config Missing

**Module**: `tk_app.py`  
**Mocking**: Mock `LLMConfig.from_env()` to raise `LLMConfigError`

| Step | Action | Expected |
|------|--------|----------|
| 1 | Trigger analysis with no env vars set | `messagebox.showerror` called with setup instructions |
| 2 | No background thread spawned | Thread not started |

---

## TC-16: Error Shown When LLM API Fails

**Module**: `tk_app.py`  
**Mocking**: Mock `analyze_item` to raise `LLMError`

| Step | Action | Expected |
|------|--------|----------|
| 1 | Trigger analysis, mock raises error | `messagebox.showerror` called with error details |
| 2 | Progress modal dismissed | Modal destroyed after error |

---

## TC-17: LLM Config Repr Masks API Key

**Module**: `llm_client.py`  
**Function**: `LLMConfig.__repr__()`

| Step | Action | Expected |
|------|--------|----------|
| 1 | Create config with `api_key="sk-secret123"` | `repr()` shows `api_key='****'` |
| 2 | `str()` also masks | No plaintext key in any string representation |
