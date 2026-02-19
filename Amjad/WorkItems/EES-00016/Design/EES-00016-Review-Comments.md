# EES-00016 — Review Comments

## Design Doc Review

### Clarity & Completeness
- **PASS**: The design doc clearly defines the four types, their validation logic, and the API surface (`validate_value`, `validate_fact`)
- **PASS**: Backward compatibility approach is well defined (`.get()` defaults)
- **PASS**: Advisory vs. enforced validation boundary is clear

### Feasibility & Sequencing
- **PASS**: Single-step implementation touching only `models.py` and `ontology_manager.py`
- **PASS**: No external dependencies

### Edge Cases to Address
1. **Empty `values` list for enum type**: If `type="enum"` but `values=[]`, should `validate_value()` reject everything or accept everything? **Recommendation**: Reject everything — an enum with no legal values is an authoring error. Add a `validate_schema() -> list[str]` method to catch this at ontology load time.
2. **Whitespace in values**: Should `" true "` pass bool validation? **Recommendation**: No. Values should be stripped at deserialization, not at validation time.
3. **Empty string as value**: Should `""` be a legal value? **Recommendation**: For `string` type, yes. For `enum`, only if explicitly in `values`. For `bool`/`long`, no.
4. **Very large long values**: `"99999999999999999999"` is a valid int in Python but may cause issues downstream. **Recommendation**: Accept it — Python handles arbitrary precision ints. No need for range constraints now.

### Naming
- **PASS**: `validate_value` and `validate_fact` are clear method names
- **PASS**: `values` field name is unambiguous in context

### Risks Not Covered
- **LLM value normalization**: The LLM may produce `"True"` instead of `"true"` for bool properties. This is an extraction concern (out of scope for this item), but the design should note that bool validation is case-sensitive by design. **Noted, no change needed.**

## Verdict
**Approved** — proceed to test cases and implementation. Address edge case #1 (empty enum values) in the test cases.

---

## Architect Notes

### Capability Impact Analysis
Files: `models.py`, `ontology_manager.py`
- **Directly affected**: `data-models`, `ontology-management`
- **Transitively affected**: `yaml-persistence`, `fact-extraction`, `rule-generation`, `cli-orchestration`, `rule-evaluation`, `gui`

The transitive blast radius is wide (8 capabilities) because `models.py` is foundational. However, all changes are **additive** (new fields with defaults, new methods). No existing signatures change. Transitive consumers only break if they explicitly reference the new fields — and none will until EES-00017.

### Architectural Alignment
- **PASS**: Extends existing dataclass pattern — consistent with codebase style
- **PASS**: `validate_fact` returns error strings, not exceptions — matches the advisory pattern used elsewhere
- **PASS**: No new coupling introduced — `OntologyManager.validate_fact` only uses `OntologyProperty.validate_value`

### Contracts
- `validate_value(v: str) -> bool` — clear input/output contract
- `validate_fact(fact: Fact) -> list[str]` — clear: empty = valid, non-empty = errors with human-readable messages
- Serialization contract preserved: `to_dict()` / `from_dict()` round-trip

### Security / Privacy
- N/A — no user input, no network, no file system changes beyond ontology YAML

### Rollback Safety
- **Safe**: Fields have defaults. Old code that reads YAML with new fields ignores them via `.get()`. New code reading old YAML gets defaults.

### Recommendation
**Approved without changes.** Proceed to developer role.
