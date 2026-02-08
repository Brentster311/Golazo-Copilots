# Role Decision Notes: Architect — LLM-0003

## Decisions Made

1. **Architecture approved**: Strategy pattern aligns with provider pattern from LLM-0001.
2. **Contracts verified**: `resolve() -> str` / `aresolve() -> str` — minimal and clear.
3. **Security validated**: Base class safe repr, no logging, no persistence. Dedicated security tests.
4. **Optional dep pattern**: `azure-identity` guarded by import-time check — clean.
5. **No new work items needed**.
