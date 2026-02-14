# Developer Decision Notes — EES-00009

## Summary

Implemented Prolog-style variable binding (Slice 1: engine-only) following TDD red-green cycle.

## Files Changed

| File | Change |
|------|--------|
| `src/ees/models.py` | Added `is_variable()` static method, `has_variable_instance`, `has_variable_value`, `has_variables` properties on `Fact` |
| `src/ees/rule_evaluator.py` | Added fast/slow path guard in forward-chaining loop; new `_unify_condition()`, `_conditions_met_with_bindings()`, `_substitute_then()` methods |
| `src/ees/rule_generator.py` | `filter_rules()` now uses unification for variable-bearing conditions instead of exact `match_key()` lookup |
| `tests/test_models.py` | Added `TestVariableDetection` class (9 tests: TC-1, TC-2) |
| `tests/test_rule_evaluator.py` | Added `TestVariableBinding` class (13 tests: TC-3 through TC-14) |
| `tests/test_rule_generator.py` | Added `TestFilterRulesVariableBinding` class (2 tests: TC-15) |

## TDD Cycle

- **Red phase**: 24 tests written; 21 failed, 3 passed (negative cases that already work without changes).
- **Green phase**: All 262 tests pass (238 existing + 24 new). 0 failures.

## Design Decisions

1. **`is_variable()` requires `len >= 2`**: Bare `$` is not a valid variable. This prevents accidental matching on typos.

2. **Fast/slow path guard**: The `has_variables` check in the forward-chaining loop avoids calling the Cartesian-product unification for rules that don't need it. All existing rules take the fast hash-lookup path — zero performance regression.

3. **`itertools.product` for backtracking**: Each condition gathers all matching fact bindings, then we try all combinations. For Slice 1 this is correct and simple. If rules with many conditions and many facts cause perf issues, we can add constraint propagation in a future slice.

4. **Whole-field substitution only**: `_substitute_then()` only replaces a then field if the _entire_ field is a variable (e.g. `$vmsize`). Embedded variables like `"Capacity for $vmsize"` are left as-is. This is intentional — partial string templating is deferred.

5. **`rule_generator.py` imports `RuleEvaluator`**: Rather than duplicating unification logic, `filter_rules()` calls `RuleEvaluator._conditions_met_with_bindings()` as a classmethod. This keeps the binding algorithm in one place.

## Files NOT Changed (by design)

- `gap_detector.py` — deferred to Slice 2 (per architect decision)
- `fact_extractor.py` — LLM prompt changes deferred to Slice 2
- `app.py` — GUI changes deferred to Slice 3
