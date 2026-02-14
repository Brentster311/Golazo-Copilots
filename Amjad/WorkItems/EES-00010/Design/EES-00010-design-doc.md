# EES-00010 — Design Doc: V2 Rule Grammar Data Model & Engine

## Summary
Replace the v1 rule model (positive/ruleout types with RuleThen noun/instance/property/value) with a v2 grammar: `IF <conditions> THEN CHANGE_STATE|RULED_OUT|GAP [ELSE CHANGE_STATE|RULED_OUT|GAP]`. The engine must evaluate both branches.

## Problem Statement
The v1 model represents rule outputs as `Noun(instance).Property = value` with a `type` flag of `positive` or `ruleout`. This cannot express:
- Diagnostic branching (what happens when conditions are NOT met)
- Three distinct output semantics (state mutation, elimination, knowledge gap)
- Chaining of RULED_OUT outputs as conditions of downstream rules

## Business Case
The expert system output will be compiled into deterministic code. The v2 grammar maps cleanly to code generation — each entity type has clear compile-time semantics. Without this, the rule engine cannot represent real troubleshooting workflows.

## Proposed Approach

### Data Model Changes (`models.py`)

1. **New `RuleOutput` dataclass** replaces `RuleThen`:
   ```python
   @dataclass
   class RuleOutput:
       kind: Literal["CHANGE_STATE", "RULED_OUT", "GAP"]
       description: str
   ```

2. **`Rule` updated**:
   - Remove: `type` field, `then` (RuleThen), `requires`/`produces`/`note` (GAP-specific)
   - Add: `then: RuleOutput`, `else_: RuleOutput | None = None`
   - Keep: `rule_id`, `status`, `sources`, `conditions`, `because`
   - `conditions.logic` becomes AND-only (OR already decomposed per v1 design)

3. **`EvaluationResult` updated**:
   - Remove: `root_causes`, `ruled_out`, `gap_rules` (type-specific lists)
   - Add: `outputs: list[dict]` — `[{rule_id, branch: "then"|"else", output: RuleOutput}]`
   - Convenience properties: `.change_states`, `.ruled_outs`, `.gaps`

4. **YAML serialization** — rules serialize as:
   ```yaml
   rule_id: R1
   status: CONFIRMED
   sources: [INC-001]
   conditions:
     logic: AND
     items: [{noun: User, instance: "*", property: role, operator: "==", value: non-admin}]
   then: {kind: CHANGE_STATE, description: "User.role => admin-escalated"}
   else: {kind: RULED_OUT, description: "User access is not the issue"}
   ```

### Engine Changes (`rule_evaluator.py`)

1. **ELSE evaluation**: When a rule's conditions are NOT met and `else_` is present, fire the ELSE branch — add its output to the working set as a derived fact.

2. **Output as derived fact**: `RuleOutput` maps to a `Fact` for working-set matching:
   - `CHANGE_STATE("X")` → `Fact(noun="CHANGE_STATE", instance="*", property="description", operator="==", value="X")`
   - `RULED_OUT("X")` → `Fact(noun="RULED_OUT", instance="*", property="description", operator="==", value="X")`
   - `GAP("X")` → recorded but NOT added to working set (terminal)

3. **Chaining**: R4's condition `RULED_OUT("User access is not the issue")` matches the derived fact from R1's ELSE branch.

4. **ELSE firing semantics**: ELSE branches only fire once (same as THEN — rule fires at most once per evaluation).

### Rule Generator Changes (`rule_generator.py`)

- `is_duplicate` compares `then` and `else_` (new structure)
- `filter_rules` validates conditions against confirmed facts (unchanged logic, new types)

## Alternatives Considered
- **Keep v1, add ELSE as post-processing**: Rejected — doesn't allow ELSE outputs to chain as conditions.
- **Nested IF/THEN/ELSE trees**: Rejected — user wants flat rules with optional ELSE.

## Risks & Mitigations
| Risk | Mitigation |
|------|-----------|
| Breaking change to existing YAML rules | Accept — rules will be re-extracted with EES-00011 |
| ELSE firing order matters | Engine iterates until fixed-point; ELSE fires same iteration as THEN |
| Performance regression from failed-condition scanning | Minimal — rules list is small |

## Dependencies
- None (first in the EES-00010/11/12 chain)

## Test Strategy
- Unit tests for `RuleOutput` construction and serialization
- Unit tests for `Rule` with/without ELSE, YAML round-trip
- Engine tests: THEN fires, ELSE fires, both-branch chaining, GAP terminal
- Engine tests: backward compat — rules without ELSE still work
- `RuleGenerator.filter_rules` with new types
