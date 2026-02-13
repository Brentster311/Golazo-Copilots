# EES-00004 — Refactor Decision Notes

## Refactoring Applied

### RF-1: Extract `_parse_input_facts()` helper
- **Location:** `main.py`
- **Change:** Extracted semicolon-delimited fact parsing from `evaluate_facts()` into `_parse_input_facts(facts_str)` helper
- **Rationale:** Reduces cognitive load in `evaluate_facts()`, makes fact parsing independently testable, follows the existing pattern of `_format_rule_conditions()` / `_format_rule_then()` helpers
- **Behavior change:** None

### RF-2: Scoped YAML import
- **Location:** `main.py` — `evaluate_facts()` function
- **Change:** Moved `from ruamel.yaml import YAML` to local scope only where needed (--facts-file branch and --output branch) instead of top of function
- **Rationale:** Lazy import — only loaded when the feature is actually used. Avoids unnecessary import when using `--facts` string input without `--output`
- **Behavior change:** None

## Code Not Refactored (Intentional)
- `rule_evaluator.py` — Already clean. `evaluate()` method is long (~65 lines) but the forward chaining logic flows naturally as a single unit. Extracting sub-methods would fragment the algorithm without improving readability.
- `models.py` — `EvaluationResult.to_dict()` is straightforward, no optimization needed.

## Tests
- 189 tests pass before and after refactoring
- No behavior changes
