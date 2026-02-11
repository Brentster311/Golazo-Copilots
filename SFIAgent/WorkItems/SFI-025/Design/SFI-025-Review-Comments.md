# SFI-025 — Design Review Comments

## Overall Assessment
The design is **clear, well-scoped, and implementable**. The dialog approach is appropriate for the feature size, and leveraging existing `_load_setting`/`_save_setting` keeps the change minimal.

## Comments

### 1. [Minor] Endpoint validation
Design says "must start with `https://`". Should also reject trailing whitespace and ensure the URL doesn't end with a bare slash inconsistency. Recommendation: `.strip()` on save, accept with or without trailing `/`.

**Resolution**: Strip whitespace on save. Normalize trailing slash.

### 2. [Minor] Default field values on first open
If no saved config and no env vars, the fields should show sensible defaults: endpoint empty, deployment `"gpt-4o"`, API version `"2024-10-21"`. Design implies this but should be explicit.

**Resolution**: Confirmed — defaults come from `LLMConfig` dataclass defaults.

### 3. [Edge Case] Auto-detect with zero results
The design handles this (show info message). Good — no crash path.

### 4. [Edge Case] Auto-detect ImportError in exe
Azure SDK optional deps may not be bundled in the PyInstaller exe. The "Auto-detect" button should gracefully show "Azure discovery SDK not available" rather than crash. Design covers this.

### 5. [Low Risk] Settings file corruption
If `settings.json` is manually edited with invalid JSON, `_load_setting` already handles this (returns default). No issue.

### 6. [Approved] Config resolution order
Saved → env → error is correct. Matches user expectations.

## Verdict: **Approved** — no blockers. Minor notes above are refinements, not gate issues.

---

## Architect Notes

### Architectural Alignment
The `ConfigureLLMDialog` fits cleanly as another modal in `tk_app.py`, alongside `ItemDetailsModal`, `AnalysisModal`, and `FilterDialog`. No new modules or packages needed. The dialog reads/writes settings via existing `_load_setting`/`_save_setting` — no new persistence layer.

### API Contract
- **Auto-detect**: `discover_azure_configs(*, subscription_id=None, api_version=None) -> list[LLMConfig]` — returns `llm_extender.config.LLMConfig` objects. The dialog needs to map these to SFIReporter's own `sfi_reporter.llm_client.LLMConfig` fields: `base_url` → `endpoint`, `deployment` → `deployment`, `model` → display only, `api_version` → `api_version`.
- **Settings keys**: `llm_endpoint`, `llm_deployment`, `llm_api_version` — string values, nullable (absent = not configured).

### Security & Privacy
- **No secrets persisted**: Confirmed. `settings.json` stores only endpoint URL, deployment name, and API version. No API keys or tokens.
- **Auth at call time**: `LLMConfig.from_env()` reads `AZURE_OPENAI_API_KEY` at call time. The saved config path will also need an API key source — either env var or future `AzureChainedAuth` integration. Current scope: env var only.
- **Auto-detect credentials**: `discover_azure_configs()` uses `AzureCliCredential` from the user's `az login` session. No credentials flow through SFIReporter code.

### Dependency Choices
- `llm_extender.discover_azure_configs()` — already a dependency via LLMExtender editable install
- Azure SDK packages — optional, only needed for auto-detect. Missing SDK is a handled error path.

### Failure Isolation
- Auto-detect failure (any exception) → error message in dialog, manual entry still works
- Invalid saved config → LLM analysis fails at call time with existing error handling
- Corrupt `settings.json` → `_load_setting` returns defaults, dialog opens with defaults

### Key Design Note: Two LLMConfig Types
SFIReporter has its own `sfi_reporter.llm_client.LLMConfig` (with `endpoint`, `api_key`, `deployment`, `api_version`). LLMExtender has `llm_extender.config.LLMConfig` (with `base_url`, `model`, `deployment`, `api_version`, `provider`). The dialog must translate between them when auto-detect returns LLMExtender configs. This is a mapping concern, not a coupling issue.

### Verdict: **Architecturally approved.** No new work items required.
