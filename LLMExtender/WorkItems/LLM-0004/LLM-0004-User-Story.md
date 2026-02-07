# LLM-0004: Azure OpenAI Provider

## Status: IN PROGRESS

## User Story

> As a developer using LLM Extender,
> I want an `AzureOpenAIProvider` that targets Azure OpenAI endpoints,
> So that I can call Azure-hosted models using Azure AD token auth via the existing auth strategies.

## Acceptance Criteria

1. New `AzureOpenAIProvider` uses Azure's URL format: `/openai/deployments/{deployment}/chat/completions?api-version=...`
2. `LLMConfig` accepts `deployment` and `api_version` fields for Azure OpenAI
3. Provider registered in `PROVIDER_REGISTRY` as `"azure_openai"`
4. Works with `CallbackAuth` + `DefaultAzureCredential` for token-based auth
5. Auth token passed as `Authorization: Bearer <token>` header (not as `api-key`)
6. Sync and async support matching existing provider interface (`complete()` / `acomplete()`)
7. No security artifacts stored or logged

## Known Azure Details

| Detail | Value |
|--------|-------|
| Endpoint | `https://open-ai-poc.openai.azure.com/` |
| Deployment | `gpt-5.2` |
| API version | `2024-12-01-preview` (configurable) |
| Auth | Azure AD (local API keys disabled) |

## Technical Notes

- Azure OpenAI URL pattern: `{base_url}/openai/deployments/{deployment}/chat/completions?api-version={api_version}`
- Standard OpenAI URL pattern (existing): `{base_url}/v1/chat/completions`
- Auth header for Azure AD uses `Authorization: Bearer <token>` instead of OpenAI's `Authorization: Bearer <api-key>` — same header format, different credential source
- The existing `CallbackAuth` strategy already supports wrapping `DefaultAzureCredential().get_token()` as the callback
- `azure-identity` is an optional dependency (already established in LLM-0003 for `ManagedIdentityAuth`)

## Out of Scope

- Azure OpenAI API key auth (local auth is disabled on PO's resource)
- Responses API / streaming — only chat completions
- Model deployment management
