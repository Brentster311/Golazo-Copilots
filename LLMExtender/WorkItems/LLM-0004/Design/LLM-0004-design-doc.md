# LLM-0004 Design Document: Azure OpenAI Provider

## Overview

Add an `AzureOpenAIProvider` that enables LLM Extender to call Azure OpenAI Service endpoints using Azure AD token authentication.

## Problem Statement

The existing `OpenAIProvider` targets the standard OpenAI URL format (`/v1/chat/completions`). Azure OpenAI uses a different URL scheme (`/openai/deployments/{deployment}/chat/completions?api-version=...`) and requires an `api-version` query parameter. A dedicated provider is needed.

## Design

### 1. Config Changes — Add `api_version` Field

Add one optional field to `LLMConfig`:

```python
api_version: str | None = None
```

The `model` field will double as the Azure deployment name. This is semantically correct: in Azure OpenAI, you select a deployment (which is backed by a model), and the deployment name is what routes the request — equivalent to `model` in standard OpenAI.

**Why not a separate `deployment` field?** The `model` field already serves as the "which model to talk to" selector. Adding a separate `deployment` field would mean two fields that both answer the same question for different providers. Reusing `model` keeps the config simple and the user's mental model consistent: "I set `model` to the thing I want to talk to."

### 2. New Provider — `AzureOpenAIProvider`

A new class in `llm_extender/providers/azure_openai.py` that inherits from `LLMProvider` directly (not from `OpenAIProvider`).

**Why not subclass `OpenAIProvider`?**
- The URL construction is fundamentally different
- Azure OpenAI doesn't require `model` in the request payload (it's implicit from the deployment)
- Subclassing would mean overriding most methods, violating LSP
- Composition via shared helpers would be premature — the classes are small

**Key differences from `OpenAIProvider`:**

| Aspect | OpenAIProvider | AzureOpenAIProvider |
|--------|---------------|-------------------|
| URL | `{base}/v1/chat/completions` | `{base}/openai/deployments/{model}/chat/completions?api-version={ver}` |
| Payload `model` field | Required | Omitted (deployment determines model) |
| `base_url` required | No (defaults to api.openai.com) | Yes (no sensible default) |
| `api_version` required | No | Yes |
| Auth header | `Authorization: Bearer {api_key}` | `Authorization: Bearer {token}` (same format) |

**Shared behavior** (response parsing, error handling) will be duplicated rather than extracted. These are ~10 lines each and extracting a shared base would be premature abstraction for two providers.

### 3. Provider Registration

```python
PROVIDER_REGISTRY: dict[str, type[LLMProvider]] = {
    "openai": OpenAIProvider,
    "azure_openai": AzureOpenAIProvider,
}
```

### 4. Validation

`AzureOpenAIProvider.__init__` will raise `ProviderError` if:
- `config.base_url` is `None` or empty (Azure requires an explicit endpoint)
- `config.api_version` is `None` or empty (Azure requires an API version)

These are fail-fast checks in the constructor, not deferred to first call.

### 5. Public Exports

Add `AzureOpenAIProvider` to `llm_extender/__init__.py` and `__all__`.

### 6. Auth Integration

No changes needed to the auth layer. The existing flow works:

```python
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
auth = CallbackAuth(lambda: credential.get_token("https://cognitiveservices.azure.com/.default").token)

config = LLMConfig(
    provider="azure_openai",
    model="gpt-5.2",  # deployment name
    base_url="https://open-ai-poc.openai.azure.com",
    api_version="2024-12-01-preview",
)

with LLMClient(config, auth=auth) as client:
    response = client.complete("Hello from LLM Extender!")
```

The `CallbackAuth.resolve()` returns the token string → `LLMClient` puts it into `config.api_key` → `AzureOpenAIProvider` uses it as `Authorization: Bearer {token}`.

## File Changes Summary

| File | Change |
|------|--------|
| `llm_extender/config.py` | Add `api_version: str \| None = None` field |
| `llm_extender/providers/azure_openai.py` | New file — `AzureOpenAIProvider` class |
| `llm_extender/client.py` | Import + register `AzureOpenAIProvider` |
| `llm_extender/__init__.py` | Export `AzureOpenAIProvider` |
| `tests/test_azure_openai_provider.py` | New file — unit tests |

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| API version goes stale | Make it a required config field, not a hardcoded default |
| Token expiry mid-session | Out of scope for LLM-0004 (auth resolves once at client creation per LLM-0003 design) |
| Response format differs from OpenAI | Azure OpenAI uses the same response schema for chat completions; verified via playground |
