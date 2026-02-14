# EES-00009: Variable Binding in Rule Engine (Slice 1 of 3)

**Status**: BACKLOG

## User Story
- **Title**: Variable binding for rule conditions and conclusions
- **As a**: Support engineer building expert system rules
- **I want**: Rule conditions to use variables (e.g. `$op`, `$vmsize`) that bind across conditions so that a single rule can express "for ANY operation where the error code is X AND the VM size is Y, the root cause is Z"
- **So that**: Rules are truly generalizable across incidents with different operations, zones, and VM sizes — not tied to a flat bag of independent facts that happen to fire together

- **Out of scope**:
  - LLM prompt changes to produce variable-bound output (Slice 2 — separate work item)
  - GUI display/editing of variable bindings (Slice 3 — separate work item)
  - Nested variable expressions or arithmetic on variables
  - Variable binding in the `operator` field (only `instance` and `value` support variables)

- **Assumptions**:
  - **Assumption (explicit)**: Variables are strings prefixed with `$` (e.g. `$op`, `$vmsize`). A field value is a variable if it starts with `$`.
  - **Assumption (explicit)**: Variables bind within a single rule evaluation — they are NOT global across rules. Each rule evaluation starts with an empty binding context.
  - **Assumption (explicit)**: `"*"` continues to work as before (literal match). Variables are a new, separate mechanism. `*` means "I don't care about instance, match literally." `$op` means "bind this to whatever instance matches, and enforce consistency across conditions."
  - **Assumption (explicit)**: Backward compatibility — all existing tests (238) must continue to pass. Existing rules with `instance="*"` are unaffected.
  - **Assumption (explicit)**: The `property` field remains a simple string (no dot-paths in this slice). Dot-path properties may come in a future work item.
  - **Assumption (explicit)**: Interface type (GUI, CLI), platform (Windows), persistence (YAML), user type (technical) are all established from prior work items.

- **Acceptance Criteria (bulleted, testable)**:
  - [ ] A `Fact` with `instance="$op"` is recognized as having a variable instance (helper method `has_variable_instance()` or similar)
  - [ ] A `Fact` with `value="$vmsize"` is recognized as having a variable value (helper method `has_variable_value()` or similar)
  - [ ] `RuleEvaluator._conditions_met()` performs unification: a condition `Fact(noun="Error", instance="$op", property="ResultCode", operator="==", value="ZonalAllocationFailed")` matches input fact `Fact(noun="Error", instance="op-1", property="ResultCode", operator="==", value="ZonalAllocationFailed")` and binds `$op → "op-1"`
  - [ ] Shared variables enforce consistency: if two conditions both use `instance="$op"`, they must bind to the same concrete instance value for the rule to fire
  - [ ] `RuleThen` substitutes bound variables: if `then.instance="$op"` and `$op` was bound to `"op-1"`, the derived fact has `instance="op-1"`
  - [ ] Existing rules with `instance="*"` and no variables continue to work identically (all 238 tests pass)
  - [ ] Variable binding works with both AND and OR logic

- **Non-functional requirements**:
  - Evaluator performance must not regress for non-variable rules (O(1) hash lookup path preserved)
  - Variable binding path may use O(n) scanning since it requires pattern matching

- **Telemetry / metrics expected**: None (engine-internal change)

- **Rollout / rollback notes**: Pure additive — no existing behavior changes. If variables aren't used, the engine behaves identically to before.

## Decomposition Rationale
The full "Option C — Prolog-style variable binding" feature spans three user-observable slices:
1. **EES-00009 (this story)**: Engine-level variable binding in models + evaluator. Testable via unit tests. No UI change.
2. **Future story**: LLM prompt changes so the extractor produces variable-bound facts/rules from incident text.
3. **Future story**: GUI display of variable bindings, letting users see and edit `$var` in the Proposed Facts/Rules tables.

Each slice is independently shippable and testable.

## Concrete Example

### Current (flat, no variables):
```
IF Error(*).ResultCode == ZonalAllocationFailed
AND Error(*).Message contains "insufficient capacity"
THEN RootCause(*).Name = "Zonal capacity exhaustion"
```
Problem: Both conditions use `*` — no way to know they refer to the same error.

### With variables (this story):
```
IF Error($op).ResultCode == ZonalAllocationFailed
AND Error($op).Message contains "insufficient capacity"
AND VMSeries($op).Name == $vmsize
THEN RootCause($op).Name = "Zonal capacity exhaustion"
```
`$op` binds to the same concrete instance across conditions. `$vmsize` binds to whatever VM size was in the incident (though not interpolated into the conclusion value in this slice).
