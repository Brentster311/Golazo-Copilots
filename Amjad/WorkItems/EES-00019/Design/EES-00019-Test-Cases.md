# EES-00019 Test Cases

## Mapping to Acceptance Criteria

| AC | Test Cases |
|----|-----------|
| AC-1: Parser produces valid AST, rejects invalid | TC-01 through TC-07 |
| AC-2: Evaluator executes and converges | TC-08 through TC-14 |
| AC-3: Evaluation produces ordered trace | TC-15, TC-16 |
| AC-4: LLM tool schema validates structural conformance | TC-17 through TC-20 |
| AC-5: GUI displays rules in new structure | TC-21, TC-22 |
| AC-6: YAML round-trip fidelity | TC-23, TC-24 |
| AC-7: Existing tests pass or are updated | TC-25 |

---

## Phase 1: AST Model + Parsing

### TC-01: Parse valid rule with CHECK/DECIDE/ASSERT
**Input**: YAML dict with CHECK on User.adminRole, DECIDE with ASSERT in then-block and GAP in else-block
**Expected**: Returns `RuleBlock` with `DecideStmt` containing correct check expression, then-block has `AssertStmt`, else-block has `GapStmt`
**Failure msg**: "Valid CHECK/DECIDE/ASSERT rule should parse without error"

### TC-02: Parse valid rule with nested DECIDE
**Input**: YAML dict with DECIDE containing another DECIDE in its then-block (2 levels deep)
**Expected**: Returns `RuleBlock` with nested `DecideStmt` inside the then-block
**Failure msg**: "Nested DECIDE blocks must parse correctly"

### TC-03: Parse valid rule with RETRACT
**Input**: YAML dict with RETRACT statement specifying noun/instance/property
**Expected**: Returns `RuleBlock` with `RetractStmt` having correct fields
**Failure msg**: "RETRACT statement should parse with noun/instance/property fields"

### TC-04: Parse valid rule with ACT and NOOP
**Input**: YAML dict with a block containing ACT("escalate to Exchange") and NOOP
**Expected**: Returns `RuleBlock` with `ActStmt` (description="escalate to Exchange") and `NoopStmt`
**Failure msg**: "ACT and NOOP statements should parse correctly"

### TC-05: Reject unknown keyword
**Input**: YAML dict containing `{"invoke": {"target": "something"}}`
**Expected**: Raises `ParseError` with message containing "Unknown keyword 'invoke'"
**Failure msg**: "Unknown keywords must be rejected with descriptive error"

### TC-06: Reject DECIDE with wrong number of blocks
**Input**: YAML dict with DECIDE containing only one block (missing else)
**Expected**: Raises `ParseError` with message containing "DECIDE requires exactly 2 blocks"
**Failure msg**: "DECIDE with missing else block must be rejected"

### TC-07: Reject DECIDE without CHECK
**Input**: YAML dict with a bare DECIDE (no check expression)
**Expected**: Raises `ParseError` with message containing "DECIDE requires a CHECK"
**Failure msg**: "DECIDE without a CHECK expression must be rejected"

---

## Phase 2: Evaluator

### TC-08: Simple ASSERT adds fact to working memory
**Input**: One rule with bare ASSERT(User.adminRole == confirmed). Working memory starts empty.
**Expected**: After evaluation, working memory contains Fact(User, *, adminRole, ==, confirmed)
**Failure msg**: "ASSERT should add the specified fact to working memory"

### TC-09: CHECK/DECIDE branches correctly - then path
**Input**: Working memory has Fact(User.adminRole == unknown). Rule: CHECK User.adminRole == unknown, DECIDE then=[ASSERT User.adminRole = confirmed] else=[NOOP]
**Expected**: After evaluation, working memory contains Fact(User.adminRole == confirmed). Old fact (unknown) may still be present unless explicitly retracted.
**Failure msg**: "DECIDE should take then-branch when CHECK is true"

### TC-10: CHECK/DECIDE branches correctly - else path
**Input**: Working memory has Fact(User.adminRole == confirmed). Rule: CHECK User.adminRole == unknown, DECIDE then=[ASSERT ...] else=[GAP "already confirmed"]
**Expected**: GAP recorded in trace. No ASSERT executed.
**Failure msg**: "DECIDE should take else-branch when CHECK is false"

### TC-11: RETRACT removes fact from working memory
**Input**: Working memory has Fact(User.adminRole == unknown). Rule with RETRACT(User.adminRole).
**Expected**: After evaluation, working memory no longer contains any User.adminRole fact.
**Failure msg**: "RETRACT should remove matching facts from working memory"

