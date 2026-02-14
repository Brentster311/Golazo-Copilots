# EES-00009 Project Owner Assistant Notes

## Decision: Decomposition
The user requested "Option C — Prolog-style variable binding" as a new story. This is a significant redesign touching models, evaluator, LLM prompt, GUI, and persistence. Decomposed into 3 slices per user's agreement:

1. **EES-00009**: Core engine — variable binding in Fact/Rule/RuleEvaluator
2. **Future**: LLM prompt to produce variable-bound output
3. **Future**: GUI display/editing of variables

## Decision: Variable syntax
Chose `$varname` prefix convention (Prolog/shell-inspired). Alternatives considered:
- `{varname}` — conflicts with Python format strings
- `:varname` — conflicts with YAML syntax
- `?varname` — less intuitive

## Decision: `*` vs `$var` semantics
Kept `*` as literal match (backward compatible). Variables are a separate mechanism:
- `*` = "this fact applies to all instances" (literal string matching)
- `$op` = "bind this to a concrete instance and enforce consistency across conditions"

## Must-Ask Checklist
- [x] Interface type: Established (Tkinter GUI + CLI) — engine-only change in this slice
- [x] Target platform: Windows
- [x] Data persistence: YAML files
- [x] User type: Technical (support engineers)
