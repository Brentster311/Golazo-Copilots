# EES-00019 Design Doc: Structured Expert System Language

## Summary
Replace the current IF/THEN/ELSE rule grammar (CHANGE_STATE/RULED_OUT/GAP) with a minimal, deterministic expert system language using 10 keywords: RULE, BEGIN, END, CHECK, DECIDE, ASSERT, RETRACT, ACT, NOOP, GAP. The new language enforces structural validity, makes reasoning explicit and traceable, and enables forward-chaining convergence through typed working-memory mutations.

## Problem Statement
The current system cannot converge to a diagnostic conclusion because:
1. **No typed ontology in extraction** - `_handle_get_ontology()` only sends property names, not types/legal values. The LLM invents free-text values that never match rule conditions.
2. **Pseudo-facts from descriptions** - `CHANGE_STATE("User.adminRole => confirmed")` produces a pseudo-fact keyed by the description string. No real property value is mutated in working memory.
3. **No goal awareness** - Despite EES-00018 adding goal fields, nothing constructs a `Goal` or passes it to `evaluate()`. The engine runs to fixed-point but has no definition of "done."

These are symptoms of a deeper issue: the rule grammar is too loose. Free-text descriptions are not machine-actionable. The proposed language replaces narrative descriptions with explicit CHECK/ASSERT/RETRACT operations on typed working memory.

## Business Case
- **Why now**: The system extracts facts and rules but evaluation never converges - the core value proposition is broken.
- **Impact**: Enables the engine to actually diagnose incidents, producing a traceable reasoning chain from input facts to root cause.
- **KPI**: After this change, running the evaluator on INC-001's facts should terminate with `goal_status="resolved"` or `goal_status="escalated"` (not `None`).

## Stakeholders
- Knowledge engineers (primary users of GUI)
- The LLM (produces rules in the new grammar via tool calls)
- Engine internals (parser, evaluator, serializer)

## Functional Requirements

### FR-1: AST Model (data models)
New dataclasses in `models.py`:
- `Stmt` - base for all statements, with a `kind` discriminator
- `CheckStmt` - contains a fact expression (noun, instance, property, operator, value); produces a boolean
- `DecideStmt` - contains a `CheckStmt`, a `then_block: Block`, and an `else_block: Block`
- `AssertStmt` - contains a fact to add to working memory (noun, instance, property, operator, value)
- `RetractStmt` - contains a fact pattern to remove from working memory
- `ActStmt` - contains a description string (external side-effect, trace only)
- `NoopStmt` - no fields
- `GapStmt` - contains a description string (unknown reasoning)
- `Block` - contains `list[Stmt]`
- `RuleBlock` - contains an optional `rule_id: str` and a `Block`

### FR-2: YAML Serialization
Rules serialize to YAML mirroring the AST tree:
```yaml
rule_id: R-001
block:
  - check:
      noun: User
      instance: $u
      property: adminRole
      operator: ==
      value: unknown
    decide:
      then:
        - assert:
            noun: User
            instance: $u
            property: adminRole
            value: confirmed
      else:
        - retract:
            noun: User
            instance: $u
            property: adminRole
            value: unknown
        - gap: "Admin role could not be confirmed"
```
`from_dict()` and `to_dict()` methods on each node. Round-trip fidelity required.

### FR-3: Parser / Validator
A `parse_rule(d: dict) -> RuleBlock` function that:
- Validates keyword set (only the 10 valid keywords)
- Validates structural rules (DECIDE has exactly 2 blocks, etc.)
- Returns typed AST or raises `ParseError` with descriptive message

### FR-4: Forward-Chaining Evaluator
New `ASTEvaluator` class (or updated `RuleEvaluator`):
1. Takes a list of `RuleBlock` objects and initial working memory (list of `Fact`)
2. For each iteration: execute all rules sequentially against working memory
3. CHECK reads working memory, returns boolean
4. DECIDE branches on CHECK result: then_block if True, else_block if False
5. ASSERT adds a fact to working memory
6. RETRACT removes a fact from working memory
7. ACT records to trace, does not modify memory
8. NOOP records to trace, does nothing
9. GAP records to trace as a terminal signal
10. Repeat until no ASSERT/RETRACT changes occur (fixed-point) or max iterations reached
11. If a Goal is declared, check goal termination after each iteration (reuse EES-00018 logic)

### FR-5: LLM Integration
Update `FactExtractor`:
- System prompt describes the new language grammar and semantics
- `submit_rule` tool schema matches the YAML AST structure
- `_validate_output_branch` replaced by full AST validation via `parse_rule()`
- `_handle_get_ontology()` sends property types, legal values, and goal annotations
- Validation errors returned to LLM for self-correction

