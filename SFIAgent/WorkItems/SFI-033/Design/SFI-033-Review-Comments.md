# SFI-033 — Design Review Comments

## Clarity & Completeness
- **Pass** — Design clearly maps the 4-phase approach (Phase 0: removal, Phase 1-2: Copilot panel, Phase 3: stub) to the user story requirements.
- **Updated** — Phase 0 explicitly enumerates all files to delete and all code to remove, eliminating ambiguity.

## Feasibility
- **Pass** — ghcpsdk reference implementation proves the AsyncBridge + CopilotClient pattern works in Tkinter.
- **Note**: Panel should check for `github-copilot-sdk` import and show install instructions if missing. Button remains enabled.

## Risk Coverage
- **Adequate** — SDK not installed and CLI not authenticated are covered.
- **Addition**: Add handling for mid-chat disconnection (SDK connection drops during a conversation).

## Edge Cases
1. User opens/closes panel rapidly — ensure no duplicate AsyncBridge threads.
2. User sends empty prompt — should be no-op (handled in ghcpsdk template).
3. Window resize with panel open — panel should remain proportional.
4. Panel open then Refresh Data — data refresh should work normally with panel open.

## LLM Removal Completeness
- **6 files to delete** — `llm_client.py`, `llm_storage.py`, `test_llm_client.py`, `test_llm_storage.py`, `test_sfi_025.py`, `docs/analyze-with-llm.md`
- **3 files to clean up** — `dialogs.py` (remove 5 classes/functions), `services.py` (remove `_load_llm_config`), `app.py` (remove ConfigureLLMDialog import/button)
- **Verify**: `pyproject.toml` to remove any `llm-extender` or `azure-openai` dependencies

## Naming
- `copilot_panel.py` — clear and consistent with module naming pattern.
- `CopilotPanel` class — follows existing naming conventions.

## No Blocking Issues
Design is approved for implementation with the minor notes above incorporated.

## Architect Notes

### Architectural Alignment
- **Phase 0 (LLM removal)** is a clean subtraction — no new coupling introduced. Removes dependencies on `azure-openai` SDK, `llm_extender`, and Azure CLI credential flows from the app's critical path.
- **Phase 1-2 (Copilot panel)** adds a single new module (`copilot_panel.py`) with clear boundary: `CopilotPanel` is a self-contained widget that the app owns via composition. No global state.

### Contracts
- `CopilotPanel.__init__(parent, on_close_callback)` — constructor contract
- `CopilotPanel.show()` / `CopilotPanel.hide()` — visibility contract
- `_launch_llm_analysis(parent, item)` — stub contract: shows messagebox, returns None, no side effects

### Security & Privacy
- Copilot SDK handles auth via existing Copilot CLI token — no new credential storage in the app
- Removing Azure OpenAI credential flow (AzureCliCredential) eliminates a credential surface

### Failure Isolation
- Missing `github-copilot-sdk` → panel shows instructions, rest of app unaffected
- SDK connection failure → error in panel status, rest of app unaffected
- AsyncBridge runs on daemon thread — process exit kills it cleanly

### Dependency Changes
- **Remove**: `llm-extender` (if in pyproject.toml), implicit `azure-openai` dependency
- **Add**: `github-copilot-sdk` as optional dependency
- **Net effect**: Simpler dependency tree
