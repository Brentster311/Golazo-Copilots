# EES-00013 Design Doc — Multi-Turn Tool-Calling Fact Extractor

## Summary

Refactor `FactExtractor` from a single-shot JSON extraction to an **agentic tool-calling loop** on Azure OpenAI. The model inspects ontology and existing rules via read-only tools, then submits facts and rules through schema-validated tool calls. Invalid submissions return validation errors so the model can self-correct. The public `extract()` signature and return type (`LLMResponse`) are unchanged — callers are unaffected.

## Problem Statement

The current `FactExtractor.extract()` crams the entire ontology, rule schema, scope classification rules, variable-binding rules, and examples into a single ~100-line system prompt, then expects the LLM to produce a perfectly-formed JSON blob in one shot. This has several problems:

1. **Fragile output parsing** — one malformed field invalidates the entire extraction. The only recovery is a full retry.
2. **No iterative refinement** — the model cannot inspect what it just proposed, compare against existing rules, or correct a rejected submission.
3. **Schema drift** — the prompt still uses v1 grammar (`RuleThen` with noun/property/value). Updating it to v2 grammar (CHANGE_STATE/RULED_OUT/GAP) in a monolithic prompt is error-prone.
4. **Context overload** — the prompt mixes structural schema definition with domain instructions, leading to the model conflating or ignoring constraints.

## Business Case

- **Why now**: v2 rule grammar (EES-00010) is complete. The extractor is the last component still producing v1 output. Multi-turn tool-calling also positions us for future interactive extraction (chat panel).
- **Impact**: Higher-quality rules with fewer manual corrections. Structured tool schemas enforce v2 grammar at the API level, eliminating malformed output.
- **KPIs**:
  - Extraction success rate (no LLMError) ≥ 95% (up from ~80% with single-shot)
  - Zero v1-format rules produced
  - Average turns per extraction (target: 3–6)

## Stakeholders

| Role | Stakeholder | Interest |
|------|-------------|----------|
| Developer | Brent | Implementation, testing |
| User | TSGs / incident responders | Higher-quality rules |

## Functional Requirements

### FR-1: Tool Definitions (5 tools)

| Tool | Type | Purpose |
|------|------|---------|
| `get_ontology` | Read-only | Returns current ontology nouns + properties |
| `get_existing_rules` | Read-only | Returns confirmed rules (v2 format) |
| `submit_fact` | Write + validate | Submits a single fact for collection |
| `submit_rule` | Write + validate | Submits a rule with v2 grammar |
| `set_root_cause` | Write | Sets the proposed root cause name |

#### Tool Schemas

**`get_ontology`** — no parameters
```json
{
  "name": "get_ontology",
  "description": "Retrieve the current ontology (nouns and their properties). Call this first to understand available entities before extracting facts.",
  "parameters": { "type": "object", "properties": {}, "required": [] }
}
```

**`get_existing_rules`** — no parameters
```json
{
  "name": "get_existing_rules",
  "description": "Retrieve all confirmed troubleshooting rules in the knowledge base. Use to avoid duplicating existing rules.",
  "parameters": { "type": "object", "properties": {}, "required": [] }
}
```

**`submit_fact`** — validated
```json
{
  "name": "submit_fact",
  "description": "Submit a single extracted fact. Facts represent observed conditions in the incident. Use scope='rule' for generalizable facts, scope='context' for instance-specific documentation. Do NOT include variables ($) in facts.",
  "parameters": {
    "type": "object",
    "properties": {
      "noun": { "type": "string", "description": "Entity name (e.g., 'Error', 'VM')" },
      "instance": { "type": "string", "description": "Instance name or '*' for generalized", "default": "*" },
      "property": { "type": "string", "description": "Property name (e.g., 'ResultCode', 'SKU')" },
      "operator": { "type": "string", "enum": ["==", "!=", ">", "<", ">=", "<=", "contains", "!contains"] },
      "value": { "type": "string", "description": "The observed value" },
      "scope": { "type": "string", "enum": ["rule", "context"], "default": "rule" }
    },
    "required": ["noun", "property", "operator", "value"]
  }
}
```

