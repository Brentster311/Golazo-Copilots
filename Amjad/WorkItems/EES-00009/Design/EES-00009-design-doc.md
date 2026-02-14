# EES-00009 Design Doc — Variable Binding in Rule Engine

## Summary
Add variable binding to the EES rule engine so that rule conditions can use `$varname` placeholders that unify across conditions. This enables rules like "for ANY operation where error code is X, the root cause is Y" — replacing the current flat, bag-of-facts matching.

## Problem Statement
The current evaluator uses `match_key()` for O(1) exact matching. The `*` instance is treated as a literal string — a condition with `instance="*"` only matches facts that also have `instance="*"`. This works for single-operation incidents but fails to express:

1. **Cross-condition consistency**: "The error on the SAME operation as the VM size" — two conditions can't say they refer to the same entity.
2. **Generalization**: Rules fire only because all extracted facts happen to use `*` as the instance. If the LLM extracted concrete instances (e.g., `op-1`), matching would break.
3. **Multi-operation incidents**: If an incident has both a failed PUT and a successful GET, flat AND can't distinguish which error goes with which operation.

## Business Case
- **Why now**: The system extracts facts from real Kusto incidents. Rules are being generated and saved. Without variable binding, rules will accumulate that are technically correct but semantically fragile — they'd break on the first multi-operation incident.
- **Impact**: Enables the rule engine to scale beyond simple single-operation incidents.
- **KPIs**: All existing tests pass + new variable-binding tests pass. No user-facing change in this slice.

## Stakeholders
- Support engineers (end users — no change in this slice)
- Developer (engine internals)

## Functional Requirements
1. Variables are strings beginning with `$` (e.g. `$op`, `$vmsize`)
2. Variables can appear in `Fact.instance` and `Fact.value` fields
3. During rule evaluation, variables bind to concrete values from input facts
4. Shared variables across conditions enforce consistency (same `$var` = same bound value)
5. Bound variables are substituted into `RuleThen` to produce concrete derived facts
6. `*` continues to work as a literal match (no change)
7. Non-variable rules take the same O(1) hash-lookup path (no regression)

## Non-Functional Requirements
- Backward compatibility: all 238 existing tests pass unchanged
- Variable-binding evaluation may use O(n) scanning per condition (acceptable for MVP)
- No YAML schema changes required (variables are just strings that start with `$`)

## Proposed Approach

### Phase 1: Model helpers
Add to `Fact`:
- `is_variable(field_value: str) -> bool` — static method, returns `field_value.startswith("$")`
- `has_variable_instance` / `has_variable_value` — property shortcuts
- `has_variables` — True if any field is a variable

### Phase 2: Unification engine
New module or method in `RuleEvaluator`:
- `_unify_condition(condition: Fact, input_facts: list[Fact], bindings: dict) -> list[dict]`
  - For each input fact, check if `condition` can match it given current `bindings`
  - Non-variable fields: exact match (case-insensitive for noun/property, exact for the rest)
  - Variable fields: if unbound, bind to the concrete value; if bound, check consistency
  - Returns a list of possible extended bindings (may be multiple for a single condition)
- `_conditions_met_with_bindings(conditions: RuleConditions, input_facts: list[Fact]) -> (bool, dict)`
  - For AND: find a single consistent binding across ALL conditions
  - For OR: any condition matches with any binding
  - Returns the final bindings if successful

### Phase 3: Evaluator integration
Update `_conditions_met()`:
- Fast path: if no conditions have variables, use existing `match_key()` hash lookup (unchanged)
- Slow path: if any condition has variables, use `_conditions_met_with_bindings()`

Update derived fact production:
- After a rule fires, substitute bound variables into `rule.then` before creating the derived fact

### Phase 4: Serialization
No change needed — variables are just strings. `Fact(instance="$op")` serializes to `{"instance": "$op"}` and deserializes back. `to_dict()`, `from_dict()` work unchanged.

## Alternatives Considered
1. **Option A (dot-path properties)** — simpler but doesn't solve cross-condition consistency
2. **Option B (dimensional qualifiers)** — adds a `dimensions` dict to Fact; more schema disruption for less expressiveness
3. **Option D (hierarchical noun path)** — parsing complexity, hard for LLM to produce consistently

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Variable binding performance on large fact sets | Slow evaluation | Fast-path for non-variable rules; variable path is O(n×m) but n,m are small (<100 facts, <20 conditions per rule) |
| LLM produces inconsistent variable names | Rules don't unify correctly | Deferred to Slice 2 (prompt engineering) |
| Backtracking complexity for AND with multiple variables | Combinatorial explosion | Limit to simple sequential binding (first match wins); no full Prolog-style backtracking in MVP |

## Open Questions
1. Should variable binding support the `contains` and `!contains` operators? **Recommendation**: Yes — match the value literally, bind the variable on the other field. No regex variables.
2. Should `$var` in `value` match case-insensitively? **Recommendation**: No — bind the exact value. Case normalization is the LLM's job.

## Dependencies
- None — purely additive engine change

## Migration / Rollout / Rollback
- **Migration**: None — existing YAML data has no `$` variables, so the new code path is never triggered
- **Rollout**: Ship with Slice 1 only. No user-facing change until Slice 2 (LLM prompt) and Slice 3 (GUI) are completed.
- **Rollback**: Remove variable-binding code; revert to `match_key()` only

## Observability Plan
- Unit test coverage for all variable-binding scenarios
- No runtime telemetry needed in this slice

## Test Strategy Summary
- Unit tests for `is_variable()`, `has_variable_instance`, etc.
- Unit tests for `_unify_condition()` with bound/unbound variables
- Unit tests for `_conditions_met_with_bindings()` with AND/OR logic
- Integration test: full `evaluate()` with variable-bound rules producing derived facts
- Backward compatibility: all 238 existing tests pass unchanged
