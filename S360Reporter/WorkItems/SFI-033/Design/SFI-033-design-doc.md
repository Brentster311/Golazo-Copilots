# SFI-033 Design Document

## Summary
Replace the "⚙️ Configure LLM" toolbar button and Azure OpenAI-based analysis workflow with a GitHub Copilot SDK-powered chat side panel. The side panel appears on the right side of the S360Reporter window when the user clicks "open"/"LLM" buttons, and can be closed via its own X button. The existing "Analyze with LLM" right-click menu items are preserved but stubbed to show "Not yet implemented".

Additionally, permanently remove the old Azure OpenAI LLM modules (`llm_client.py`, `llm_storage.py`) and all related UI code (`ConfigureLLMDialog`, `AnalysisModal`, `AnalysisProgressModal`) from the codebase, along with the `_load_llm_config` helper in `services.py`.

## Problem Statement
The current LLM integration requires manual configuration of Azure OpenAI endpoints (endpoint URL, deployment name, API version) via a settings dialog. This is fragile, requires users to discover and configure their own Azure OpenAI instances, and creates a barrier to adoption. GitHub Copilot is already available to all Microsoft engineers and provides a simpler authentication model.

## Business Case
- **Why now**: GitHub Copilot SDK for Python is available; the team already has a working reference implementation (ghcpsdk).
- **Impact**: Removes configuration friction; users no longer need Azure OpenAI credentials.
- **KPIs**: Reduced support questions about LLM configuration; increased adoption of AI-assisted analysis.

## Stakeholders
- S360Reporter end users (managers and ICs)
- S360Reporter developer (Brent)

## Functional Requirements
1. Replace "⚙️ Configure LLM" button with "open" and "LLM" label buttons that toggle side panel visibility
2. Side panel: right-aligned, ~350px wide, contains chat interface
3. Chat interface includes: model selector dropdown, connection status, scrollable chat display, text input + send button  
4. Side panel has X close button in its header
5. Chat uses GitHub Copilot SDK via AsyncBridge pattern (non-blocking)
6. "Analyze with LLM" right-click items show messagebox "Not yet implemented"
7. `ConfigureLLMDialog`, `AnalysisModal`, `AnalysisProgressModal` classes removed from `dialogs.py`
8. `llm_client.py` module deleted
9. `llm_storage.py` module deleted
10. `_load_llm_config()` removed from `services.py`
11. `_launch_llm_analysis()` rewritten as stub (no LLM imports)
12. `_on_analysis_complete()` and `_on_analysis_error()` removed from `dialogs.py`
13. All `llm_extender` imports removed

## Non-functional Requirements
- Side panel show/hide must be instant (no layout recalculation jank)
- Copilot SDK calls must not block Tkinter main loop
- All existing tests not testing removed LLM code must continue to pass
- `test_llm_client.py` and `test_llm_storage.py` are deleted
- `test_sfi_025.py` (ConfigureLLMDialog tests) is deleted

## Proposed Approach

### Phase 0: Remove Old LLM Code (permanent, not rolled back)
1. Delete `GUI/src/sfi_reporter/llm_client.py`
2. Delete `GUI/src/sfi_reporter/llm_storage.py`
3. Delete `GUI/tests/test_llm_client.py` and `GUI/tests/test_llm_storage.py`
4. Delete `GUI/tests/test_sfi_025.py` (ConfigureLLMDialog tests)
5. Remove `ConfigureLLMDialog`, `AnalysisModal`, `AnalysisProgressModal`, `_on_analysis_complete`, `_on_analysis_error` from `dialogs.py`
6. Rewrite `_launch_llm_analysis()` in `dialogs.py` as a stub: `messagebox.showinfo(...)`
7. Remove `_load_llm_config()` from `services.py` and its `__all__` entry
8. Remove `ConfigureLLMDialog` import and button from `app.py`
9. Remove `llm_extender` dependency from `pyproject.toml` if present

### Phase 1: UI Changes (app.py)
1. Remove "⚙️ Configure LLM" button
2. Add "open" + "LLM" toggle buttons in toolbar (matching screenshot layout)
3. Create `CopilotPanel` — a `tk.Frame` on the right side of the main window
4. Panel contains: header with title + close button, model selector, scrolled chat display, input bar + send button
5. Toggle logic: button click shows/hides panel via `pack`/`pack_forget`

### Phase 2: Copilot SDK Integration (copilot_panel.py — new module)
1. Port `AsyncBridge` class from ghcpsdk
2. Port `CopilotClient`/session lifecycle into `CopilotPanel`
3. Streaming response rendering with tag styles
4. Connection status indicator

### Phase 3: Stub Analysis (dialogs.py)
1. Already done in Phase 0 — `_launch_llm_analysis()` rewritten as messagebox stub

## Alternatives Considered
| Alternative | Reason Rejected |
|---|---|
| Embed Copilot in a separate window | User wants integrated side panel, not a pop-out |
| Keep Azure OpenAI and add Copilot as second option | Increases complexity; Copilot is the strategic direction |
| Remove "Analyze with LLM" entirely | Users expect it; stubbing preserves discoverability |

## Risks and Mitigations
| Risk | Mitigation |
|---|---|
| `github-copilot-sdk` not installed | Graceful error on panel open; button stays functional |
| Copilot CLI not authenticated | Show connection error in panel status, not a crash |
| Side panel layout disrupts existing UI | Use `PanedWindow` or simple pack management; test at various window sizes |

## Dependencies
- `github-copilot-sdk` pip package
- GitHub Copilot CLI installed and authenticated on user's machine

## Migration / Rollout / Rollback
- **Rollout**: Add `github-copilot-sdk` to pyproject.toml extras or optional dependency; remove `llm-extender` dependency
- **Rollback**: Copilot panel can be reverted; LLM module removal is permanent and not rolled back

## Observability Plan
- Desktop app — no server-side observability. Connection status visible in panel UI.

## Test Strategy Summary
- Unit test: `_launch_llm_analysis` stub shows messagebox (mock `messagebox.showinfo`)
- Unit test: CopilotPanel instantiation (mock SDK)
- Deletion: `test_llm_client.py`, `test_llm_storage.py`, `test_sfi_025.py` deleted with their modules
- Integration: remaining test suite must pass
- Manual: verify panel open/close, chat send/receive

## Files to Delete
| File | Reason |
|---|---|
| `GUI/src/sfi_reporter/llm_client.py` | Azure OpenAI client — replaced by Copilot SDK |
| `GUI/src/sfi_reporter/llm_storage.py` | Analysis result storage — no longer needed |
| `GUI/tests/test_llm_client.py` | Tests for deleted module |
| `GUI/tests/test_llm_storage.py` | Tests for deleted module |
| `GUI/tests/test_sfi_025.py` | Tests for ConfigureLLMDialog |
| `GUI/docs/analyze-with-llm.md` | Documentation for removed feature |

## Files to Modify
| File | Changes |
|---|---|
| `GUI/src/sfi_reporter/app.py` | Remove ConfigureLLMDialog import/button; add open/LLM buttons + CopilotPanel |
| `GUI/src/sfi_reporter/dialogs.py` | Remove ConfigureLLMDialog, AnalysisModal, AnalysisProgressModal, analysis helpers; rewrite `_launch_llm_analysis` as stub |
| `GUI/src/sfi_reporter/services.py` | Remove `_load_llm_config()` and its `__all__` entry |
| `pyproject.toml` | Remove llm-extender dep; add github-copilot-sdk |
