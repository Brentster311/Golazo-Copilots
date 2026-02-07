# Test Cases: LLM-0001

**Work Item:** LLM-0001  
**Author:** Quality Assurance  
**Date:** 2026-02-07

---

## Test Framework
- `pytest` + `pytest-asyncio`
- `httpx` mocking via `respx` or `pytest-httpx`

## Test File Structure
```
tests/
├── test_client.py           # LLMClient tests
├── test_openai_provider.py  # OpenAIProvider tests
└── conftest.py              # Shared fixtures
```

---

## TC-1: LLMClient accepts config and resolves provider (AC-1)

| Field | Value |
|---|---|
| **Type** | Unit — Happy Path |
| **Given** | A valid `LLMClientConfig` with `provider="openai"` |
| **When** | `LLMClient(config)` is called |
| **Then** | Client is created, internal provider is an `OpenAIProvider` instance |
| **Failure message** | `"LLMClient should resolve 'openai' to OpenAIProvider, got {type}"` |

## TC-2: LLMClient.complete() returns completion string (AC-2)

| Field | Value |
|---|---|
| **Type** | Unit — Happy Path |
| **Given** | A mocked HTTP endpoint returning `{"choices": [{"message": {"content": "Hello"}}]}` |
| **When** | `client.complete("Say hello")` is called |
| **Then** | Returns `"Hello"` |
| **Failure message** | `"complete() should return 'Hello', got '{result}'"` |

## TC-3: LLMClient.acomplete() returns completion string (AC-3)

| Field | Value |
|---|---|
| **Type** | Unit — Happy Path (async) |
| **Given** | A mocked async HTTP endpoint returning `{"choices": [{"message": {"content": "Hello"}}]}` |
| **When** | `await client.acomplete("Say hello")` is called |
| **Then** | Returns `"Hello"` |
| **Failure message** | `"acomplete() should return 'Hello', got '{result}'"` |

## TC-4: LLMProvider is an abstract base class (AC-4)

| Field | Value |
|---|---|
| **Type** | Unit — Structural |
| **Given** | `LLMProvider` class |
| **When** | Attempting to instantiate `LLMProvider()` directly |
| **Then** | Raises `TypeError` |
| **Failure message** | `"LLMProvider should not be directly instantiable"` |

## TC-5: OpenAIProvider exists and implements LLMProvider (AC-5)

| Field | Value |
|---|---|
| **Type** | Unit — Structural |
| **Given** | `OpenAIProvider` class |
| **When** | Checking `issubclass(OpenAIProvider, LLMProvider)` |
| **Then** | Returns `True` |
| **Failure message** | `"OpenAIProvider should be a subclass of LLMProvider"` |

## TC-6: Unsupported provider raises UnsupportedProviderError (AC-6)

| Field | Value |
|---|---|
| **Type** | Unit — Error Case |
| **Given** | Config with `provider="nonexistent"` |
| **When** | `LLMClient(config)` is called |
| **Then** | Raises `UnsupportedProviderError` with message containing `"nonexistent"` |
| **Failure message** | `"Should raise UnsupportedProviderError for unknown provider"` |

## TC-7: All public classes have docstrings (AC-7)

| Field | Value |
|---|---|
| **Type** | Unit — Documentation |
| **Given** | Public classes: `LLMClient`, `LLMProvider`, `OpenAIProvider`, `LLMClientConfig` |
| **When** | Checking `cls.__doc__` |
| **Then** | All have non-empty docstrings |
| **Failure message** | `"{cls.__name__} is missing a docstring"` |

## TC-8: OpenAIProvider.complete() sends correct HTTP request

| Field | Value |
|---|---|
| **Type** | Unit — Integration |
| **Given** | Mocked `httpx.Client.post` |
| **When** | `provider.complete("test prompt")` is called |
| **Then** | POST sent to `/v1/chat/completions` with correct model and messages payload |
| **Failure message** | `"OpenAIProvider should POST to /v1/chat/completions with correct payload"` |

## TC-9: OpenAIProvider.acomplete() sends correct async HTTP request

| Field | Value |
|---|---|
| **Type** | Unit — Integration (async) |
| **Given** | Mocked `httpx.AsyncClient.post` |
| **When** | `await provider.acomplete("test prompt")` is called |
| **Then** | POST sent to `/v1/chat/completions` with correct model and messages payload |
| **Failure message** | `"OpenAIProvider async should POST to /v1/chat/completions with correct payload"` |

## TC-10: Provider HTTP error is raised, not swallowed

| Field | Value |
|---|---|
| **Type** | Unit — Error Case |
| **Given** | Mocked HTTP endpoint returning 500 |
| **When** | `client.complete("test")` is called |
| **Then** | Raises an exception (not silently returns empty string) |
| **Failure message** | `"HTTP errors from provider should be raised, not swallowed"` |

## TC-11: Config with custom base_url is passed to provider

| Field | Value |
|---|---|
| **Type** | Unit — Edge Case |
| **Given** | Config with `base_url="https://custom.api.com"` |
| **When** | `client.complete("test")` is called |
| **Then** | HTTP request goes to `https://custom.api.com/v1/chat/completions` |
| **Failure message** | `"Custom base_url should be used for API requests"` |

---

## Acceptance Criteria Coverage Matrix

| AC | Test Cases |
|---|---|
| AC-1: LLMClient accepts config | TC-1 |
| AC-2: sync complete() | TC-2, TC-8 |
| AC-3: async acomplete() | TC-3, TC-9 |
| AC-4: Provider ABC | TC-4 |
| AC-5: OpenAI provider exists | TC-5 |
| AC-6: Unsupported provider error | TC-6 |
| AC-7: Docstrings and type hints | TC-7 |