### FR-6: GUI Display
Update the Proposed Rules table in `app.py` and `adapters.py`:
- Display rules as indented keyword trees (CHECK, DECIDE with nested THEN/ELSE blocks)
- Columns: Rule_Id, Structure (multi-line keyword tree), Status
- Existing Confirm/Reject buttons work on the new rule format

## Non-Functional Requirements
- No new external dependencies (pure Python parser and evaluator)
- Max-iteration guard (default 100) prevents infinite loops
- Evaluation must produce an ordered trace: each entry records rule_id, statement kind, and working memory delta

## Proposed Approach (High Level)

### Phase 1: AST Model + Serialization
1. Define new dataclasses in `models.py` (or new `ast_models.py`)
2. Implement `to_dict()` / `from_dict()` on each node
3. Implement `parse_rule()` validator
4. Unit tests for parsing, validation, round-trip

### Phase 2: Evaluator
1. New `ASTEvaluator` class with `evaluate(rules, facts, goal=None)` method
2. Working memory as set of Facts with match_key() lookup
3. Trace recording
4. Goal termination integration
5. Unit tests for convergence, branching, trace

### Phase 3: LLM Integration
1. Update system prompt with new grammar
2. Update `submit_rule` tool schema
3. Update `_handle_get_ontology()` to include types/values
4. Validation via `parse_rule()`
5. Delete old rules R-001 through R-004

### Phase 4: GUI
1. Update `rules_to_rows()` adapter for new AST structure
2. Update Proposed Rules table display
3. Evaluation results panel shows trace

## Alternatives Considered

| Alternative | Why rejected |
|------------|-------------|
| Patch existing IF/THEN/ELSE grammar | Root cause is the grammar is too loose. Patches (EES-00016/17/18) didn't wire through to extraction. |
| Use external grammar toolkit (ANTLR/PLY) | Adds dependency, overkill for 10 keywords. Pure Python is simpler. |
| Plain text `.ees` files | YAML AST is more consistent with existing storage and easier for LLM to produce via JSON tool calls. |
| Incremental migration (keep old rules) | User explicitly chose clean break. Old rules use description strings that can't be auto-converted to typed ASSERT/RETRACT. |

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| LLM fails to produce valid AST | Medium | High | Validation errors are returned to LLM for self-correction. System prompt includes concrete examples. Max turns = 20. |
| Large scope causes partial implementation | Medium | Medium | Phased approach. Each phase is independently testable. Phase 1+2 are the critical path; Phase 3+4 can be deferred if needed. |
| Breaking change disrupts existing workflow | Low | Low | Only 4 rules exist, all from same incident. User chose to delete them. Git revert is the rollback. |
| Nested DECIDE causes complex traces | Low | Low | Trace records indentation level. Tests cover 3-deep nesting. |

## Open Questions
1. Should the existing `Rule`, `RuleConditions`, `RuleOutput` classes be kept as deprecated wrappers, or removed entirely? **Proposed**: Remove. Clean break.
2. Should `Fact` remain the working memory unit, or should a new `WorkingMemoryEntry` be introduced? **Proposed**: Reuse `Fact`. It already has noun/instance/property/operator/value and match_key().
3. Should `ACT` statements have structured fields (target team, action type) or remain free-text? **Proposed**: Free-text description for now. Structure can be added later.

## Dependencies
- EES-00016 (typed ontology): `OntologyProperty.validate_value()` used by CHECK validation
- EES-00018 (goal termination): `Goal` dataclass and `goal_status` used by evaluator
- Azure OpenAI deployment (existing) for LLM extraction

## Migration / Rollout / Rollback
- **Migration**: Delete `data/rules/R-001.yaml` through `R-004.yaml`. No auto-migration.
- **Rollout**: All-at-once. New grammar is used by both extraction and evaluation.
- **Rollback**: Git revert restores old grammar, old rules, old prompt.

## Observability Plan
- Extraction logs: number of rules emitted, rejected, correction turns
- Evaluation logs: iteration count, ASSERT/RETRACT count per iteration, convergence reason (fixed-point / goal-resolved / goal-escalated / max-iterations)
- Trace: full ordered record of CHECK results, ASSERT/RETRACT deltas, ACT/GAP signals

## Test Strategy Summary
- **Unit tests**: AST parsing (valid/invalid), YAML round-trip, evaluator convergence, CHECK/DECIDE branching, ASSERT/RETRACT memory mutation, trace correctness
- **Integration tests**: End-to-end extraction with mock LLM producing AST rules, followed by evaluation
- **GUI tests**: `rules_to_rows()` adapter produces correct display dicts for new AST structure
- **Regression**: All non-rule tests (fact extraction validation, ontology management, YAML store for incidents/ontology) must continue to pass
