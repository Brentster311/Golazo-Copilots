# EES-00009 Capability Impact Analysis

## Directly Affected (3 capabilities)

### data-models
- **Change**: Add `is_variable()` static method, `has_variable_instance`/`has_variable_value` properties to `Fact`
- **Contract impact**: Additive only — no existing fields change. `match_key()` unchanged. `to_dict()`/`from_dict()` unchanged (variables are just strings).
- **Risk**: None — purely additive

### rule-evaluation
- **Change**: `_conditions_met()` gains a variable-aware slow path. Derived fact production substitutes bound variables into `RuleThen`.
- **Contract impact**: `evaluate()` return type (`EvaluationResult`) unchanged. New behavior only triggered when conditions contain `$`-prefixed values.
- **Risk**: Low — fast path preserved for all existing rules

### rule-generation
- **Change**: `filter_rules()` needs variable-aware condition matching (a rule with `Error($op).ResultCode == X` should be kept if any confirmed fact has a matching Error noun+property+value regardless of instance).
- **Contract impact**: `filter_rules()` signature unchanged. Return behavior unchanged for non-variable rules.
- **Risk**: Low — existing exact-match path preserved

## Transitively Affected (5 capabilities) — No Changes Required in Slice 1

| Capability | Impact | Action |
|-----------|--------|--------|
| yaml-persistence | Variables serialize as plain strings — no schema change | None |
| fact-extraction | LLM prompt unchanged in Slice 1 (deferred to Slice 2) | None |
| ontology-management | Unaffected — ontology doesn't reference variables | None |
| cli-orchestration | Calls `filter_rules()` and `evaluate()` — unchanged signatures | None |
| gui | Displays facts/rules — `$var` strings render as-is | None |

## Contract Compatibility Verification
- All public method signatures remain identical
- All return types remain identical
- YAML schema unchanged (variables are strings)
- All 238 existing tests must pass without modification
