# SFI-025 — Project Owner Assistant Decision Notes

## Work Item
**ID**: SFI-025  
**Title**: Configure LLM — GUI dialog with manual entry and auto-detect

## Decisions Made

### 1. Single User Story (no decomposition)
The feature has one user-observable outcome: a Configure LLM dialog accessible from the main screen. Auto-detect and manual entry are two paths within the same dialog, not separate deliverables.

### 2. Persistence via existing `settings.json`
SFIReporter already persists the "re-apply filter" preference to `%TEMP%/sfireporter/settings.json`. Reusing this file for LLM config avoids introducing a new storage mechanism. Keys: `llm_endpoint`, `llm_deployment`, `llm_api_version`.

### 3. No API key storage
The app must not persist API keys or tokens. Azure OpenAI auth is handled at call time via `AzureChainedAuth` (token-based) or the existing `AZURE_OPENAI_API_KEY` env var. The saved config stores only endpoint, deployment name, and API version.

### 4. Saved config takes priority over env vars
When a user has explicitly configured via the dialog, that choice should stick. `LLMConfig.from_env()` remains as a fallback for users who prefer the env-var approach or haven't configured via the dialog yet.

### 5. Auto-detect leverages LLM-0012
The "Auto-detect" button calls `llm_extender.discover_azure_configs()` (implemented in LLM-0012). This returns `list[LLMConfig]` — the dialog presents them in a selection list. This avoids reimplementing Azure resource discovery.

## Scope Justification
- Manual entry covers users who know their endpoint and just want to set it once.
- Auto-detect covers users who have multiple Azure OpenAI resources and don't want to look up endpoint URLs.
- Both paths converge to the same persisted config — minimal code surface.

## Open Questions
None — all checklist items resolved:
- Interface: GUI (existing Tkinter app)
- Platform: Windows (exe via PyInstaller)
- Persistence: File-based (`settings.json`)
- User type: Technical (developers managing SFI items)
