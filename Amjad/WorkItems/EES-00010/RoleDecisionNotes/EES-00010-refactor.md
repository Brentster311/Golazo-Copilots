# EES-00010 — Refactor Decision Notes

## Refactoring Applied
- Moved `RuleOutput` import from inline (inside function body) to module-level in `gui/adapters.py`

## Refactoring Considered but Deferred
- The deprecated `RuleThen` class and v1 backward-compat fields on `Rule` are intentionally messy — cleaning them requires EES-00011/12 to eliminate consumers first
- The `rule_evaluator.py` `_conditions_met_with_bindings` could be simplified but is already well-structured from EES-00009

## Result
- 234 tests passing, no behavior changes
