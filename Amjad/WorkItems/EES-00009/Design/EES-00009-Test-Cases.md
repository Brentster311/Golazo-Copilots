# EES-00009 Test Cases

## TC-1: `is_variable` recognizes `$`-prefixed strings
- **Input**: `Fact.is_variable("$op")` → `True`; `Fact.is_variable("*")` → `False`; `Fact.is_variable("op-1")` → `False`; `Fact.is_variable("")` → `False`; `Fact.is_variable("$")` → `False` (bare `$` is not a valid variable)
- **Maps to**: AC-1, AC-2

## TC-2: `has_variable_instance` and `has_variable_value` properties
- **Input**: `Fact(instance="$op", value="X")` → `has_variable_instance=True`, `has_variable_value=False`
- **Input**: `Fact(instance="*", value="$vmsize")` → `has_variable_instance=False`, `has_variable_value=True`
- **Maps to**: AC-1, AC-2

## TC-3: Simple variable binding — single condition, instance variable
- **Condition**: `Error($op).ResultCode == ZonalAllocationFailed`
- **Input facts**: `Error(op-1).ResultCode == ZonalAllocationFailed`
- **Expected**: Rule fires, `$op` binds to `"op-1"`
- **Maps to**: AC-3

## TC-4: Simple variable binding — single condition, value variable
- **Condition**: `VMSeries(*).Name == $vmsize`
- **Input facts**: `VMSeries(*).Name == NvadsA10v5`
- **Expected**: Rule fires, `$vmsize` binds to `"NvadsA10v5"`
- **Maps to**: AC-3

## TC-5: Shared variable — AND, consistent binding
- **Conditions (AND)**: `Error($op).ResultCode == ZonalAllocationFailed`, `VMSeries($op).Name == NvadsA10v5`
- **Input facts**: `Error(op-1).ResultCode == ZonalAllocationFailed`, `VMSeries(op-1).Name == NvadsA10v5`
- **Expected**: Rule fires with `$op → "op-1"`
- **Maps to**: AC-4

## TC-6: Shared variable — AND, inconsistent binding (should NOT fire)
- **Conditions (AND)**: `Error($op).ResultCode == ZonalAllocationFailed`, `VMSeries($op).Name == NvadsA10v5`
- **Input facts**: `Error(op-1).ResultCode == ZonalAllocationFailed`, `VMSeries(op-2).Name == NvadsA10v5`
- **Expected**: Rule does NOT fire (no consistent binding for `$op`)
- **Maps to**: AC-4

## TC-7: Shared variable — AND, multiple candidates, correct one found
- **Conditions (AND)**: `Error($op).ResultCode == ZonalAllocationFailed`, `VMSeries($op).Name == NvadsA10v5`
- **Input facts**: `Error(op-1).ResultCode == OK`, `Error(op-2).ResultCode == ZonalAllocationFailed`, `VMSeries(op-2).Name == NvadsA10v5`
- **Expected**: Rule fires with `$op → "op-2"` (backtracking needed — first candidate `op-1` fails)
- **Maps to**: AC-4

## TC-8: Variable substitution in RuleThen
- **Rule**: conditions bind `$op → "op-1"`, `then.instance = "$op"`
- **Expected**: derived fact has `instance = "op-1"`
- **Maps to**: AC-5

## TC-9: Variable substitution in RuleThen value
- **Rule**: conditions bind `$vmsize → "NvadsA10v5"`, `then.value = "Capacity exhaustion for $vmsize"`
- **Expected**: Derived fact value is `"Capacity exhaustion for $vmsize"` (exact string — NO interpolation in this slice; `$vmsize` in value of `then` is treated as a variable only if the ENTIRE value is `$vmsize`, not embedded)
- **Clarification**: If `then.value == "$vmsize"`, substitute to `"NvadsA10v5"`. If `then.value == "text $vmsize text"`, leave as-is (embedded variables are out of scope).
- **Maps to**: AC-5

## TC-10: Backward compatibility — no-variable rules unchanged
- **Conditions**: `Error(*).ResultCode == ZonalAllocationFailed` (no variables)
- **Input facts**: `Error(*).ResultCode == ZonalAllocationFailed`
- **Expected**: Rule fires via existing `match_key()` fast path
- **Maps to**: AC-6

## TC-11: OR logic with variables
- **Conditions (OR)**: `Error($op).ResultCode == ZonalAllocationFailed`, `Error($op).ResultCode == AllocationFailed`
- **Input facts**: `Error(op-1).ResultCode == AllocationFailed`
- **Expected**: Rule fires with `$op → "op-1"`
- **Maps to**: AC-7

## TC-12: Multiple different variables in same rule
- **Conditions (AND)**: `Error($op).ResultCode == ZonalAllocationFailed`, `VMSeries($op).Name == $vmsize`
- **Input facts**: `Error(op-1).ResultCode == ZonalAllocationFailed`, `VMSeries(op-1).Name == NvadsA10v5`
- **Expected**: Rule fires with `$op → "op-1"`, `$vmsize → "NvadsA10v5"`
- **Maps to**: AC-3, AC-4

## TC-13: Variable in condition with `contains` operator
- **Condition**: `Error($op).Message contains "insufficient capacity"`
- **Input facts**: `Error(op-1).Message contains "No compute stamps available"`, `Error(op-2).Message contains "insufficient capacity"`
- **Expected**: `$op` binds to `"op-2"`
- **Maps to**: AC-3

## TC-14: Full evaluate() integration — variable rule produces derived fact
- **Setup**: Input facts + a variable-bound rule. Run `evaluate()`.
- **Expected**: Derived fact appears in result with bound instance. Root cause identified.
- **Maps to**: AC-3, AC-4, AC-5

## TC-15: filter_rules with variable conditions
- **Setup**: A rule with variable conditions, confirmed facts that match
- **Expected**: `filter_rules()` keeps the rule (variable-aware matching)
- **Maps to**: AC-3, AC-6
