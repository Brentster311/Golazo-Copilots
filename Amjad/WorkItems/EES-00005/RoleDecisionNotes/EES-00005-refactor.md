# Refactor Decision Notes — EES-00005

## Changes Made

| Refactoring | File | Rationale |
|-------------|------|-----------|
| Removed unused imports `sys`, `RuleConditions`, `RuleThen` | `app.py` | Dead code removal |
| Extracted `_ensure_data_dirs()` | `app.py` | Deduplicated directory creation from `__init__` and `_set_data_dir` |
| Extracted `_format_eval_display()` module-level function | `app.py` | Separates display formatting from UI widget manipulation; testable without Tk |
| List comprehension in `facts_to_rows()` | `adapters.py` | Idiomatic Python; removes mutable-accumulator pattern |

## Verification

- 207 tests pass before and after refactoring
- No behavior changes — all refactors are structural only
