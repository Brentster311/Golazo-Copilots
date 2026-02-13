# EES-00004 — Review Comments

## Design Review

### Findings

| ID | Severity | Area | Finding | Recommendation |
|----|----------|------|---------|----------------|
| MJ-1 | Major | FR-2 | Operator matching uses `match_key()` which compares operators as strings. This means `Server(*).CPUUsage > 90` in a rule condition will only match an input fact with identical noun, instance, property, operator, AND value. This is correct for symbolic matching but won't do numeric evaluation (e.g., input `CPUUsage == 95` won't match condition `CPUUsage > 90`). Design doc acknowledges this but architect should confirm this is acceptable for V1. | Architect to confirm: string-based `match_key()` matching is correct for testing-phase evaluation where input facts mirror the extracted fact format. |
| MN-1 | Minor | FR-1 | `--facts` parsing with comma separation breaks if fact values contain commas. | Recommend using semicolons as delimiters, or only support `--facts-file` for multi-fact input. Architect to decide. |
| MN-2 | Minor | FR-5 | `EvaluationResult.to_dict()` mentioned but serialization format of `fired_rules` and `gap_rules` not fully specified. | Include `Rule.to_dict()` for fired rules. Trace entries should include rule_id + derived fact display string. |
| MN-3 | Minor | FR-6 | `--output` flag mentioned for YAML file output. Clarify whether this is required for V1 or deferred. | Implement `--output` in V1 — it's simple and useful. |

### Overall Assessment
**Conditionally Approved** — Design is clean and well-structured. MJ-1 requires architect confirmation. Minor findings are clarification-level.

---

## Architect Notes

### MJ-1 Resolution: String-based `match_key()` — CONFIRMED ACCEPTABLE
String-based `match_key()` matching is correct for V1. Rationale:
- Facts are extracted by LLM in the same `Noun(instance).Property operator value` format as rule conditions. Testing-phase evaluation means input facts mirror extracted fact format exactly.
- The system is a symbolic expert system, not a numeric calculator. Rule conditions and facts both use the same operator+value pair, so exact string matching is the right semantic.
- Numeric evaluation (e.g., input `CPUUsage == 95` matching condition `CPUUsage > 90`) would require type inference from ontology — deferred to a future story if needed.
- **Action:** No design change. Document in code that matching is symbolic/string-based.

### MN-1 Resolution: Delimiter for `--facts` — SEMICOLONS
Use semicolons (`;`) as the delimiter for `--facts` CLI option. Rationale:
- Fact values could theoretically contain commas (e.g., `Error == "timeout, retry failed"`)
- Semicolons are unambiguous in the fact format `Noun(instance).Property operator value`
- Example: `--facts "Server(*).CPUUsage > 90; Server(*).MemoryFree < 5%"`
- **Action:** Update design and implementation to use `;` delimiter in `--facts` parsing.

### MN-2 Resolution: Serialization Format — CONFIRMED
- `EvaluationResult.to_dict()` should use `Rule.to_dict()` for `fired_rules` and `gap_rules` (already exists).
- `rule_trace` entries: `{"rule_id": str, "iteration": int, "derived": str}` where `derived` is `Fact.to_display()`.
- **Action:** No design change needed — this is implementation detail.

### MN-3 Resolution: `--output` Flag — INCLUDE IN V1
`--output` is simple (write `EvaluationResult.to_dict()` via `ruamel.yaml`) and completes the structured output story. Include in V1.

### Additional Architectural Notes

**AN-1: Derived Fact Construction**
When a rule fires, its `RuleThen` (noun, instance, property, value) must be converted to a `Fact` object for the working set. The derived fact uses operator `==` (assertion/assignment semantic). Example: `RuleThen(noun="RootCause", instance="*", property="Name", value="HighCPU")` → `Fact("RootCause", "*", "Name", "==", "HighCPU")`.

**AN-2: Instance Matching is Exact**
`match_key()` compares instances as-is. Generalized rules use `*`, so input facts should also use `*` to match them. No wildcard expansion in V1. This is documented behavior, not a limitation — users test with the same abstraction level as the rules.

**AN-3: OR Logic Handling**
For rules with `conditions.logic == "OR"`, the evaluator fires the rule if ANY condition fact matches the working set. For `"AND"`, ALL conditions must match. This is a straightforward branch in the evaluation loop.

**AN-4: Read-Only Safety**
The evaluator takes `list[Rule]` as input and produces `EvaluationResult` as output. No YamlStore writes. No side effects. Safe to run repeatedly.

**AN-5: Capability Registry Update**
Add new `rule-evaluation` capability to `capabilities.yaml` for `rule_evaluator.py` with contract `RuleEvaluator.evaluate(facts) -> EvaluationResult`. Depends on `data-models`. Update `cli-orchestration` to also depend on `rule-evaluation`.
