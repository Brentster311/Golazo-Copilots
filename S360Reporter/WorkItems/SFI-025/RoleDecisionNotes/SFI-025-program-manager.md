# SFI-025 — Program Manager Decision Notes

## Work Item
**ID**: SFI-025  
**Title**: Configure LLM — GUI dialog with manual entry and auto-detect

## Key Decisions

### 1. Dialog in tk_app.py, not a separate module
The dialog is a single modal class (~150 lines). Putting it in `tk_app.py` alongside other modals (ItemDetailsModal, AnalysisModal, etc.) is consistent with the existing pattern. No new module needed.

### 2. Combobox for discovered configs (not a separate list dialog)
A `ttk.Combobox` inline in the dialog keeps the flow simple: detect → select from dropdown → fields populate. A separate selection dialog would add unnecessary navigation.

### 3. No API key field in the dialog
The user story explicitly excludes key storage. Auth is resolved at call time via `AzureChainedAuth` or `AZURE_OPENAI_API_KEY` env var. The dialog only configures connection routing (where to send requests), not credentials.

### 4. Config resolution order: saved → env → error
Saved config takes priority because it represents an explicit user choice. Env vars are the fallback for users who haven't used the dialog. This avoids surprising behavior where env vars silently override the dialog.

### 5. "Clear" button to revert to env-var mode
Users who switch back to env-var configuration need a way to remove the saved config. A "Clear" button removes the keys from settings.json.

## Risk Assessment
Low risk overall. The dialog is additive — it doesn't change existing behavior unless the user actively configures via it. Auto-detect failure degrades gracefully to manual entry.
