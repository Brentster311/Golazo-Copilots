# SFI-025 — Architect Decision Notes

## Work Item
**ID**: SFI-025  
**Title**: Configure LLM — GUI dialog with manual entry and auto-detect

## Architectural Decisions

### 1. Single modal class, no new modules
`ConfigureLLMDialog` lives in `tk_app.py` alongside other modals. The feature doesn't warrant a new module — it's ~150 lines of UI code that reads/writes settings and optionally calls discovery.

### 2. LLMConfig type mapping
LLMExtender's `LLMConfig` has `base_url`, `model`, `deployment`. S360Reporter's `LLMConfig` has `endpoint`, `deployment`, `api_key`. The dialog maps `base_url → endpoint` and `deployment → deployment` when populating from auto-detect. This is a display-layer concern only.

### 3. API key remains env-var sourced
The saved config covers connection routing only (endpoint, deployment, API version). The API key is still sourced from `AZURE_OPENAI_API_KEY` env var at call time in `LLMConfig.from_env()`. A future work item could add `AzureChainedAuth` support to eliminate the env var entirely.

### 4. No new hidden-import needed for PyInstaller
`llm_extender.discovery` is imported lazily inside the auto-detect callback. PyInstaller already bundles `llm_extender` — the discovery module will be included. Azure SDK packages are NOT bundled (they're optional) — `ImportError` is the expected path in the exe unless the user installs them separately.

## Security Review
- No secrets in settings.json ✓
- No credential logging ✓
- Azure CLI credentials used only transiently by `discover_azure_configs()` ✓
