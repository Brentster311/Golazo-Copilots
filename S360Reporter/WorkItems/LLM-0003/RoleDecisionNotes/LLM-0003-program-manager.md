# Role Decision Notes: Program Manager — LLM-0003

## Decisions Made

1. **Strategy pattern**: Chosen over single-class-with-mode for extensibility and SRP.
2. **Optional azure-identity**: Import-time check avoids forcing the dependency on non-Azure users.
3. **CallbackAuth dual-mode**: Supports both sync and async callbacks with fallback — covers all integration patterns.
4. **Client integration**: `auth` parameter on `LLMClient.__init__` resolves and replaces `api_key` — minimal coupling.
