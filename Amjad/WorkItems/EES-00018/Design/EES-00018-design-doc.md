# EES-00018 — Design Doc: Goal Declaration and Evaluation Termination

## Summary
Add goal-based termination to the rule evaluation engine. A goal is an `OntologyProperty` annotated with `is_goal=True`, `initial` value, and `terminal` values. The evaluator stops when the goal fact reaches a terminal value (resolved), a GAP fires while the goal is still in progress (escalated), or max iterations are reached (inconclusive). `EvaluationResult` gains a `goal_status` field.

## Problem Statement
Today the rule evaluator runs until no new facts are derived (fixed-point). It has no concept of "done" — it doesn't know what question the evaluation is trying to answer. This means:
- Evaluation may rule things out without ever converging on an answer
- There's no way to distinguish "we found the root cause" from "we exhausted all rules"
- The evaluator has no early-termination path — it must always process every rule
- Operators can't tell from `EvaluationResult` whether the problem was solved

## Business Case
- **Why now**: EES-00016 (typed ontology) and EES-00017 (structured CHANGE_STATE) are both implemented. Resolution rules can now write typed values to goal properties using the structured target fields.
- **Impact**: Evaluation converges to an answer. Operators see "resolved" / "escalated" / "in_progress" instead of raw lists.
- **KPIs**: All evaluations with a declared goal report a `goal_status`.

## Stakeholders
- Knowledge engineers (declaring goals in ontology)
- Rule evaluator engine (checking termination)
- GUI/CLI (displaying goal status)

## Functional Requirements

### FR-1: OntologyProperty goal annotations
```python
@dataclass
class OntologyProperty:
    name: str
    type: str = "enum"
    values: list[str] = field(default_factory=list)
    default: str | None = None
    is_goal: bool = False                    # NEW
    initial: str | None = None               # NEW — starting value for goal
    terminal: list[str] = field(default_factory=list)  # NEW — terminal values
```

Goal semantics: when `is_goal=True`, the property's `initial` value is the starting state, and `terminal` values are the end states that resolve the evaluation. The `initial` value must be in `values` (for enum type). All `terminal` values must also be in `values`.

### FR-2: Goal dataclass
```python
@dataclass
class Goal:
    """A goal for evaluation — which property to watch and when to stop."""
    noun: str
    instance: str
    property: str
    initial: str
    terminal: list[str]
```

This is extracted from the ontology at evaluation time. It tells the evaluator what to watch. A `Goal` is optional — evaluations without a goal work exactly as before.

### FR-3: EvaluationResult.goal_status
```python
@dataclass
class EvaluationResult:
    ...
    goal_status: Literal["in_progress", "resolved", "escalated"] | None = None
```

- `None` — no goal was declared (backward compatible)
- `"in_progress"` — max iterations reached, goal not satisfied
- `"resolved"` — goal fact's value is in the terminal set
- `"escalated"` — a GAP fired while goal was still in_progress

### FR-4: Rule evaluator termination logic
Modify `RuleEvaluator.evaluate()` to accept an optional `goal: Goal | None`:

```python
def evaluate(self, input_facts: list[Fact], goal: Goal | None = None) -> EvaluationResult:
```

Inside the forward-chaining loop, after each rule fires:
1. If `goal` is set and a derived fact matches `(goal.noun, goal.instance, goal.property)` with a value in `goal.terminal` → stop immediately, `goal_status = "resolved"` (per-rule check)
2. After a full iteration completes: if `goal` is set and a GAP output fired during this iteration → stop, `goal_status = "escalated"`
3. After the loop ends with no termination trigger → `goal_status = "in_progress"` if goal exists, `None` if no goal

### FR-5: Serialization
- `OntologyProperty.to_dict()` / `from_dict()` handle `is_goal`, `initial`, `terminal`
- `Goal.to_dict()` / `Goal.from_dict()` for roundtrip
- `EvaluationResult.to_dict()` includes `goal_status`

## Non-Functional Requirements
- No new dependencies
- Backward compatible: evaluations without a goal behave exactly as today (`goal_status=None`)
- Goal checking adds O(1) per rule firing (single key lookup)

## Proposed Approach

### Step 1: Extend OntologyProperty (models.py)
Add `is_goal`, `initial`, `terminal` fields. Update `to_dict()` / `from_dict()`.

### Step 2: Add Goal dataclass (models.py)
Simple dataclass with `noun`, `instance`, `property`, `initial`, `terminal`.

### Step 3: Extend EvaluationResult (models.py)
Add `goal_status` field, update `to_dict()`.

### Step 4: Modify RuleEvaluator.evaluate() (rule_evaluator.py)
Add optional `goal` parameter. Insert termination checks after each rule fires.

### Step 5: Unit Tests
Cover all acceptance criteria — see Test Strategy below.

## Alternatives Considered
1. **Goal in incident YAML**: Rejected — goals are properties of the domain (ontology), not the specific incident. Making goals reusable across incidents.
2. **Separate GoalEvaluator class**: Rejected — termination is part of the evaluation loop, not a separate concern. Extracting it would split a single loop into two coordinating objects.
3. **Automatic escalation on fixed-point**: Rejected — reaching a fixed-point without resolution isn't always escalation-worthy. The user story explicitly ties escalation to GAP firing.

## Risks and Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Early termination misses a rule that should have fired | Low | Medium | Only stop *after* the current iteration completes — all rules in the current pass get a chance to fire |
| Goal declared but no resolution rule exists | Medium | Low | Evaluation reaches fixed-point, returns `in_progress` — operator sees the status |
| Multiple GAPs fire in same iteration | Low | Low | First GAP sets escalated; others still recorded in outputs |

## Dependencies
- EES-00016 (typed ontology) — IMPLEMENTED ✓
- EES-00017 (structured CHANGE_STATE) — IMPLEMENTED ✓

## Migration / Rollout / Rollback
- **Rollout**: Additive fields only. No existing APIs change signature (goal defaults to None).
- **Rollback**: Revert models.py and rule_evaluator.py. Fields are ignored by old code.
- **Data migration**: None. Existing ontology YAML without goal annotations loads unchanged.

## Observability Plan
- N/A for initial implementation. `goal_status` is visible in `EvaluationResult.to_dict()`.

## Capability Impact
- **Directly affected**: `data-models` (OntologyProperty, EvaluationResult, new Goal), `rule-evaluation` (termination logic)
- **Transitively affected**: `yaml-persistence`, `cli-orchestration`, `gui`, `fact-extraction`, `rule-generation`

## Test Strategy Summary
| Test | Description | Type |
|------|-------------|------|
| goal resolved | Goal reaches terminal value → resolved | Unit |
| goal escalated | GAP fires while in_progress → escalated | Unit |
| goal inconclusive | Max iterations, goal still in_progress | Unit |
| no goal (backward compat) | goal=None → goal_status=None, behavior unchanged | Unit |
| OntologyProperty goal fields | is_goal/initial/terminal serialization | Unit |
| Goal dataclass | Construction and round-trip | Unit |
| EvaluationResult goal_status | to_dict includes status | Unit |
| goal early termination | Stops before processing remaining rules | Unit |
