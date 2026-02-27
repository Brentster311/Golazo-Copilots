# Role Decision Notes: Program Manager — LLM-0004

## Decisions Made

1. **Reuse pattern**: Same provider ABC, same response parsing, same registry pattern.
2. **Backward-compatible config**: `deployment` and `api_version` are optional fields with defaults.
3. **No new dependencies**: Uses httpx (already installed).
