# EES-00009 Review Comments

## Design Review

### Strengths
- Clean fast-path / slow-path split preserves backward compatibility
- No YAML schema changes — variables are just strings
- Well-scoped slice boundary (engine-only, no GUI/LLM)

### Issues

#### Issue 1: AND binding needs backtracking, not "first match wins"
The design says "sequential binding (first match wins)" for AND logic. This is insufficient. Consider:

```
Conditions (AND):
  Error($op).ResultCode == ZonalAllocationFailed
  VMSeries($op).Name == NvadsA10v5
```

Input facts:
```
Error(op-1).ResultCode == "OK"
Error(op-2).ResultCode == "ZonalAllocationFailed"
VMSeries(op-1).Name == "NvadsA10v5"
VMSeries(op-2).Name == "NvadsA10v5"
```

With "first match wins" on the first condition, `$op` might bind to `op-1` (wrong — ResultCode doesn't match). The correct implementation must try all candidate bindings for condition 1 and check if any produce a consistent binding across condition 2.

**Recommendation**: Use iterative narrowing — for each condition, produce all valid bindings, then intersect. This is NOT full Prolog backtracking; it's a simple filter-and-narrow approach with bounded complexity.

#### Issue 2: `match_key()` behavior with variables
The design doesn't specify whether `match_key()` changes. Since `match_key()` is used in `filter_rules()` (rule_generator.py) to check if condition facts exist in confirmed facts, it must either:
- Remain unchanged (variables in conditions won't match via `match_key()`)
- Or `filter_rules()` needs a variable-aware path

**Recommendation**: `match_key()` stays unchanged. `filter_rules()` gets a variable-aware path similar to the evaluator. Note: this is already in-scope since `rule_generator.py` is an affected file.

#### Issue 3: `contains` operator with variable binding
The design's open question #1 asks if `contains` should work with variables. The answer should be yes — `Error($op).Message contains "insufficient"` should bind `$op` to the instance of any Error whose Message contains "insufficient". The `contains` check is on the VALUE, while the variable is on the INSTANCE — they're independent fields.

**Verdict**: Approve with the backtracking fix (Issue 1) and `filter_rules` variable awareness (Issue 2).

---

## Architect Notes

### Architectural Alignment
- **Boundary**: Change is contained within `models.py`, `rule_evaluator.py`, and `rule_generator.py`. No new modules needed — the unification logic fits naturally as private methods on `RuleEvaluator`.
- **Fast/slow path split**: Architecturally sound. The `has_variables` check on conditions is O(n) on condition count (tiny), and gates the expensive path. Non-variable rules never enter the new code.

### Data Contracts
- No contract changes. `Fact.match_key()` unchanged. `evaluate()` returns `EvaluationResult` unchanged. `filter_rules()` signature unchanged.
- Variables are strings — no new types, no schema migration.

### TechBestPractices Compliance
- No new dependencies
- No `DefaultAzureCredential` involvement
- No new file I/O patterns
- Test-first (TDD) approach maintained

### Risk: Gap Detector
- As analyzed in discussion: `GapDetector` uses `match_key()` for overlap detection. Variable-bearing rules would cause false orphan detection. This is **acceptable in Slice 1** because the LLM prompt doesn't produce variables yet. **Must be addressed in Slice 2.**
- Recommendation: Add a comment/TODO in `gap_detector.py` noting this dependency.

### Risk: Combinatorial binding
- The filter-and-narrow approach for AND logic is bounded by `|conditions| × |input_facts|` per rule. With <20 conditions and <100 facts, this is at most 2000 iterations per rule — negligible.
- No full Prolog-style search tree. The binding is deterministic once we enumerate candidates per condition.

### Approval
Design approved. No architectural concerns.
