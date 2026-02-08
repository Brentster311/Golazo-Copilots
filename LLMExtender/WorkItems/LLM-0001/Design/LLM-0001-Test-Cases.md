# Test Cases — LLM-0001

## Test Case Mapping to Acceptance Criteria

| AC# | Acceptance Criterion | Test Case(s) | File |
|-----|---------------------|--------------|------|
| AC-1 | LLMClient accepts config and resolves provider | TC-1 | test_client.py |
| AC-2 | LLMClient.complete(prompt) → str | TC-2 | test_client.py |
| AC-3 | LLMClient.acomplete(prompt) → str | TC-3 | test_client.py |
| AC-4 | Abstract base class / protocol for provider | TC-4 | test_client.py |
| AC-5 | Concrete OpenAI-compatible provider | TC-5, TC-8, TC-9 | test_client.py, test_openai_provider.py |
| AC-6 | Unsupported provider raises clear error | TC-6 | test_client.py |
| AC-7 | Docstrings and type hints on public API | TC-7 | test_client.py |

## Additional Test Coverage

| Test ID | Description | File |
|---------|------------|------|
| TC-8 | OpenAIProvider posts correct HTTP request (endpoint, payload, auth header) | test_openai_provider.py |
| TC-9 | Async HTTP request sends correctly | test_openai_provider.py |
| TC-10 | HTTP error propagation (500 sync + async) | test_client.py |
| TC-11 | Custom base_url passed through to provider | test_client.py |
| — | Context manager support (sync + async) | test_client.py |
| — | api_key hidden from repr | test_client.py |
| — | Error hierarchy (UnsupportedProviderError, ProviderError ⊂ LLMExtenderError) | test_client.py |
| — | 401 / 429 error codes raise ProviderError | test_openai_provider.py |

## Coverage Summary

- **30 tests** covering happy paths, error paths, edge cases, and structural assertions
- All 7 acceptance criteria have direct test coverage
- HTTP mocking via `respx` — no real API calls in tests
- Async tests via `pytest-asyncio` with `asyncio_mode = "auto"`
