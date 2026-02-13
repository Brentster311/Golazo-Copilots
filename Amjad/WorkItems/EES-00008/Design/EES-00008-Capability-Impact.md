# EES-00008 — Capability Impact Analysis

## Impact Summary
5 files changed → 8 capabilities affected (4 direct, 4 transitive)

## Directly Affected Capabilities

### data-models
- **Change**: Add `scope` field to `Fact` dataclass
- **Contract impact**: `to_dict()` gains new key, `from_dict()` reads with default
- **Risk**: Low — additive, backward compatible

### fact-extraction
- **Change**: Update `_SYSTEM_PROMPT` and `_parse_response` to handle scope
- **Contract impact**: LLM JSON schema gains optional `scope` field
- **Risk**: Low — optional field with fallback

### rule-generation
- **Change**: None in module itself; callers filter by scope before calling
- **Contract impact**: None
- **Risk**: None

### gui
- **Change**: Scope column in facts table, toggle buttons, scope filter in _save_all
- **Contract impact**: UI-only
- **Risk**: Low

## Transitively Affected Capabilities

### yaml-persistence
- **Change needed**: None — serializes whatever `to_dict()` returns
- **Risk**: None

### rule-evaluation
- **Change needed**: None — evaluates stored rules, not raw facts
- **Risk**: None

### cli-orchestration
- **Change needed**: Yes — add scope filter before `filter_rules()` call in main.py
- **Risk**: Low — one-line filter

### ontology-management
- **Change needed**: None — updates ontology from all confirmed facts regardless of scope
- **Risk**: None
