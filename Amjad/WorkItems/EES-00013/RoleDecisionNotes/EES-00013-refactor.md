# EES-00013 Refactor Notes

## Refactoring Applied

### 1. Extract `_validate_output_branch()` helper
- **What**: Extracted duplicated THEN/ELSE branch validation from `_handle_submit_rule()` into a module-level `_validate_output_branch(data, label)` function.
- **Why**: The THEN and ELSE validation blocks had identical logic (check kind ∈ VALID_OUTPUT_KINDS, check description non-empty, construct RuleOutput). Duplicated code = duplicated maintenance.
- **Before**: ~20 lines duplicated in `_handle_submit_rule()`
- **After**: Single 15-line function called twice with different labels ("THEN"/"ELSE")
- **Behavior change**: None. All 253 tests pass.

## Items Reviewed But Not Changed

- **Tool definitions (`_TOOLS`)**: Verbose but necessarily so — JSON Schema doesn't compress well. No refactoring opportunity.
- **`_dispatch_tool()` if/elif chain**: Could use a dict dispatch pattern, but with only 5 tools the if/elif is more readable and allows different return-type handling (read-only tools return `(str, True)` vs write tools return `tuple[str, bool]`).
- **`extract()` loop**: Clean and readable. The `for/else` pattern is idiomatic Python. No change needed.
- **Test file**: New code, well-organized by test case groups. No refactoring needed.
