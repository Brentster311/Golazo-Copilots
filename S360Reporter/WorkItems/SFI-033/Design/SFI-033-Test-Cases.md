# SFI-033 — Test Cases

## Acceptance Criteria Coverage

### AC: `llm_client.py` module is removed
**Test**: `test_llm_client_module_deleted`
- Assert `GUI/src/sfi_reporter/llm_client.py` does not exist on disk
- Assert `import sfi_reporter.llm_client` raises `ModuleNotFoundError`
- **Expected**: File deleted, import fails

### AC: `llm_storage.py` module is removed
**Test**: `test_llm_storage_module_deleted`
- Assert `GUI/src/sfi_reporter/llm_storage.py` does not exist on disk
- **Expected**: File deleted

### AC: All LLM references cleaned up
**Test**: `test_no_llm_imports_in_dialogs`
- Import `sfi_reporter.dialogs`
- Assert `ConfigureLLMDialog` not in `dir(dialogs)` or `dialogs.__all__`
- Assert `AnalysisModal` not in `dir(dialogs)` or `dialogs.__all__`
- Assert `AnalysisProgressModal` not in `dir(dialogs)` or `dialogs.__all__`
- **Expected**: All three classes removed

**Test**: `test_no_load_llm_config_in_services`
- Import `sfi_reporter.services`
- Assert `_load_llm_config` not in `services.__all__`
- Assert `_load_llm_config` is not callable on the module
- **Expected**: Function removed

### AC: Tests for removed code are deleted
**Test**: `test_deleted_test_files_gone`
- Assert `test_llm_client.py`, `test_llm_storage.py`, `test_sfi_025.py` do not exist
- **Expected**: Files deleted

### AC: "open"/"LLM" button replaces "⚙️ Configure LLM" button
**Test**: `test_configure_llm_button_removed`
- Assert `ConfigureLLMDialog` is not referenced in any toolbar button command
- Assert toolbar contains buttons with text "open" and "LLM"
- **Expected**: No `llm_config_btn` attribute on app; `open_btn` and `llm_btn` exist

**Test**: `test_open_llm_button_toggles_panel`
- Click the open/LLM button → assert `CopilotPanel` frame is visible (winfo_ismapped)
- Click again → assert panel is hidden
- **Expected**: Panel visibility toggles on each click

### AC: Side panel contains Copilot chat interface
**Test**: `test_copilot_panel_has_required_widgets`
- Instantiate `CopilotPanel` with a mock parent frame
- Assert it contains: model combo, status label, chat display (ScrolledText), input entry, send button
- **Expected**: All widgets exist as attributes

**Test**: `test_copilot_panel_model_selector_default`
- Assert default model value is "gpt-4.1"
- Assert dropdown contains expected model options
- **Expected**: `_model_var.get() == "gpt-4.1"`

### AC: Side panel has close button
**Test**: `test_copilot_panel_close_button`
- Instantiate `CopilotPanel`, assert close button exists in header
- Simulate close button click → assert panel calls hide callback
- **Expected**: Close button triggers `on_close` callback

### AC: "Analyze with LLM" shows "Not yet implemented"
**Test**: `test_analyze_with_llm_shows_not_implemented`
- Mock `tkinter.messagebox.showinfo`
- Call `_launch_llm_analysis(parent, item)`
- Assert `messagebox.showinfo` was called with message containing "not yet implemented"
- Assert NO imports from `llm_client` or `llm_storage` occurred
- **Expected**: messagebox shown, no LLM dependencies loaded

### AC: AsyncBridge non-blocking
**Test**: `test_async_bridge_starts_background_loop`
- Create `AsyncBridge`, call `start()`
- Assert `bridge.loop` is not None and is running
- Call `stop()`
- **Expected**: Background event loop starts on daemon thread

**Test**: `test_async_bridge_runs_coroutine`
- Create `AsyncBridge`, start it
- Schedule a simple coroutine that returns 42
- Assert `future.result(timeout=2) == 42`
- **Expected**: Coroutine executes on background thread

### AC: Dependency check on panel open
**Test**: `test_copilot_panel_missing_sdk_shows_instructions`
- Mock `importlib.import_module("copilot")` to raise `ImportError`
- Open panel → assert instructions message displayed in chat area
- **Expected**: Panel opens, shows install instructions, does not crash

### AC: Existing tests pass
**Test**: Run remaining test suite
- `pytest GUI/tests/ -v` (excluding deleted test files)
- **Expected**: All tests pass

## Edge Cases

**Test**: `test_send_empty_prompt_is_noop`
- Set input entry to empty string, call `_on_send()`
- Assert no message appended to chat display
- **Expected**: No SDK call, no change to display

**Test**: `test_panel_toggle_rapid`
- Toggle panel visibility 10 times rapidly
- Assert final state is consistent (visible if odd, hidden if even)
- **Expected**: No exceptions, consistent final state

## Capability Registry Impact
- **reporter-web-app**: Not impacted — separate Streamlit codebase, no shared LLM code.
