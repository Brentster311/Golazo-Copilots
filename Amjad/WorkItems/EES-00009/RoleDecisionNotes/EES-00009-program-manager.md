# EES-00009 Program Manager Notes

## Key Design Decisions
1. **Fast path / slow path split**: Non-variable rules keep the existing O(1) `match_key()` path. Variable rules use a new unification path. This preserves backward compatibility and performance.
2. **Sequential binding (no backtracking)**: For AND logic, we bind variables sequentially across conditions. If the first condition binds `$op → "op-1"`, subsequent conditions must match that binding. We do NOT implement full Prolog-style backtracking — it's unnecessary for the expected rule complexity.
3. **No schema changes**: `$varname` strings serialize naturally in YAML. No migration needed.
4. **Slice boundary is clean**: This slice has zero user-facing change. It's purely engine internals tested via unit tests.

## Risk Assessment
Low risk — purely additive. The fast-path guard ensures existing behavior is untouched.
