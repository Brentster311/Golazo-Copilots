# SFI-033 Developer Notes

## Summary
Replaced the Azure OpenAI LLM integration with a GitHub Copilot SDK-powered chat side panel. Permanently removed old LLM modules and added a new `CopilotPanel` widget with `AsyncBridge` pattern.

## Changes Made

### Phase 0 — LLM Removal (permanent)
**Files deleted:**
- `GUI/src/sfi_reporter/llm_client.py` (419 lines — Azure OpenAI client)
- `GUI/src/sfi_reporter/llm_storage.py` (analysis result storage)
- `GUI/tests/test_llm_client.py`
- `GUI/tests/test_llm_storage.py`
- `GUI/tests/test_sfi_025.py` (ConfigureLLMDialog tests)
- `GUI/docs/analyze-with-llm.md`

**Files modified:**
- `dialogs.py` — Removed `ConfigureLLMDialog` (~200 lines), `AnalysisProgressModal`, `AnalysisModal`, `_on_analysis_complete`, `_on_analysis_error`. Rewrote `_launch_llm_analysis` as `messagebox.showinfo` stub. Cleaned `__all__`.
- `services.py` — Removed `_load_llm_config()` function and its `__all__` entry.
- `app.py` — Removed `ConfigureLLMDialog` import and `llm_config_btn` button.
- `pyproject.toml` — Removed `llm-extender`, `openai` deps, `streamlit` optional dep, `sfi-reporter-web` entry point.

### Phase 1 — UI Changes (app.py)
- Replaced "⚙️ Configure LLM" button with "🤖 LLM" toggle button (`self.llm_btn`)
- Added `_toggle_copilot_panel()` and `_hide_copilot_panel()` methods
- Panel lazy-created on first toggle via `CopilotPanel` import

### Phase 2 — Copilot SDK Integration (copilot_panel.py — new)
- `AsyncBridge` class — background asyncio event loop on daemon thread
- `CopilotPanel(tk.Frame)` — side panel with:
  - Header bar with title + X close button
  - Connection status indicator
  - Model selector (gpt-4.1, gpt-5, claude-sonnet-4.5, o4-mini)
  - ScrolledText chat display with user/assistant/error/system tags
  - Input entry + Send button
- System/light theme (matches S360Reporter, not dark ghcpsdk theme)
- Graceful SDK-missing handling: shows install instructions on first send

## TDD Approach
- **Red phase**: 27 tests written in `test_sfi_033.py` — all failed initially
- **Green phase**: Implementation completed, all 27 pass
- **Regression**: Full suite (229 passed, 2 pre-existing failures in test_tk_app.py, 8 pre-existing errors in test_data.py/test_tk_app.py — none related to SFI-033)

## Test Coverage (test_sfi_033.py)
| Test Class | Count | What It Tests |
|---|---|---|
| TestLLMModuleDeletion | 5 | Files deleted, imports fail |
| TestDialogsLLMCleanup | 5 | Classes/functions removed from dialogs |
| TestServicesLLMCleanup | 1 | _load_llm_config removed |
| TestAppLLMCleanup | 2 | ConfigureLLMDialog references gone |
| TestLLMAnalysisStub | 2 | Stub shows messagebox, no LLM imports |
| TestOpenLLMButtons | 1 | CopilotPanel referenced in app.py |
| TestAsyncBridge | 2 | Background loop starts/runs coroutines |
| TestCopilotPanel | 5 | Widget presence, model default, close, empty send, missing SDK |
| TestPyprojectCleanup | 4 | Deps and entrypoints cleaned |

## Capability Registry Impact
- **reporter-build** — affected (pyproject.toml changed). PyInstaller spec may need updating for removed `llm-extender`/`openai` deps and added `copilot_panel.py` module. No action needed now; spec will pick up changes on next build.

## Decisions
- Used lazy import of `CopilotPanel` in `_toggle_copilot_panel` to avoid importing `copilot` SDK at app startup
- Kept `_launch_llm_analysis` in `dialogs.__all__` since it's still called from right-click menus (now as stub)
- `SubscriptionPickerDialog` kept in dialogs — not LLM-specific, could be reused

## Run Tests
```bash
cd GUI
..\.venv\Scripts\python.exe -m pytest tests/test_sfi_033.py -v
```
