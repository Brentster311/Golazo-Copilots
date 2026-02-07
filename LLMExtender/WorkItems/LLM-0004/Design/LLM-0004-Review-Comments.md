# LLM-0004 Review Comments

## Date: 2026-02-07
## Reviewer: Program Manager

### Design Decisions Reviewed

| ID | Decision | PO Verdict |
|----|----------|------------|
| D1 | Reuse `model` field as Azure deployment name; add `api_version` field only | **Approved** |
| D2 | Extract `BaseOpenAIProvider` abstract base from `OpenAIProvider`; both providers inherit shared HTTP/parsing logic | **Approved** (PO overrode initial "keep separate" recommendation) |
| D3 | `base_url` and `api_version` required — fail-fast `ProviderError` in constructor | **Approved** |
| D5 | No auth layer changes — existing `CallbackAuth` + `DefaultAzureCredential` pipeline works | **Approved** |

### Observations

1. **D2 override**: PO explicitly requested shared base extraction. This is the right call — `_check_response`, `_extract_content`, `complete`/`acomplete` orchestration, and client lifecycle are identical between providers. Subclasses only differ in URL construction and payload shape.

2. **Refactor risk**: Extracting `BaseOpenAIProvider` from `OpenAIProvider` changes an existing class's inheritance chain. The 30 existing tests in `test_openai_provider.py` and `test_client.py` serve as the regression safety net.

3. **Token expiry**: Auth resolves once at `LLMClient` construction (LLM-0003 design). Long-lived clients with Azure AD tokens will eventually get 401s. This is a known limitation, not in scope for LLM-0004.

### No Blocking Issues Found

---

## Architect Notes

### Date: 2026-02-07

### Architectural Review

**Alignment**: Design aligns with existing provider/strategy patterns. `BaseOpenAIProvider` extraction is a clean refactor that doesn't change the public API surface.

**Contracts**: `AzureOpenAIProvider` has the same `complete(prompt) -> str` / `acomplete(prompt) -> str` contract as all providers. No new public methods.

**Security**: Auth token flows through the same `config.api_key` path as standard OpenAI. No new security surface. Token is never logged (existing `repr=False` on `api_key` field).

### Decisions

| ID | Decision | Rationale |
|----|----------|-----------|
| A1 | `BaseOpenAIProvider._get_url()` and `_build_payload()` are abstract methods (not overridable hooks with defaults) | Forces subclasses to be explicit about their URL and payload shape. No "accidental inheritance" of wrong behavior. |
| A2 | `AzureOpenAIProvider` validation errors use `ProviderError` (not `ValueError`) | Consistent with the library's exception hierarchy. All provider-related failures are `ProviderError`. |
| A3 | The `api_version` field goes on `LLMConfig` (not on provider constructor) | Config is the single source of truth for all provider settings. Keeps the `LLMClient(config)` pattern consistent. Provider reads from config, doesn't accept extra kwargs. |

### No New User Stories Required
