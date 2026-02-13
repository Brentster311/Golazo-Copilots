# EES-00004 — Capability Impact Analysis

## Impact Summary
4 files changed → 6 capabilities affected (3 direct, 3 transitive)

## Directly Affected Capabilities

### data-models
- **File:** `src/ees/models.py`
- **Change:** Add `EvaluationResult` dataclass
- **Contract Impact:** Additive only — new class, no changes to existing `Fact`, `Rule`, etc.
- **Risk:** Low — no existing contract changes

### cli-orchestration
- **File:** `src/ees/main.py`
- **Change:** Add `evaluate` subcommand with `--facts`/`--facts-file`/`--output`/`--data-dir`
- **Contract Impact:** Additive — new subcommand, existing `process` command unchanged
- **Risk:** Low — existing CLI paths untouched

### NEW: rule-evaluation
- **File:** `src/ees/rule_evaluator.py` (new module)
- **Change:** New `RuleEvaluator` class with `evaluate()` method
- **Contract:** `RuleEvaluator(rules: list[Rule]).evaluate(input_facts: list[Fact]) -> EvaluationResult`
- **Risk:** None — entirely new capability

## Transitively Affected Capabilities

### yaml-persistence
- **Why:** `cli-orchestration` calls `YamlStore.list_rules()` to load rules for evaluation
- **Contract Change:** None — using existing `list_rules()` contract
- **Risk:** None

### fact-extraction, rule-generation, ontology-management
- **Why:** Depend on `data-models` which gets a new class
- **Contract Change:** None — `EvaluationResult` doesn't affect existing model classes
- **Risk:** None

## Capability Registry Update Required
Add to `capabilities.yaml`:
```yaml
- name: rule-evaluation
  description: "Forward-chaining rule evaluation engine"
  key_files:
    - src/ees/rule_evaluator.py
  contracts:
    - "RuleEvaluator.evaluate(input_facts) -> EvaluationResult"
  depends_on:
    - data-models
```
Update `cli-orchestration.depends_on` to include `rule-evaluation`.

## Conclusion
All changes are additive. No existing contracts broken. No blast radius concerns.
