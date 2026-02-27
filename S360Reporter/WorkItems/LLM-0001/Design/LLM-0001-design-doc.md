# Design Document — LLM-0001

## Summary

Implement a provider-abstracted LLM client library in Python that supports both synchronous and asynchronous completion calls through a unified `LLMClient` interface. Provider selection is config-driven, enabling zero-code-change provider swaps.

## Problem Statement

Python developers integrating LLM capabilities need to write provider-specific code for each LLM service. Switching providers requires rewriting HTTP calls, response parsing, and auth handling. This coupling slows iteration and locks teams into specific vendors.

## Business Case

- **Why now:** LLM adoption is accelerating; teams need provider flexibility from day one.
- **Impact:** Developers can evaluate and switch LLM providers without code changes.
- **KPIs:** Library installable via pip, full test coverage, <1ms abstraction overhead.

## Stakeholders

- Python developers consuming the library
- Future work items (LLM-0003 Auth, LLM-0004 Azure provider) depend on this foundation

## Functional Requirements

1. `LLMClient` class accepts `LLMConfig` and resolves provider from registry
2. Synchronous `complete(prompt) -> str` method
3. Asynchronous `acomplete(prompt) -> str` method
4. Abstract `LLMProvider` base class defining the provider contract
5. Concrete `OpenAIProvider` for OpenAI-compatible APIs
6. Clear `UnsupportedProviderError` for unknown provider names
7. Docstrings and type hints on all public API surfaces

## Non-Functional Requirements

- Abstraction overhead < 1ms
- `pip install -e .` support
- Python 3.10+ cross-platform
- `api_key` excluded from `repr` output (security)

## Proposed Approach

- **Config**: `LLMConfig` dataclass with `provider`, `model`, `api_key`, `base_url`, `timeout`
- **Provider ABC**: `LLMProvider` with `complete()`, `acomplete()`, `close()`, `aclose()`
- **Registry**: `PROVIDER_REGISTRY` dict mapping name → class in `client.py`
- **Client facade**: `LLMClient` resolves provider from registry, delegates calls, supports context managers
- **HTTP layer**: `httpx` for sync + async HTTP (single dependency)

## Alternatives Considered

| Alternative | Reason Rejected |
|---|---|
| Use `requests` + `aiohttp` | Two deps instead of one; httpx covers both |
| Plugin-based provider discovery | Over-engineered for current scope; dict registry is simpler |
| Accept raw dict config | Dataclass gives type safety, IDE support, and repr control |

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| httpx breaking changes | Pinned to >=0.24, tested in CI |
| Provider response format drift | Response parsing isolated in `_extract_content` / `_check_response` |

## Dependencies

- `httpx>=0.24` (runtime)
- `pytest>=7.0`, `pytest-asyncio>=0.21`, `respx>=0.20` (dev)

## Migration / Rollout / Rollback

- New library, no migration needed. Versioned via `pyproject.toml`.

## Observability Plan

- None for initial version (deferred to future telemetry story).

## Test Strategy

- Unit tests for client creation, sync/async completion, error paths, provider ABC, docstring presence
- HTTP mocking via `respx`
- 30 tests covering TC-1 through TC-11 plus supplementary cases
