# LLM-0004 — Program Manager Notes

## Date: 2026-02-07

## Summary
Produced design doc and review comments for Azure OpenAI Provider.

## Key Decisions
- **D1**: Reuse `model` as deployment name — PO approved
- **D2**: Extract `BaseOpenAIProvider` — PO overrode initial recommendation to keep providers separate; requested shared base class
- **D3**: Fail-fast validation for `base_url` and `api_version` — PO approved
- **D5**: No auth changes needed — PO approved

## Risks Identified
- Refactor of `OpenAIProvider` inheritance has regression risk (mitigated by 30 existing tests)
- Token expiry for long-lived clients is a known limitation (deferred)
