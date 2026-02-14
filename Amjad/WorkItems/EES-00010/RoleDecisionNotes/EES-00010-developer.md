# EES-00010 — Developer Decision Notes

## Implementation Summary

Implemented v2 rule grammar across the expert system core:
- `IF <conditions> THEN CHANGE_STATE|RULED_OUT|GAP [ELSE CHANGE_STATE|RULED_OUT|GAP]`

## Key Decisions

### 1. RuleOutput replaces RuleThen
- New `RuleOutput(kind, description)` dataclass — `kind` is `CHANGE_STATE`, `RULED_OUT`, or `GAP`
- `to_fact()` maps output to `Fact(noun=kind, instance="*", property="description", operator="==", value=description)` for working-set matching

### 2. Backward Compatibility
- `RuleThen` kept as deprecated plain class for import compat (fact_extractor.py, gap_detector.py)
- `Rule` retains deprecated v1 fields: `type`, `requires`, `produces`, `note` (default values only)
- `Rule.from_dict()` handles both v1 `{"noun":...}` and v2 `{"kind":...}` then formats
- `EvaluationResult` has backward-compat properties: `.root_causes`, `.ruled_out`, `.gap_rules`
- `EvaluationResult.to_dict()` includes `"root_causes"` and `"ruled_out"` keys for CLI compat
- `main.py._format_rule_then()` handles both `RuleOutput` and legacy `RuleThen`
- `gui/adapters.py.eval_result_to_display()` handles both types

### 3. ELSE Branch in Evaluator
- When conditions NOT met AND `else_` is present → fire ELSE branch
- When conditions NOT met AND no `else_` → skip rule entirely (no output)
- Each rule fires at most once (THEN or ELSE, never both)

### 4. GAP Terminal Behavior
- GAP outputs are recorded in `outputs` list but NOT converted to `Fact` / added to working set
- Prevents nonsensical chaining where downstream rules match on GAP facts

### 5. `_substitute_then()` Removed
- v2 `RuleOutput.description` is free text, not parameterized — no variable substitution needed
- Variable binding still works for condition matching; it just doesn't affect the output

## Files Modified
- `src/ees/models.py` — RuleOutput, Rule refactored, EvaluationResult refactored
- `src/ees/rule_evaluator.py` — ELSE evaluation, output-to-fact mapping, removed _substitute_then
- `src/ees/main.py` — _format_rule_then handles RuleOutput, added RuleOutput import
- `src/ees/gui/adapters.py` — eval_result_to_display handles RuleOutput

## Files NOT Modified (EES-00011/12 scope)
- `src/ees/fact_extractor.py` — still produces v1 RuleThen (EES-00011)
- `src/ees/gap_detector.py` — uses deprecated requires/produces fields (EES-00011)
- `src/ees/gui/app.py` — uses deprecated type/requires/produces/note (EES-00012)

## Test Results
- 234 tests passing (87 new v2 tests + 147 existing tests via backward compat)
- All three core test files rewritten: test_models.py, test_rule_evaluator.py, test_rule_generator.py
