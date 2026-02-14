# EES-00013 — Project Owner Assistant Decision Notes

## Context
Discussion about switching from Azure OpenAI to GitHub Copilot SDK led to the realization that the real improvement is **multi-turn tool-calling**, not the SDK choice. The Azure OpenAI SDK already supports tool/function calling with the same capabilities.

## Key Decisions

### 1. Keep Azure OpenAI SDK (not Copilot SDK)
- No new dependency
- Auth already working (Azure AD)
- `response_format=json` available as fallback
- Copilot SDK adds async complexity (AsyncBridge) with no benefit for batch extraction

### 2. Multi-turn > single-shot
- Current single-shot approach crams fact extraction + rule proposal + root cause identification into one prompt with one JSON response
- Multi-turn lets the model: inspect context (ontology, existing rules) → extract facts one-by-one → propose rules referencing confirmed facts → iterate on rejections
- Tool parameter schemas enforce structure per-call (no more parsing 100-line JSON blobs)

### 3. Supersedes EES-00011
- EES-00011 was "update LLM prompt for v2 grammar" — this work item replaces that with a deeper architectural change
- EES-00011 can be closed as superseded

### 4. Scope boundary
- Same `extract()` signature and `LLMResponse` return type — GUI/CLI callers unaffected
- No GUI changes (EES-00012 remains separate)