### TC-12: Fixed-point convergence
**Input**: Two rules. R1 asserts Fact A if Fact B exists. R2 asserts Fact B if Fact C exists. Working memory starts with Fact C.
**Expected**: After evaluation, working memory contains C, B, A. Evaluation terminates in <=3 iterations.
**Failure msg**: "Forward chaining should converge when no new ASSERT/RETRACT changes occur"

### TC-13: Max-iteration guard
**Input**: Rule that always asserts a new unique fact (infinite loop scenario - e.g., counter increment). Max iterations = 5.
**Expected**: Evaluation stops at 5 iterations. Result indicates max-iterations reached.
**Failure msg**: "Evaluation must terminate at max_iterations even if not converged"

### TC-14: Goal-based termination
**Input**: Goal(noun=Incident, property=rootCause, terminal=["admin_role_missing"]). Rule that asserts Incident.rootCause == admin_role_missing.
**Expected**: Evaluation stops with goal_status="resolved" after the ASSERT fires.
**Failure msg**: "Goal-based termination should stop evaluation when terminal value is reached"

### TC-15: Trace records CHECK result
**Input**: Rule with CHECK User.adminRole == unknown (condition met).
**Expected**: Trace entry includes rule_id, stmt_kind="CHECK", result=True, fact expression.
**Failure msg**: "Trace must record CHECK statement with boolean result"

### TC-16: Trace records ASSERT/RETRACT delta
**Input**: Rule with ASSERT and RETRACT in same block.
**Expected**: Trace entries include stmt_kind="ASSERT" with fact added, and stmt_kind="RETRACT" with fact removed.
**Failure msg**: "Trace must record working memory delta for ASSERT and RETRACT"

---

## Phase 3: LLM Integration

### TC-17: submit_rule accepts valid AST
**Input**: Tool call args matching the new YAML schema (CHECK/DECIDE/ASSERT structure).
**Expected**: Rule accepted, appended to collected_rules.
**Failure msg**: "submit_rule should accept structurally valid AST rules"

### TC-18: submit_rule rejects unknown keyword
**Input**: Tool call args containing `{"invoke": {...}}` in a block.
**Expected**: Returns error string "Unknown keyword 'invoke'", accepted=False.
**Failure msg**: "submit_rule should reject rules with unknown keywords"

### TC-19: submit_rule rejects DECIDE with one block
**Input**: Tool call args with DECIDE having only a then block.
**Expected**: Returns error string about missing else block, accepted=False.
**Failure msg**: "submit_rule should reject structurally invalid DECIDE"

### TC-20: get_ontology includes types and values
**Input**: Ontology with OntologyProperty(name="adminRole", type="enum", values=["unknown", "confirmed", "denied"])
**Expected**: `_handle_get_ontology()` returns JSON including `{"name": "adminRole", "type": "enum", "values": ["unknown", "confirmed", "denied"]}`
**Failure msg**: "get_ontology must include property types and legal values"

---

## Phase 4: GUI

### TC-21: rules_to_rows produces display dicts for AST rules
**Input**: List of `RuleBlock` objects with CHECK/DECIDE/ASSERT structure.
**Expected**: Each row dict has keys: rule_id, summary (human-readable keyword structure), status.
**Failure msg**: "rules_to_rows must produce display-ready dicts for new AST rules"

### TC-22: rules_to_rows handles empty rule (block with no statements)
**Input**: `RuleBlock` with empty block.
**Expected**: Row dict with summary showing "(empty rule)" or equivalent.
**Failure msg**: "Empty rules should display gracefully without error"

---

## Regression

### TC-23: YAML round-trip for new rule format
**Input**: Construct a `RuleBlock` with nested DECIDE, ASSERT, RETRACT, ACT, GAP, NOOP. Serialize to dict, deserialize back.
**Expected**: `original.to_dict() == deserialized.to_dict()`
**Failure msg**: "YAML round-trip must preserve all AST structure"

### TC-24: YAML round-trip for rule with variables
**Input**: `RuleBlock` with CHECK using instance=$u, ASSERT using instance=$u.
**Expected**: Round-trip preserves variable tokens.
**Failure msg**: "Variable tokens must survive YAML round-trip"

### TC-25: Existing non-rule tests pass unchanged
**Input**: Run full test suite after implementation.
**Expected**: All tests in test_fact_extractor, test_ontology_manager (non-rule parts), test_yaml_store (incident/ontology), test_models (Fact, Incident, OntologyProperty, Goal) pass without modification.
**Failure msg**: "Non-rule tests must not regress"
