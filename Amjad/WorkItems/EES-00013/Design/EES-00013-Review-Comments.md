# EES-00013 Design Review Comments

## Review Summary

The design is well-structured and feasible. The tool-calling approach is a clear improvement over single-shot JSON extraction. A few items below need clarification or strengthening before implementation.

## Comments

### C-1: `get_existing_rules` needs a source parameter [Minor]

**Location**: FR-1 Tool Definitions — `get_existing_rules`  
**Issue**: The design says "Returns confirmed rules" but doesn't specify where these come from. The current `extract()` signature only takes `incident_text` and `ontology`. There's no rules parameter.  
**Recommendation**: Either (a) add an optional `existing_rules: list[Rule] = []` parameter to `extract()`, or (b) have `get_existing_rules` return an empty list with a note that callers can provide rules in a future enhancement. Option (b) is simpler and doesn't change the API.  
**Impact**: Low — the tool is still useful even returning empty; the model at least calls it first.

### C-2: Token usage tracking assumes `response.usage` is always populated [Minor]

**Location**: NFR — Token logging  
**Issue**: Azure OpenAI streaming responses may not populate `usage`. Since we're not streaming, this should be fine, but worth asserting.  
**Recommendation**: Guard with `if response.usage:` before accessing `total_tokens`.

### C-3: No specification for what happens at MAX_TURNS cutoff [Clarification]

**Location**: FR-2 Agentic Loop  
**Issue**: Design says "loop guard with early exit" but doesn't specify return behavior. Should it return whatever was collected, raise an error, or log a warning?  
**Recommendation**: Return collected `LLMResponse` with whatever was gathered + log a WARNING. Not an error — partial extraction is still useful.

### C-4: `submit_fact` instance default handling [Clarification]

**Location**: FR-1 — `submit_fact` schema  
**Issue**: Schema shows `"default": "*"` for instance, but OpenAI tool calling doesn't apply JSON Schema defaults. The handler needs to default `instance` to `"*"` if missing.  
**Recommendation**: Handle in the Python tool handler: `instance = args.get("instance", "*")`.

### C-5: Unknown tool name handling not specified [Gap]

**Location**: FR-2 Agentic Loop  
**Issue**: What if the model invokes a tool name not in our list?  
**Recommendation**: Return an error message: `"Unknown tool: {name}. Available tools: get_ontology, get_existing_rules, submit_fact, submit_rule, set_root_cause"`. Count as a rejection.

### C-6: Multiple `set_root_cause` calls [Edge case]

**Location**: FR-1 — `set_root_cause`  
**Issue**: What if the model calls `set_root_cause` more than once?  
**Recommendation**: Last call wins. Log a debug message noting the override.

### C-7: Existing test fixtures use v1 format [Migration]

**Location**: Test Strategy  
**Issue**: `mock_llm_response.json` uses v1 `then` format. The new implementation won't use `_parse_response()` at all, so these fixtures become irrelevant.  
**Recommendation**: Keep old fixtures for any backward-compat tests, create new fixtures that simulate tool-call response sequences.

## Verdict

**Approved with minor comments.** None of the comments are blocking — implement C-1 through C-7 inline during development. No scope changes required.

---

## Architect Notes

### A-1: Contract Preservation — `fact-extraction` Capability

**Capability**: `fact-extraction`  
**Contract**: `FactExtractor.extract(text, ontology_nouns) -> LLMResponse`  
**Assessment**: ✅ Contract preserved. Signature unchanged, return type unchanged. Transitive dependents (`cli-orchestration`, `gui`) need no changes.

### A-2: Tool Schema Serialization — Use `openai` SDK Types

**Concern**: Tool definitions should use `ChatCompletionToolParam` typed dicts from the `openai` SDK rather than raw dicts, for type safety and forward compatibility.  
**Recommendation**: Define tools using the typed dict pattern:
```python
tools = [
    {"type": "function", "function": {"name": "...", "parameters": {...}}}
]
```
The `openai` SDK accepts this shape as `Iterable[ChatCompletionToolParam]`. No need to import the type explicitly — plain dicts with correct structure work.

### A-3: Error Isolation — Tool Handlers Must Not Raise

**Concern**: If a tool handler raises an unhandled exception, it could crash the loop.  
**Recommendation**: Wrap each handler dispatch in try/except. Return the exception message as the tool result string. Only `LLMError` from the API call itself should propagate.

### A-4: Security — No Secrets in Tool Results

**Concern**: `get_ontology()` and `get_existing_rules()` return domain data. Verify no secrets/credentials leak into tool result strings.  
**Assessment**: ✅ Ontology nouns and rules contain only domain knowledge (noun names, properties, rule conditions). No PII, credentials, or connection strings. Safe.

### A-5: Dependency Review

| Dependency | Status | Risk |
|-----------|--------|------|
| `openai>=1.0` | ✅ Already installed | None — tool calling is stable API |
| `azure.identity` | ✅ Already installed | None — unchanged |
| No new deps | ✅ | None |

### A-6: Rollback Safety

**Assessment**: ✅ Single-file change (`fact_extractor.py`). Git revert restores previous behavior. No database migrations, config changes, or infrastructure changes.

### A-7: `tool_choice="auto"` Default Behavior

**Concern**: OpenAI's `tool_choice="auto"` means the model *may* choose not to call tools. This is intentional (TC-11 covers it), but worth noting that different model versions may behave differently.  
**Recommendation**: If `get_ontology` is never called on first turn, consider `tool_choice="required"` for the first turn only, then `"auto"` for subsequent turns. Decision: **defer to implementation** — start with `"auto"` throughout, add `"required"` if empirically needed.

### A-8: Token Logging — Guard Against Missing `usage`

**Concern**: Per QA comment C-2, `response.usage` may be `None` in edge cases.  
**Recommendation**: `total_tokens += response.usage.total_tokens if response.usage else 0`. Simple guard.

### Architect Verdict

**Approved.** Architecture is sound. Single-file refactor with preserved contract. No coupling risks. Address A-3 (handler error isolation) and A-8 (usage guard) during implementation.