**`submit_rule`** — validated, v2 grammar enforced
```json
{
  "name": "submit_rule",
  "description": "Submit a troubleshooting rule with v2 grammar. The THEN branch is required (CHANGE_STATE, RULED_OUT, or GAP). An optional ELSE branch fires when conditions are NOT met.",
  "parameters": {
    "type": "object",
    "properties": {
      "conditions": {
        "type": "object",
        "properties": {
          "logic": { "type": "string", "enum": ["AND", "OR"] },
          "items": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "noun": { "type": "string" },
                "instance": { "type": "string", "default": "*" },
                "property": { "type": "string" },
                "operator": { "type": "string", "enum": ["==", "!=", ">", "<", ">=", "<=", "contains", "!contains"] },
                "value": { "type": "string" }
              },
              "required": ["noun", "property", "operator", "value"]
            },
            "minItems": 1
          }
        },
        "required": ["logic", "items"]
      },
      "then": {
        "type": "object",
        "properties": {
          "kind": { "type": "string", "enum": ["CHANGE_STATE", "RULED_OUT", "GAP"] },
          "description": { "type": "string", "minLength": 1 }
        },
        "required": ["kind", "description"]
      },
      "else": {
        "type": "object",
        "properties": {
          "kind": { "type": "string", "enum": ["CHANGE_STATE", "RULED_OUT", "GAP"] },
          "description": { "type": "string", "minLength": 1 }
        },
        "required": ["kind", "description"]
      },
      "because": { "type": "string", "description": "Human-readable explanation of why this rule exists" }
    },
    "required": ["conditions", "then", "because"]
  }
}
```

**`set_root_cause`** — simple write
```json
{
  "name": "set_root_cause",
  "description": "Set the root cause identified in this incident. Call once when you have determined the root cause.",
  "parameters": {
    "type": "object",
    "properties": {
      "name": { "type": "string", "description": "Root cause name, or null if undetermined" }
    },
    "required": ["name"]
  }
}
```

### FR-2: Agentic Loop

```
1. Build messages = [system_prompt, user_message(incident_text)]
2. Loop (max MAX_TURNS):
   a. Call client.chat.completions.create(messages, tools, tool_choice="auto")
   b. If response has no tool_calls → break (model is done)
   c. For each tool_call:
      - Dispatch to handler function
      - Validate inputs; return error string if invalid
      - Append assistant message + tool result messages
   d. Increment turn counter
3. Collect submitted facts, rules, root_cause → return LLMResponse
```

### FR-3: Validation Rules

| Tool | Validation | Error returned |
|------|-----------|----------------|
| `submit_fact` | `operator` ∈ VALID_OPERATORS | "Invalid operator '{op}'. Valid: ..." |
| `submit_fact` | No variables (`$`) in instance or value | "Facts must not contain variables" |
| `submit_fact` | Ontology warning if noun/property unknown | accepted with warning |
| `submit_rule` | `then.kind` ∈ VALID_OUTPUT_KINDS | "Invalid kind '{k}'. Valid: ..." |
| `submit_rule` | `then.description` non-empty | "Description must not be empty" |
| `submit_rule` | `else.kind` ∈ VALID_OUTPUT_KINDS (if else present) | same |
| `submit_rule` | `conditions.items` non-empty | "Rule must have at least one condition" |
| `submit_rule` | each condition has valid operator | "Invalid operator in condition N" |
| `submit_rule` | `because` non-empty | "Rule must have a 'because' explanation" |

### FR-4: System Prompt (Simplified)

The new system prompt is much shorter — it describes the extraction *task*, not the output *schema* (the schema is now enforced by tool parameters):

```
You are an expert system fact extractor. Given an incident report, your job is to:

1. Call get_ontology() to see existing entity types and properties.
2. Call get_existing_rules() to see what rules already exist (avoid duplicates).
3. Read the incident report and extract facts using submit_fact().
4. Propose troubleshooting rules using submit_rule().
5. If a root cause is identified, call set_root_cause().

Guidelines:
- Facts use scope="rule" for generalizable patterns, scope="context" for instance-specific data.
- Do NOT extract GUIDs, timestamps, resource names, or subscription IDs as rule-scoped facts.
- Rules use variables ($op, $vm, etc.) in instance fields when conditions must match the same entity.
- Facts never use variables — only rules do.
- Every rule needs a "because" explanation.
- Use CHANGE_STATE for positive identification, RULED_OUT for elimination, GAP for missing information.
- Prefer reusing existing ontology nouns/properties (case-insensitive match).
```

### FR-5: Backward Compatibility

- `extract(incident_text, ontology)` signature unchanged
- Returns `LLMResponse(facts, rules, root_cause)` — same type
- Rules are constructed with v2 `RuleOutput` (not deprecated `RuleThen`)
- The `_parse_response()` method is removed (tools produce structured objects directly)

## Non-Functional Requirements

