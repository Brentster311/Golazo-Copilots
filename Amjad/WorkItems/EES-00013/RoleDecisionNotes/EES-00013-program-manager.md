# EES-00013 PM Decision Notes

## Key Decisions

### 1. Keep Azure OpenAI SDK (not Copilot SDK)
- **Decision**: Use existing `openai>=1.0` tool calling, not `github-copilot-sdk`
- **Rationale**: No new dependencies, no async complexity, tool calling already supported. Copilot SDK reserved for future interactive chat panel.

### 2. Five tools (not fewer, not more)
- **Decision**: `get_ontology`, `get_existing_rules`, `submit_fact`, `submit_rule`, `set_root_cause`
- **Rationale**: Read-only tools let the model inspect context before writing. Separate submit tools give per-item validation. `set_root_cause` is separate because it's a different concept than rules/facts.
- **Considered**: Single `submit_extraction` tool — rejected because it's just single-shot with extra steps.

### 3. Validation returns errors (not exceptions)
- **Decision**: Invalid tool calls return an error string in the tool result, allowing the model to self-correct.
- **Rationale**: Throwing an exception would abort the loop. Returning errors lets the model retry with corrected inputs.

### 4. Max 10 turns default
- **Decision**: Hard cap at 10 turns, configurable via `max_turns` parameter.
- **Rationale**: Prevents runaway token consumption. Typical extraction should complete in 3–6 turns.

### 5. No fallback to single-shot
- **Decision**: If the model doesn't call tools, log a warning and return empty `LLMResponse` (or whatever was collected).
- **Rationale**: Adding a fallback path doubles the code to maintain. If the model doesn't use tools, we should investigate why, not silently degrade.
- **Reconsidered**: Added a note in design doc that fallback could be added if needed, but not in initial implementation.

### 6. Only `fact_extractor.py` and its tests change
- **Decision**: No changes to models, rule_evaluator, gap_detector, GUI, or CLI.
- **Rationale**: `extract()` returns the same `LLMResponse` type. Backward compat layer from EES-00010 handles everything downstream.

### 7. Tool schemas enforce v2 grammar at API level
- **Decision**: `submit_rule` schema uses `enum: ["CHANGE_STATE", "RULED_OUT", "GAP"]` for kind.
- **Rationale**: Eliminates malformed output — the model literally cannot send an invalid kind through the tool interface.

## Open Questions (None Blocking)

- Should `get_existing_rules` accept a filter (e.g., by noun)? **Decision**: No, return all. Rules lists are small. Can revisit if needed.
- Should `submit_fact` warn vs reject on unknown ontology nouns? **Decision**: Accept with warning. New nouns are expected during extraction.

## Risk Acknowledgments

- Multi-turn increases latency ~2–4x. Acceptable for batch extraction.
- Multi-turn increases token cost ~2–4x. Logged for monitoring.
