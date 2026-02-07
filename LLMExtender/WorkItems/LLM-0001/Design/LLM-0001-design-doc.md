# Design Doc: LLM-0001 — Provider-Abstracted LLM Client

**Work Item:** LLM-0001  
**Author:** Program Manager  
**Date:** 2026-02-07  
**Status:** DRAFT

---

## 1. Summary

Build a Python library exposing a `LLMClient` class that delegates completion calls to provider-specific implementations via a strategy pattern. The client supports both synchronous and asynchronous operations. Provider selection is driven entirely by a config object passed to the constructor.

## 2. Problem Statement

Developers who integrate LLM capabilities into Python applications are tightly coupled to a single provider's SDK. Switching providers (e.g., OpenAI → Anthropic, or cloud → local) requires rewriting calling code. This creates vendor lock-in and makes testing difficult.

## 3. Business Case

| Dimension | Detail |
|---|---|
| **Why now** | LLM provider landscape is rapidly evolving; flexibility to switch providers is a competitive advantage |
| **Impact** | Developers can swap providers in one line of config, enabling cost optimization and resilience |
| **KPIs** | N/A for library — success = passing tests and usability |

## 4. Stakeholders

| Role | Interest |
|---|---|
| Library consumers (Python devs) | Clean, type-hinted API for LLM calls |
| Future work items (LLM-0002, LLM-0003) | Depend on the provider protocol and config interface defined here |

## 5. Functional Requirements

| ID | Requirement | Source |
|---|---|---|
| FR-1 | `LLMClient(config)` constructor accepting a config dataclass | AC-1 |
| FR-2 | `LLMClient.complete(prompt: str) -> str` — synchronous completion | AC-2 |
| FR-3 | `LLMClient.acomplete(prompt: str) -> str` — async completion | AC-3 |
| FR-4 | `LLMProvider` abstract base class / Protocol defining the provider contract | AC-4 |
| FR-5 | `OpenAIProvider` concrete implementation for OpenAI-compatible APIs | AC-5 |
| FR-6 | `UnsupportedProviderError` raised for unknown provider names | AC-6 |
| FR-7 | Docstrings and type hints on all public surfaces | AC-7 |

## 6. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-1 | Abstraction overhead < 1ms on top of provider latency |
| NFR-2 | Installable via `pip install -e .` |
| NFR-3 | Python 3.10+ compatibility |
| NFR-4 | Cross-platform: Windows, macOS, Linux |

## 7. Proposed Approach

### 7.1 Package Structure

```
llm_extender/
├── __init__.py          # Public API exports
├── client.py            # LLMClient class
├── config.py            # LLMClientConfig dataclass (minimal for this story)
├── providers/
│   ├── __init__.py
│   ├── base.py          # LLMProvider ABC/Protocol
│   └── openai.py        # OpenAIProvider implementation
├── exceptions.py        # UnsupportedProviderError, etc.
└── py.typed             # PEP 561 marker
```

### 7.2 Core Classes

**`LLMClientConfig`** (dataclass)
```
- provider: str          # e.g., "openai"
- model: str             # e.g., "gpt-4"
- api_key: str           # Direct key for this story; replaced by auth manager in LLM-0003
- base_url: str | None   # Optional endpoint override
```

**`LLMProvider`** (ABC)
```
- complete(prompt: str) -> str          # Abstract — sync
- acomplete(prompt: str) -> str         # Abstract — async
```

**`LLMClient`** (public facade)
```
- __init__(config: LLMClientConfig)     # Resolves provider from config.provider
- complete(prompt: str) -> str           # Delegates to provider.complete()
- acomplete(prompt: str) -> str          # Delegates to provider.acomplete()
```

**`OpenAIProvider`** (concrete)
```
- Uses `httpx` for sync and async HTTP calls to OpenAI-compatible /chat/completions endpoint
- Constructs request from prompt + config.model
- Returns content string from response
```

### 7.3 Provider Registry

A simple dictionary mapping provider names to provider classes:

```python
PROVIDER_REGISTRY: dict[str, type[LLMProvider]] = {
    "openai": OpenAIProvider,
}
```

`LLMClient.__init__` looks up `config.provider` in this registry. If not found → `UnsupportedProviderError`.

### 7.4 Sync/Async Design

- `OpenAIProvider.complete()` uses `httpx.Client` (sync)
- `OpenAIProvider.acomplete()` uses `httpx.AsyncClient` (async)
- No `asyncio.run()` wrapping — sync and async are independent code paths

### 7.5 Dependencies

| Package | Purpose | Required? |
|---|---|---|
| `httpx` | HTTP client for sync + async | Yes |

Chose `httpx` over `requests` because it natively supports both sync and async with the same API surface, avoiding the need for two HTTP libraries.

## 8. Alternatives Considered

| Alternative | Why Rejected |
|---|---|
| Use `openai` SDK directly | Couples us to one provider's SDK; not provider-agnostic |
| Use `litellm` | Heavy dependency; we want a thin abstraction we control |
| Use `aiohttp` for async + `requests` for sync | Two libraries with different APIs; `httpx` unifies both |
| Protocol (structural typing) instead of ABC | ABC provides clearer error messages when methods are missing; Protocol can be added later if duck-typing is preferred |

## 9. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| OpenAI API format changes | Low | Medium | Pin to known `/v1/chat/completions` format; version in config |
| `httpx` breaking changes | Low | Low | Pin version range in `pyproject.toml` |
| Async event loop conflicts | Medium | Medium | Never call `asyncio.run()` inside library; let caller manage the loop |

## 10. Dependencies on Other Work Items

| Dependency | Direction | Detail |
|---|---|---|
| LLM-0002 | Forward | Config persistence will extend `LLMClientConfig` — this story defines the minimal config shape |
| LLM-0003 | Forward | Auth manager will replace `api_key` field with strategy-based resolution — provider interface stays the same |

## 11. Migration / Rollout / Rollback

- **New library** — no migration needed
- **Rollout:** Publish to internal use, then PyPI if desired
- **Rollback:** Revert package version

## 12. Observability Plan

- None for initial version
- Future: optional logging at DEBUG level for request/response metadata (no secrets)

## 13. Test Strategy Summary

| Layer | What | How |
|---|---|---|
| Unit | `LLMClient` dispatches to correct provider | Mock provider; assert delegation |
| Unit | Unknown provider raises `UnsupportedProviderError` | Pass invalid provider name |
| Unit | `OpenAIProvider.complete()` constructs correct HTTP request | Mock `httpx`; assert request body |
| Unit | `OpenAIProvider.acomplete()` constructs correct HTTP request | Mock `httpx.AsyncClient`; assert request body |
| Integration | End-to-end call against a real/mock OpenAI endpoint | Optional; requires API key or mock server |
