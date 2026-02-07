# LLM-0004 — Architect Notes

## Date: 2026-02-07

## Summary
Reviewed design for architectural alignment, security, and contracts. No blocking issues found.

## Decisions
- **A1**: `_get_url()` and `_build_payload()` are abstract methods in `BaseOpenAIProvider` — forces subclasses to be explicit
- **A2**: Validation errors use `ProviderError` — consistent with library exception hierarchy
- **A3**: `api_version` goes on `LLMConfig` — single source of truth pattern

## Security Review
- Token flows through existing `api_key` field with `repr=False` — no new security surface
- No changes to auth layer — existing `CallbackAuth` pattern handles Azure AD tokens
- No credentials logged or stored per library security policy

## Refactor Risk Assessment
- `BaseOpenAIProvider` extraction changes `OpenAIProvider`'s inheritance chain
- 30 existing tests (`test_openai_provider.py` + `test_client.py`) provide regression coverage
- Public API surface unchanged — `OpenAIProvider` still exposes same methods

## No New User Stories Required
