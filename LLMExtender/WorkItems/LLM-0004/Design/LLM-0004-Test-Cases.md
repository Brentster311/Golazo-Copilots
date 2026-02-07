# LLM-0004 Test Cases

## Test File: `tests/test_azure_openai_provider.py`

### AC1 — Azure URL Format

| ID | Test | Expected | AC |
|----|------|----------|-----|
| TC-01 | `_get_url()` returns `{base_url}/openai/deployments/{model}/chat/completions?api-version={api_version}` | URL matches Azure format exactly | AC1 |
| TC-02 | `_get_url()` strips trailing slash from `base_url` before building path | No double slashes in URL | AC1 |

### AC2 — Config `api_version` Field

| ID | Test | Expected | AC |
|----|------|----------|-----|
| TC-03 | `LLMConfig` accepts `api_version` kwarg and stores it | `config.api_version == "2024-12-01-preview"` | AC2 |
| TC-04 | `LLMConfig` defaults `api_version` to `None` | `config.api_version is None` | AC2 |

### AC3 — Provider Registration

| ID | Test | Expected | AC |
|----|------|----------|-----|
| TC-05 | `PROVIDER_REGISTRY["azure_openai"]` is `AzureOpenAIProvider` | Registry lookup succeeds | AC3 |
| TC-06 | `LLMClient` with `provider="azure_openai"` instantiates without error (given valid config) | No exception | AC3 |

### AC4 — Auth Integration (Bearer Token)

| ID | Test | Expected | AC |
|----|------|----------|-----|
| TC-07 | Provider sends `Authorization: Bearer {token}` header | Request header matches | AC4, AC5 |

### AC5 — Validation (Fail-Fast)

| ID | Test | Expected | AC |
|----|------|----------|-----|
| TC-08 | Constructor raises `ProviderError` when `base_url` is `None` | `ProviderError` with message mentioning `base_url` | D3 |
| TC-09 | Constructor raises `ProviderError` when `base_url` is empty string | `ProviderError` | D3 |
| TC-10 | Constructor raises `ProviderError` when `api_version` is `None` | `ProviderError` with message mentioning `api_version` | D3 |
| TC-11 | Constructor raises `ProviderError` when `api_version` is empty string | `ProviderError` | D3 |

### AC6 — Sync and Async Support

| ID | Test | Expected | AC |
|----|------|----------|-----|
| TC-12 | `complete(prompt)` returns parsed content from mocked 200 response | Content string matches expected | AC6 |
| TC-13 | `acomplete(prompt)` returns parsed content from mocked 200 response | Content string matches expected | AC6 |

### Payload Tests

| ID | Test | Expected | AC |
|----|------|----------|-----|
| TC-14 | `_build_payload(prompt)` does NOT include `model` key | `"model" not in payload` | AC1 |
| TC-15 | `_build_payload(prompt)` includes `messages` with user role and prompt content | Correct message structure | AC1 |

### Error Handling (Inherited from BaseOpenAIProvider)

| ID | Test | Expected | AC |
|----|------|----------|-----|
| TC-16 | HTTP 401 raises `ProviderError` with status code in message | `ProviderError("...401...")` | AC6 |
| TC-17 | HTTP 500 raises `ProviderError` | `ProviderError("...500...")` | AC6 |
| TC-18 | Malformed response (missing `choices`) raises `ProviderError` | `ProviderError("Unexpected response format...")` | AC6 |

## Test File: `tests/test_base_openai_provider.py`

### BaseOpenAIProvider Refactor Regression

| ID | Test | Expected | AC |
|----|------|----------|-----|
| TC-19 | `BaseOpenAIProvider` is abstract — cannot instantiate directly | `TypeError` | D2 |
| TC-20 | `OpenAIProvider` still passes all existing tests after refactor to inherit `BaseOpenAIProvider` | 30 existing tests green | D2 |

## Test File: `tests/test_config.py` (additions)

| ID | Test | Expected | AC |
|----|------|----------|-----|
| TC-21 | `LLMConfig(provider="azure_openai", model="gpt-5.2", api_version="2024-12-01-preview")` round-trips all fields | All fields accessible | AC2 |

---

**Total: 21 test cases** (18 new in azure provider file, 2 in base provider file, 1 config addition)
