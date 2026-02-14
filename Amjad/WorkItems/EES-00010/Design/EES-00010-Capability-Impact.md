# EES-00010 — Capability Impact

## Directly Affected Capabilities
| Capability | Key Files | Impact |
|------------|-----------|--------|
| data-models | `src/ees/models.py` | Replace `RuleThen` with `RuleOutput`, add `else_` to `Rule` |
| rule-evaluation | `src/ees/rule_evaluator.py` | Add ELSE branch evaluation, output-to-fact mapping |
| rule-generation | `src/ees/rule_generator.py` | Update `is_duplicate` and `filter_rules` for new types |

## Transitively Affected Capabilities
| Capability | Impact | Handled By |
|------------|--------|------------|
| yaml-persistence | Rule YAML format changes | EES-00010 (serialization in models) |
| fact-extraction | LLM prompt produces v2 rules | EES-00011 |
| ontology-management | No direct impact | N/A |
| cli-orchestration | Uses EvaluationResult — fields change | EES-00010 (model update) |
| gui | Displays rules and evaluation results | EES-00012 |
