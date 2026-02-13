# Architect Decision Notes — EES-00007

## Decisions Made

1. **Approved `azure-kusto-data`** as the Kusto SDK — official Azure SDK, consistent with existing Azure dependency pattern.
2. **Graceful degradation** required: if `azure-kusto-data` not installed, Kusto button is disabled (not hidden). Import guard via try/except.
3. **KQL injection prevention**: Use `KustoClient` query parameters or sanitize incident ID input (strip to alphanumeric + hyphens only).
4. **ChainedTokenCredential reuse**: Same pattern as Azure OpenAI.
5. **Error contract**: `fetch_incident` raises `ValueError` (empty ID), `RuntimeError` (not found / Kusto errors) — no custom exception classes needed.

## Capability Impact
- 1 capability affected: `gui`
- No transitive impacts on other capabilities
