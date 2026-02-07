# Role Decision Notes: Program Manager

**Work Item:** LLM-0001  
**Role:** program-manager  
**Date:** 2026-02-07

---

## Decisions

### 1. httpx over requests/aiohttp
Chose `httpx` as the sole HTTP dependency because it provides both sync (`httpx.Client`) and async (`httpx.AsyncClient`) with the same API surface. This avoids managing two separate HTTP libraries and keeps the dependency footprint minimal.

### 2. ABC over Protocol for Provider Interface
Chose ABC (`LLMProvider`) over Protocol for the initial implementation. ABCs give clear instantiation-time errors if required methods are missing. Protocol (structural/duck typing) can be layered on later if needed.

### 3. Provider Registry as Simple Dict
A plain dictionary mapping `str → type[LLMProvider]` is sufficient. No need for plugin systems, entry points, or decorators at this stage. New providers are added by inserting into the dict.

### 4. No asyncio.run() Inside the Library
The library never manages the event loop. `complete()` uses sync `httpx.Client`. `acomplete()` is a coroutine the caller awaits. This avoids event loop conflicts in frameworks like FastAPI, Jupyter, etc.

### 5. Minimal Config Shape
`LLMClientConfig` only has `provider`, `model`, `api_key`, and optional `base_url` for this story. LLM-0002 extends it with persistence; LLM-0003 replaces `api_key` with auth strategies. Keeping it minimal avoids forward-coupling.

## Open Questions
- None blocking.
