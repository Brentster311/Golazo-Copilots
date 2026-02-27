# Test Cases — LLM-0004

## Test Case Mapping to Acceptance Criteria

| AC# | Acceptance Criterion | Test Case(s) |
|-----|---------------------|--------------|
| AC-1 | Azure URL format | TC-1: Verify URL construction |
| AC-2 | LLMConfig accepts deployment and api_version | TC-2: Config fields exist |
| AC-3 | Registered as "azure_openai" | TC-3: Registry lookup |
| AC-4 | Works with CallbackAuth | TC-4: Auth integration |
| AC-5 | Bearer token header | TC-5: Auth header format |
| AC-6 | Sync and async support | TC-6, TC-7: complete/acomplete |
| AC-7 | No security artifacts logged | Covered by existing security tests |

## Additional Tests

- Missing deployment raises error
- Missing base_url raises error
- HTTP error propagation (4xx/5xx)
- Custom api_version used in URL