| NFR | Requirement | Implementation |
|-----|-------------|----------------|
| Max turns | 10 (configurable via `max_turns` param) | Loop guard with early exit |
| Token logging | Total prompt + completion tokens logged | `response.usage.total_tokens` summed across turns |
| Telemetry | Turns, tool calls, rejections counted | Logged at INFO level after extraction |
| No new deps | Use existing `openai>=1.0` | Tool calling is built-in since v1.0 |
| Latency | Acceptable increase from multi-turn | Expected 2–4x single-shot wall time |

## Proposed Approach (High Level)

### Phase 1: Refactor `fact_extractor.py`

1. **Replace `_SYSTEM_PROMPT`** with the simplified tool-oriented prompt (FR-4).
2. **Define tool schemas** as Python dicts in a `_TOOLS` list.
3. **Implement tool handlers** as private methods:
   - `_handle_get_ontology(ontology)` → JSON string of ontology
   - `_handle_get_existing_rules(rules)` → JSON string of rules
   - `_handle_submit_fact(args, collected_facts)` → validation + collect
   - `_handle_submit_rule(args, collected_rules)` → validation + collect
   - `_handle_set_root_cause(args)` → store root cause
4. **Rewrite `extract()`** with the agentic loop (FR-2).
5. **Remove `_parse_response()`** — no longer needed.
6. **Add `max_turns` parameter** to `extract()` with default 10.
7. **Log telemetry** (turns, tool calls, rejections, tokens) at method end.

### Phase 2: Update tests

- Replace mock-based tests that mock `chat.completions.create` with tests that simulate multi-turn tool calling responses.
- Test each tool handler in isolation (validation, acceptance, error messages).
- Test the agentic loop with mock responses containing tool_calls.
- Test max-turn cutoff behavior.
- Test backward compatibility — `extract()` still returns `LLMResponse`.

### Files Changed

| File | Change | Risk |
|------|--------|------|
| `src/ees/fact_extractor.py` | Major rewrite (prompt, loop, tools, handlers) | High — covered by new tests |
| `tests/test_fact_extractor.py` | Rewrite to match new architecture | Medium |
| No other files | Callers use `extract()` API unchanged | None |

## Alternatives Considered

| Alternative | Why rejected |
|-------------|-------------|
| Copilot SDK (`github-copilot-sdk`) | Adds async complexity, new dependency, no `response_format` fallback. Azure OpenAI SDK already has tool calling. Reserved for future chat panel. |
| Prompt-only update (EES-00011) | Superseded — updating the JSON schema prompt can't solve the fundamental single-shot fragility. |
| Streaming tool calls | Unnecessary complexity for batch extraction. No user-facing latency requirement. |
| `response_format=json_schema` structured output | OpenAI's structured output only constrains the final message. Tool calling gives per-submission validation + iteration. Could be used as fallback if tool calling fails. |

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Model doesn't call tools (returns plain text) | Low | Medium | Detect no tool_calls on first turn → fall back to single-shot with v2 prompt |
| Runaway loop (model keeps calling tools) | Medium | Low | MAX_TURNS guard (default 10), log warning on cutoff |
| Token cost increase from multi-turn | Medium | Low | Log total tokens, monitor. Expected 2–4x increase is acceptable. |
| Tool schema not supported by deployment | Low | High | gpt-5.2 deployment confirmed to support tools. Add runtime check. |
| Model submits many invalid tool calls | Low | Medium | Clear error messages enable self-correction. Counted in telemetry. |

## Dependencies

| Dependency | Status |
|-----------|--------|
| EES-00010 (v2 rule grammar) | ✅ Complete |
| `openai>=1.0` with tool calling | ✅ Already installed |
| Azure OpenAI gpt-5.2 deployment | ✅ Available |

## Migration / Rollout / Rollback Plan

- **Migration**: Drop-in replacement. Same `extract()` API, same `LLMResponse` return.
- **Rollout**: Merge to branch, test with live LLM call. No feature flag needed — extraction path is the same.
- **Rollback**: Revert the single commit. Old single-shot code is in git history.

## Observability Plan

- **Logging** (Python `logging` at INFO level):
  - Extraction started (incident length, ontology size)
  - Each turn: tool calls made, validations passed/failed
  - Extraction complete: total turns, total tool calls, rejections, total tokens
- **No external telemetry** — console/file logging only (matches existing pattern).

## Test Strategy Summary

1. **Unit tests for tool handlers**: Each handler tested with valid/invalid inputs.
2. **Integration test for agentic loop**: Mock `client.chat.completions.create` to return sequences of tool-call responses, verify collected facts/rules/root_cause.
3. **Edge cases**: max-turn cutoff, no tool calls (plain text response), model sends unknown tool name, empty incident text.
4. **Backward compat**: `extract()` returns `LLMResponse` with v2 `Rule` objects, not deprecated `RuleThen`.
