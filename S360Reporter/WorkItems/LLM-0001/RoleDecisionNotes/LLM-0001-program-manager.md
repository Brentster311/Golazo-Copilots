# Role Decision Notes: Program Manager — LLM-0001

## Decisions Made

1. **Single HTTP library**: Selected `httpx` over `requests`+`aiohttp` to cover both sync and async with one dependency.
2. **Registry pattern**: Simple dict-based `PROVIDER_REGISTRY` over plugin discovery — appropriate for current scale.
3. **Dataclass config**: `LLMConfig` as a dataclass rather than raw dict for type safety and `repr` control.
4. **Context manager support**: Added sync and async context manager protocols for deterministic resource cleanup.
5. **Test strategy**: `respx` for HTTP mocking, `pytest-asyncio` for async test support, structured by test case IDs mapping to acceptance criteria.

## Open Questions

- None — all resolved during implementation.
