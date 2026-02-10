# LLM-0012 — Project Owner Assistant Decision Notes

## Context
The user discovered during a live session that both of their Azure OpenAI resources have `disableLocalAuth: true` (API keys disabled). The only way to authenticate is via Azure AD tokens. This makes the current manual configuration workflow (copy endpoint, key, deployment name) cumbersome and fragile.

## Key Decisions

### 1. Single story — discovery only
The user also mentioned "remove using keys from llm_extender altogether" — this was **intentionally scoped out** as a separate work item. Removing `api_key` support is a breaking change that affects all providers and all existing users. This story is additive only.

### 2. Static method vs. standalone function
The user suggested "a static method called configure or similar." Options:
- `LLMClient.discover()` — discoverable, intuitive
- `discover_azure_configs()` — module-level, more explicit

Decision: **Both** — implement as a module-level function and also expose as `LLMClient.discover()` class method that delegates to it. This follows the pattern of `fetch_url` being both a standalone function and used within `LLMClient.complete_with_url`.

### 3. Azure CLI only
Scoped to `AzureCliCredential` only. MSI doesn't make sense for discovery (it's a dev-machine feature). Service principal auth could be added later.

### 4. RBAC check approach
Rather than attempting inference and catching 403s, the method should check role assignments via Azure Management API. This is faster and avoids side effects. Required roles: `Cognitive Services OpenAI User`, `Cognitive Services OpenAI Contributor`, `Cognitive Services Contributor`, or `Owner`/`Contributor` at resource/RG/subscription level.

### 5. Return type
Returns `list[LLMConfig]` — each entry is a complete, pre-filled config. The user picks one and passes it to `LLMClient`. This matches the user's stated goal: "returns a list of viable config options that can be passed to llmclient."

## Must-Ask Checklist Resolution
- **Interface type**: Library (Python API) — known from context
- **Target platform**: Cross-platform — known from context
- **Data persistence**: In-memory only — stated in user request ("returns a list")
- **User type**: Developers — known from context
