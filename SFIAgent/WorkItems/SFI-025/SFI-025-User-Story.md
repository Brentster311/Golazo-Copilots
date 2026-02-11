# SFI-025 — Configure LLM Dialog

**Status**: IMPLEMENTED

## User Story

- **Title**: Configure LLM — GUI dialog with manual entry and auto-detect
- **As a**: SFI Reporter user
- **I want**: a "Configure LLM" button on the main screen that opens a dialog where I can manually enter Azure OpenAI endpoint, model/deployment, and API version — or click "Auto-detect" to discover available configs from my Azure CLI credentials and pick one
- **So that**: I can configure the LLM without setting environment variables, and quickly find my Azure OpenAI resources without looking them up manually

## Out of Scope

- Storing API keys (the app already uses `AzureChainedAuth` / env vars for auth tokens at call time)
- Changing the LLM analysis prompt or output format
- Supporting non-Azure OpenAI providers
- Modifying the existing `LLMConfig.from_env()` fallback (it remains as a secondary fallback)

## Assumptions

- **Assumption (explicit)**: The dialog persists the chosen config to the existing `settings.json` in the cache directory (`%TEMP%/sfireporter/`). This avoids requiring env vars for repeat use.
- **Assumption (explicit)**: Auto-detect calls `llm_extender.discover_azure_configs()` which requires the Azure SDK optional deps and `az login`. If the SDK is missing or the user isn't logged in, a clear error message is shown.
- **Assumption (explicit)**: The persisted config takes priority over environment variables when both exist. The user can clear the saved config to revert to env-var behavior.
- **Assumption (explicit)**: The existing `_launch_llm_analysis` function is updated to load the saved config first, falling back to `LLMConfig.from_env()`.

## Acceptance Criteria

- [ ] A "Configure LLM" button is visible on the main screen (controls row).
- [ ] Clicking it opens a modal dialog with text fields for **Endpoint**, **Deployment** (model), and **API Version**, plus a "Save" and "Cancel" button.
- [ ] The dialog has an "Auto-detect" button that calls `discover_azure_configs()` in a background thread, shows a progress indicator, and on success presents a list/dropdown of discovered configs for the user to select — populating the fields.
- [ ] If auto-detect fails (missing SDK, no `az login`, no configs found), a clear error message is displayed in the dialog.
- [ ] Saving the config persists it to `settings.json` and immediately makes it available for LLM analysis without restarting.
- [ ] `_launch_llm_analysis` loads the saved config first; if none saved, falls back to `LLMConfig.from_env()`.
- [ ] If saved config fields are pre-populated when reopening the dialog, the user can edit and re-save.

## Non-functional Requirements

- Auto-detect runs in a background thread to avoid freezing the UI.
- The dialog is modal — the user cannot interact with the main window while it is open.
- Persisted config must not store secrets (API keys). Auth is resolved at call time via `AzureChainedAuth`.

## Telemetry / Metrics Expected

- None (desktop app, no telemetry).

## Rollout / Rollback Notes

- Ship with next exe build. No migration needed — `settings.json` gains new keys (`llm_endpoint`, `llm_deployment`, `llm_api_version`) which are ignored by older versions.
