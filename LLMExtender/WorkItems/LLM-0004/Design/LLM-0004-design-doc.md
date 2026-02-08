# Design Document — LLM-0004

## Summary

Add an `AzureOpenAIProvider` that targets Azure OpenAI endpoints using Azure AD token authentication, registered as `"azure_openai"` in the provider registry.

## Problem Statement

Azure OpenAI uses a different URL pattern (`/openai/deployments/{deployment}/chat/completions?api-version=...`) and requires deployment-specific configuration. The existing `OpenAIProvider` can't be reused directly.

## Proposed Approach

### Config Changes
Add two optional fields to `LLMConfig`:
- `deployment: str | None = None` — Azure deployment name
- `api_version: str | None = None` — Azure API version

### New Provider
`AzureOpenAIProvider(LLMProvider)`:
- URL: `{base_url}/openai/deployments/{deployment}/chat/completions?api-version={api_version}`
- Uses `Authorization: Bearer <token>` header (same format, different credential source)
- Validates that `base_url` and `deployment` are provided
- Same response format as OpenAI — can reuse parsing logic

### Registration
Add `"azure_openai": AzureOpenAIProvider` to `PROVIDER_REGISTRY`

### Files Modified
- `llm_extender/config.py` — add `deployment`, `api_version` fields
- `llm_extender/providers/azure_openai.py` — new file
- `llm_extender/providers/__init__.py` — export new provider
- `llm_extender/client.py` — register in `PROVIDER_REGISTRY`
- `llm_extender/__init__.py` — export new provider

### Files Created
- `tests/test_azure_openai_provider.py` — new test file

## Test Strategy

- Mock HTTP calls via `respx` (same pattern as OpenAI tests)
- Verify correct Azure URL construction
- Verify auth header format
- Verify sync/async support
- Verify error on missing deployment/base_url
- Verify registration in provider registry
