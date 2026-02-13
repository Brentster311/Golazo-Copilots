# EES-00004 — Architect Decision Notes

## QA Finding Resolutions

| Finding | Resolution | Rationale |
|---------|-----------|-----------|
| MJ-1: String-based match_key() | **Confirmed acceptable** | Symbolic expert system — input facts mirror extracted fact format. Numeric evaluation deferred to future story. |
| MN-1: Comma delimiter | **Use semicolons** | Safer — fact values can contain commas. Semicolons are unambiguous in fact format. |
| MN-2: Serialization format | **Confirmed** | Use existing `Rule.to_dict()`. Trace entries: `{rule_id, iteration, derived}`. |
| MN-3: --output flag | **Include in V1** | Simple to implement (ruamel.yaml dump), completes the structured output story. |

## Architectural Decisions

### AD-1: Module Boundary
`rule_evaluator.py` is a pure computation module — takes `list[Rule]` + `list[Fact]`, returns `EvaluationResult`. No I/O, no side effects, no YamlStore dependency. CLI layer in `main.py` handles I/O.

### AD-2: Derived Fact Operator
Derived facts from `RuleThen` use operator `==` (assertion semantic). This ensures derived facts can participate in further chaining via `match_key()` matching.

### AD-3: Instance Matching
Exact match on instance field. Generalized rules (`*`) match input facts that also use `*`. No wildcard expansion in V1. Users input facts at the same abstraction level as rules.

### AD-4: OR Logic Branch
Evaluation loop checks `rule.conditions.logic`:
- `"AND"`: all condition `match_key()`s must be in working set
- `"OR"`: at least one condition `match_key()` must be in working set

### AD-5: Forward Chaining Termination
Convergence guaranteed because:
1. Rules only add facts (never remove)
2. Working set uses `match_key()` deduplication — each unique fact added at most once
3. Rule set is finite
4. Maximum iterations = number of unique derivable facts

### AD-6: No Scope Changes
All design elements align with the design doc. No new user stories needed.

## Security/Privacy
- No external API calls during evaluation
- No file writes except optional `--output` (user-specified path)
- No credential handling in evaluator module

## Contract Summary
```
RuleEvaluator.__init__(rules: list[Rule]) -> None
RuleEvaluator.evaluate(input_facts: list[Fact]) -> EvaluationResult
EvaluationResult.to_dict() -> dict
```

## Approval
**Approved** — Design is architecturally sound. All QA findings resolved. Additive changes only, no contract breaks.
