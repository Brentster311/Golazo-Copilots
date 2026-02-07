# Role Decision Notes: Architect

**Work Item:** LLM-0001  
**Role:** architect  
**Date:** 2026-02-07

---

## Architectural Decisions

### A1: Exception Hierarchy
Added `LLMExtenderError` base, `UnsupportedProviderError`, `ProviderError`. Callers get a consistent exception contract. This is part of the public API and belongs in this story.

### A2: httpx Client Lifecycle
Providers must manage `httpx.Client`/`httpx.AsyncClient` lifecycle. `LLMClient` and providers will support context manager protocol. This prevents connection leaks — critical for long-running applications.

### A3: Config Naming → `LLMConfig`
Renamed from `LLMClientConfig` to `LLMConfig`. Aligns with LLM-0002 which extends the same config. One name across the library.

### A4: api_key Hidden from repr
`api_key` field uses `field(repr=False)` on the dataclass even in this story. Defense in depth — prevents accidental exposure in logs/debug output before LLM-0003 replaces it.

### A5: Default Timeout
Set 30s default timeout on httpx clients. `httpx` defaults to no timeout, which would cause indefinite hangs on unresponsive providers. Configurable via `LLMConfig.timeout` field.

## Contracts Summary

```
LLMConfig(provider: str, model: str, api_key: str, base_url: str | None, timeout: float = 30.0)
LLMProvider(ABC): complete(str) -> str, acomplete(str) -> str, close(), aclose()
LLMClient(config): complete(str) -> str, acomplete(str) -> str, close(), aclose(), __enter__, __exit__, __aenter__, __aexit__
Exceptions: LLMExtenderError > UnsupportedProviderError, ProviderError
```

## No New User Stories Required
All additions (exception hierarchy, lifecycle, timeout) are within scope of the existing acceptance criteria — they are implementation details of a well-designed public API.
