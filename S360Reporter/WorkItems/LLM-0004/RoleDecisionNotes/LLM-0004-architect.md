# Role Decision Notes: Architect — LLM-0004

## Decisions Made

1. **Architecture approved**: Clean extension via new provider class + registry entry.
2. **No breaking changes**: Config fields are optional, client layer untouched.
3. **Config validation**: Provider validates required fields (base_url, deployment) at init time.
