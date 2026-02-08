# Role Decision Notes: Project Owner Assistant — LLM-0004

## Decisions Made

1. **Interface type**: Python library (API only) — consistent with LLM-0001/LLM-0003.
2. **Target platform**: Cross-platform, Python 3.10+.
3. **Data persistence**: In-memory only.
4. **User type**: Technical (Python developers).
5. **Scope**: Azure OpenAI provider only — no API key auth (disabled on PO's resource), no streaming, no deployment management.
6. **Config extension**: `deployment` and `api_version` fields added to `LLMConfig` as optional fields.
7. **Auth pattern**: Uses existing `CallbackAuth` + `DefaultAzureCredential` — no new auth strategies needed.

## Assumptions Documented

- Azure AD token auth via `Authorization: Bearer <token>` header
- Default API version: `2024-12-01-preview` (configurable)
- URL pattern: `{base_url}/openai/deployments/{deployment}/chat/completions?api-version={api_version}`
