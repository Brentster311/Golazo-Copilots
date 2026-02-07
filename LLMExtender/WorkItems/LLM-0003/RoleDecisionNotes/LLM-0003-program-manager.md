# Role Decision Notes: Program Manager

**Work Item:** LLM-0003  
**Role:** program-manager  
**Date:** 2026-02-07

---

## Decisions

### 1. Strategy Pattern over Mode Enum
Each auth mechanism is a separate class implementing `AuthStrategy` ABC, rather than a single class with a `mode` parameter. This is more extensible — users can write custom strategies by subclassing, and each strategy's dependencies are isolated.

### 2. Both sync and async on AuthStrategy
`resolve()` and `aresolve()` on the ABC. `EnvVarAuth.aresolve()` just calls `resolve()` (env var lookup is instant). `ManagedIdentityAuth.aresolve()` uses azure-identity's async module. `CallbackAuth` accepts an optional async callback.

### 3. azure-identity as Optional
Only imported inside `ManagedIdentityAuth.__init__`. Users who don't need Azure MSI never need to install it. Clear `ImportError` message with install instructions.

### 4. CallbackAuth Accepts Both Sync and Async Callables
`CallbackAuth(callback, async_callback=None)`. If only sync is provided, `aresolve()` falls back to calling the sync callback. This covers the 80% case where users have a simple function.

### 5. Integration with LLM-0001 is Backward-Compatible
`LLMClient.__init__` gains an optional `auth` parameter. If provided, it replaces `config.api_key`. If not, `config.api_key` still works. No breaking changes.

## Open Questions
- None blocking.
