# EES-00013 Architect Decision Notes

## Architecture Assessment

### Contract Compatibility
- `fact-extraction` capability contract: `FactExtractor.extract(text, ontology_nouns) -> LLMResponse` — **preserved exactly**
- Transitive dependents `cli-orchestration` and `gui` call `extract()` and consume `LLMResponse` — **no changes needed**
- `data-models` dependency provides `Rule`, `RuleOutput`, `Fact`, `LLMResponse` — all used correctly in tool handler design

### Key Architectural Decisions

1. **Tool handlers as private methods, not standalone functions**: Keeps state (`collected_facts`, `collected_rules`, `root_cause`) encapsulated within the `extract()` call. No need for a separate class.

2. **Error isolation via try/except in handler dispatch (A-3)**: Each tool handler invocation wrapped to prevent crashes. Only API-level errors propagate as `LLMError`.

3. **`tool_choice="auto"` throughout (A-7)**: Start simple. If first-turn behavior is problematic (model skips `get_ontology`), can switch first turn to `"required"` — but that's a future concern.

4. **No new abstractions**: No `ToolRegistry`, no `AgentLoop` class. The loop is simple enough to be a `for` loop inside `extract()`. YAGNI.

5. **Token usage guard (A-8)**: `if response.usage` check before accessing `total_tokens`.

### Security Review
- No credentials in tool results ✅
- No PII in ontology/rule data ✅
- Azure AD token provider unchanged ✅
- `ChainedTokenCredential` per TechBestPractices.md ✅

### Risks Accepted
- Multi-turn latency increase (~2–4x) — acceptable for batch extraction
- Model behavior may vary across deployments — mitigated by schema enforcement in tool params
