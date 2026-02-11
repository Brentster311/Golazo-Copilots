# SFI-025 — Design Doc: Configure LLM Dialog

## Summary

Add a "Configure LLM" button to the SFI Reporter main screen that opens a modal dialog where the user can manually enter Azure OpenAI connection details (endpoint, deployment, API version) or click "Auto-detect" to discover available configurations from their Azure CLI credentials via `llm_extender.discover_azure_configs()`. The chosen config is persisted to `settings.json` and used for all subsequent LLM analysis calls.

## Problem Statement

Today, LLM analysis requires setting environment variables (`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_API_VERSION`) before launching the app. This is cumbersome for non-CLI users and invisible — there's no in-app indication of what's configured or how to change it. Users with multiple Azure OpenAI resources have no way to switch between them without restarting.

## Business Case

- **Why now**: The `discover_azure_configs()` capability just shipped in LLMExtender (LLM-0012), making auto-detection possible.
- **Impact**: Removes the biggest friction point for LLM analysis adoption — users no longer need to know about env vars.
- **KPIs**: Increased LLM analysis usage (no telemetry, but user feedback expected).

## Stakeholders

- SFI Reporter end users (developers managing SFI remediation items)

## Functional Requirements

### FR-1: Configure LLM Button
A `ttk.Button` labeled "Configure LLM" on the main screen controls row. Opens the `ConfigureLLMDialog` modal.

### FR-2: ConfigureLLMDialog
A `tk.Toplevel` modal with:
- **Endpoint** field: `ttk.Entry`, pre-populated from saved config or empty
- **Deployment** field: `ttk.Entry`, pre-populated or default `"gpt-4o"`
- **API Version** field: `ttk.Entry`, pre-populated or default `"2024-10-21"`
- **Auto-detect** button: triggers discovery flow
- **Save** button: validates and persists config
- **Cancel** button: closes without saving

### FR-3: Auto-detect Flow
1. User clicks "Auto-detect"
2. Button text changes to "Detecting..." (disabled)
3. Background thread calls `discover_azure_configs()`
4. On success with results: populate a `ttk.Combobox` / listbox with discovered configs (display: `endpoint — deployment (model)`)
5. User selects a config → fields auto-populate
6. On success with empty results: show info message "No Azure OpenAI deployments found"
7. On error (`ImportError`): show error "Azure SDK not installed — run `pip install llm-extender[azure-discover]`"
8. On error (other): show error message

### FR-4: Persistence
- Save: writes `llm_endpoint`, `llm_deployment`, `llm_api_version` to `settings.json` via existing `_save_setting()` helper
- Load: reads via `_load_setting()` on dialog open and on LLM analysis launch
- Clear: a "Clear" button removes the saved keys (reverts to env-var fallback)

### FR-5: Integration with LLM Analysis
Update `_launch_llm_analysis()` to:
1. Try loading saved config from `settings.json`
2. If saved config has endpoint — use it (still needs API key from env or `AzureChainedAuth`)
3. If no saved config — fall back to `LLMConfig.from_env()`

## Non-Functional Requirements

- Auto-detect runs in a background thread (no UI freeze)
- Dialog is modal (grabs focus)
- No secrets persisted (no API keys in settings.json)
- Works in PyInstaller exe (no file-system assumptions beyond cache dir)

## Proposed Approach

### New Code

1. **`ConfigureLLMDialog` class** in `tk_app.py`:
   - `__init__(self, parent)` — builds the dialog UI
   - `_load_saved_config()` — reads from settings.json, populates fields
   - `_on_auto_detect()` — spawns thread, calls `discover_azure_configs()`
   - `_on_detect_complete(configs)` — main-thread callback, populates dropdown
   - `_on_detect_error(error)` — main-thread callback, shows error
   - `_on_config_selected(event)` — dropdown selection → populate fields
   - `_on_save()` — validate + persist + close
   - `_on_clear()` — remove saved keys + clear fields
   - `_on_cancel()` — close without saving

2. **Button in `SFIReporterApp._build_controls()`**: adds "Configure LLM" button

3. **Updated `_launch_llm_analysis()`**: load saved config first, fallback to `from_env()`

### Modified Code

- `tk_app.py`: add `ConfigureLLMDialog` class, button in controls row, update `_launch_llm_analysis`
- Possible: `llm_client.py` — add `LLMConfig.from_settings()` classmethod (or handle in tk_app.py directly)

## Alternatives Considered

| Alternative | Why Rejected |
|---|---|
| Settings file instead of dialog | No discovery capability, same as env vars but in a file |
| Auto-detect on app startup | Slow, may fail silently, user has no control |
| Separate settings window | Over-engineered for 3 fields |

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Azure SDK not installed in exe | Medium | Auto-detect fails | Clear error message with install instructions; manual entry still works |
| `az login` expired | Medium | Auto-detect returns empty | Show "No configs found — ensure `az login` is current" |
| User saves invalid endpoint | Low | LLM calls fail | Validation on save (must start with `https://`); failure at call time shows error |

## Dependencies

- `llm_extender.discover_azure_configs()` (LLM-0012) — already implemented and tested
- Existing `_load_setting()` / `_save_setting()` helpers (SFI-024)
- Existing `LLMConfig` dataclass in `llm_client.py`

## Migration / Rollout / Rollback

- **Rollout**: Next exe build. New `settings.json` keys are additive.
- **Rollback**: Remove the button. Saved settings are harmless if ignored.
- **Migration**: None. Existing env-var users are unaffected.

## Observability

- Logger messages for: config loaded from settings, auto-detect started/completed/failed, config saved
- No external telemetry

## Test Strategy Summary

- Unit tests for `ConfigureLLMDialog` field population and save/load
- Unit test for `_launch_llm_analysis` config resolution order (saved → env → error)
- Mock `discover_azure_configs()` in auto-detect tests
- Integration: manual testing of dialog in exe
