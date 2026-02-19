# EES-00018 — Review Comments

## Design Doc Review

### Clarity & Completeness
- **PASS**: Goal semantics (initial/terminal/is_goal) are clearly defined
- **PASS**: Three termination outcomes (resolved/escalated/in_progress) cover all cases
- **PASS**: Backward compatibility is explicit — `goal=None` means today's behavior

### Feasibility & Sequencing
- **PASS**: Four-step approach is well ordered — models first, then evaluator
- **PASS**: Dependencies (EES-00016, EES-00017) are both satisfied

### Edge Cases to Address
1. **Goal property not in working set initially**: The evaluator needs to seed the goal fact (`Fact(goal.noun, goal.instance, goal.property, "==", goal.initial)`) into the working set at start. **Recommendation**: Add this to FR-4 explicitly — the evaluator creates the initial goal fact if it's not already in `input_facts`.
2. **Multiple GAPs in same iteration**: Design says "first GAP sets escalated" — but the evaluator should still record all GAP outputs. Only the *termination decision* happens on the first GAP. **Recommendation**: Check escalation at end-of-iteration, not mid-iteration, consistent with termination-after-full-iteration design.
3. **Goal terminal value matches initial**: If `initial` is in `terminal`, evaluation terminates immediately. **Recommendation**: This is a valid (if unusual) configuration — test it but don't block it.
4. **Max iterations**: The current evaluator doesn't have a max iteration limit — it runs until fixed-point. **Recommendation**: Add a `max_iterations` parameter (default 100) to prevent infinite loops in pathological rule sets. This is implicit in the user story's acceptance criteria.

### Naming
- **PASS**: `Goal`, `goal_status`, `is_goal`, `initial`, `terminal` are clear
- **PASS**: `resolved`/`escalated`/`in_progress` are unambiguous status values

### Risks Not Covered
- **No goal validation**: Nothing prevents `is_goal=True` with `initial` not in `values` or `terminal` values not in `values`. **Recommendation**: Add a `Goal.validate(ontology_property)` or check in `OntologyProperty` — but this can be a follow-up. Note it as a known gap.

## Verdict
**Approved** — proceed. Address edge case #1 (initial goal fact seeding) and #4 (max_iterations) in implementation.

---

## Architect Notes

### Architectural Alignment
- **PASS**: Extends existing dataclass models — consistent with codebase
- **PASS**: `Goal` as a separate dataclass decouples evaluator from ontology internals
- **PASS**: Optional `goal` parameter preserves backward compatibility

### Contracts
- `evaluate(input_facts, goal=None) -> EvaluationResult` — clear contract, additive parameter
- `Goal` is a value object — no side effects, no dependencies
- `goal_status` Literal type constrains values at the type level

### Capability Impact
- Files: `models.py`, `rule_evaluator.py`
- Directly: `data-models`, `rule-evaluation`
- Transitively: `yaml-persistence`, `cli-orchestration`, `gui`, `fact-extraction`, `rule-generation`
- All changes additive. `evaluate()` signature gains optional param.

### Blast Radius
- Minimal: `goal=None` default means zero behavior change for existing callers.
- `EvaluationResult.goal_status=None` default means existing consumers unaffected.

### Security / Privacy
- N/A — internal evaluation logic

### Verdict
**Approved** — proceed to implementation.
