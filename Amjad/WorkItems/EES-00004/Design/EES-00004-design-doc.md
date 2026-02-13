# EES-00004 — Design Doc: Rule Evaluation Engine (Testing Phase)

## Summary
Add an `evaluate` CLI command that takes a set of observed facts and evaluates all rules from the knowledge base against them, reporting which root causes are identified, which are ruled out, which GAP rules were encountered, and the full rule chain trace.

## Problem Statement
The expert system can learn rules from incidents (EES-00001/02/03) but cannot yet test those rules. The evaluation engine enables the "testing phase" — validating diagnostic accuracy by running rules against input facts and reporting results.

## Business Case
- **Why now:** Learning loop (EES-00001), GAP detection (EES-00002), and RULEOUT rules (EES-00003) are all complete. The knowledge base needs validation — evaluation is the natural next step.
- **Impact:** Enables users to verify the expert system gives correct diagnoses, identify blind spots (GAPs), and audit elimination reasoning (RULEOUTs).
- **KPIs:** Rules evaluated vs. fired, root causes identified vs. ruled out, GAP rules triggered.

## Stakeholders
- Technical user — validates diagnostic rules
- Future GUI (EES-00005) — will wrap this engine

## Functional Requirements

### FR-1: New CLI Command `ees evaluate`
```bash
ees evaluate --facts "Server(*).CPUUsage > 90, Server(*).MemoryFree < 5%" --data-dir data
```
Alternatively, facts from a file:
```bash
ees evaluate --facts-file path/to/facts.yaml --data-dir data
```
Both options parse facts into `Fact` objects using `Fact.parse()`.

### FR-2: Rule Evaluation Engine (`rule_evaluator.py`)
New module: `src/ees/rule_evaluator.py` with `RuleEvaluator` class.

**Core algorithm (forward chaining):**
1. Start with input facts as the working set.
2. Iterate all CONFIRMED rules. For each:
   - Check if ALL condition facts match working set (using `match_key()`).
   - If matched: the rule "fires" — add its `then` as a derived fact to the working set.
3. Repeat until no new facts are derived (fixed-point).
4. After convergence, scan for:
   - **Root causes:** Rules that fired where `then.noun == "RootCause"` — collected as identified.
   - **RULEOUTs:** Rules that fired where `then.noun == "RULEOUT"` (type="ruleout") — collected as eliminated root causes.
   - **GAPs:** GAP-status rules whose `requires` facts are all in the working set — these indicate incomplete chains.

### FR-3: Chained Rule Execution (Dependency Order)
Forward chaining naturally handles dependency order:
- Rule A: IF X THEN Y
- Rule B: IF Y THEN RootCause = Z
- Given fact X, iteration 1 fires A (adds Y), iteration 2 fires B (adds RootCause=Z).

### FR-4: Conflict Handling
When multiple root causes match, ALL are presented as candidates (per design decision). No silent resolution.

### FR-5: Evaluation Result Model
```python
@dataclass
class EvaluationResult:
    input_facts: list[Fact]
    derived_facts: list[Fact]
    fired_rules: list[Rule]        # In firing order
    root_causes: list[str]          # Identified root causes
    ruled_out: list[str]            # Eliminated root causes
    gap_rules: list[Rule]           # Encountered GAP rules
    rule_trace: list[dict]          # [{rule_id, conditions_matched, derived_fact}]
```

### FR-6: Structured Output
Print evaluation results to stdout in a human-readable format. Optionally write to YAML file with `--output path/to/result.yaml`.

### FR-7: Read-Only Operation
The evaluation engine does NOT modify any persisted data. No writes to `rules/`, `incidents/`, `ontology.yaml`, or `rootcauses.yaml`.

## Non-Functional Requirements
- **Deterministic:** Same input facts + same knowledge base = same output (always).
- **Finite:** Forward chaining terminates when no new facts are derived (convergence guaranteed because rules only add facts, never remove).
- **Human-readable trace:** Each fired rule shows what conditions matched and what was derived.

## Proposed Approach

### Step 1: EvaluationResult Model (`models.py`)
- Add `EvaluationResult` dataclass with fields for input/derived facts, fired rules, root causes, ruled out, gaps, and trace.
- `to_dict()` for YAML output.

### Step 2: RuleEvaluator Class (`rule_evaluator.py`)
- Constructor: takes `list[Rule]` (all rules from knowledge base).
- `evaluate(input_facts: list[Fact]) -> EvaluationResult`.
- Forward chaining loop with `match_key()`-based matching.
- Trace each fired rule with its matched conditions and derived fact.
- After convergence, scan GAP rules for triggered ones.

### Step 3: CLI Integration (`main.py`)
- Add `evaluate` subcommand to argparse.
- Parse `--facts` (comma-separated) or `--facts-file` (YAML file) into `Fact` objects.
- Load all rules from `YamlStore.list_rules()`.
- Run `RuleEvaluator.evaluate()`.
- Print results. Optionally write to `--output` file.

### Step 4: Fact Matching
- Conditions use `match_key()` for normalized comparison (case-insensitive noun/property).
- Derived facts are also `Fact` objects created from `RuleThen` fields.

## Alternatives Considered

| Alternative | Reason Rejected |
|-------------|----------------|
| Backward chaining (goal-directed) | Forward chaining is simpler and naturally handles chaining. Backward chaining would require goal specification. |
| External rule engine (e.g., Drools) | Overkill for flat AND/OR rules. Python evaluation is trivial. |
| Interactive evaluation (step-by-step) | Out of scope. Batch evaluation is the testing use case. |

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Infinite loop in forward chaining | Convergence guaranteed: rules only add facts, working set is finite, each fact added at most once |
| Operator matching complexity (>, <, etc.) | V1 uses exact `match_key()` matching — operators are compared as strings, not evaluated numerically. This is correct for rule matching against extracted facts. |
| Large rule set performance | Rules are flat with few conditions each. Forward chaining with set lookups is O(rules × iterations). Performance is not a concern for this scale. |

## Open Questions
None.

## Dependencies
- EES-00001 (Core Loop) — models, yaml_store
- EES-00002 (GAP Rules) — GAP rule detection
- EES-00003 (RULEOUT Rules) — RULEOUT rule type

## Migration / Rollout / Rollback
- **Additive:** New command, new module. No changes to existing functionality.
- **Read-only:** No rollback needed — no data modification.

## Observability Plan
- Evaluation output includes counts: rules evaluated, rules fired, root causes found, ruleouts fired, GAPs encountered.

## Test Strategy Summary
- **Unit tests:** `RuleEvaluator.evaluate()` with various rule sets and input facts.
- **Unit tests:** Forward chaining with dependent rules (chain depth 2+).
- **Unit tests:** RULEOUT rules fire and report eliminated root causes.
- **Unit tests:** GAP rules detected in evaluation.
- **Unit tests:** Conflicting root causes (multiple matches).
- **Unit tests:** No rules fire (empty result).
- **Integration tests:** `ees evaluate` CLI command with `--facts` and `--data-dir`.
- **Negative tests:** Invalid fact format in `--facts`, missing data dir.
