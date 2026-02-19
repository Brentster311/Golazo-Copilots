# EES-00019 Design Review Comments

## Overall Assessment
The design is clear, well-structured, and addresses the root convergence problem directly. The 4-phase approach is sound. The following items need attention before implementation.

## Review Items

### RC-1: DECIDE semantics - CHECK is embedded, not separate (Medium)
The grammar says `Stmt -> CHECK Decision` where `Decision -> DECIDE Block Block`. This means CHECK and DECIDE are coupled: you CHECK something, then DECIDE based on that result. But the design doc's FR-1 lists `CheckStmt` and `DecideStmt` as separate classes. The AST should model this as `DecideStmt` containing a CHECK expression plus two blocks, not as two independent statement types. A standalone CHECK with no DECIDE has no effect (it reads memory and discards the result).

**Recommendation**: `DecideStmt` should contain the check expression directly. A bare `CHECK` (without DECIDE) should still be valid per the grammar but is effectively a NOOP that records a trace entry.

### RC-2: RETRACT matching semantics undefined (Medium)
The design says RETRACT "removes a fact from working memory" but does not specify how matching works. Does RETRACT require exact match on all 5 fields (noun, instance, property, operator, value)? Or does it match on a subset (e.g., noun+property)? What happens if the fact does not exist?

**Recommendation**: RETRACT matches on (noun, instance, property) only - it removes ALL facts for that noun/instance/property regardless of operator/value. If no match, it is a no-op (recorded in trace as "no match").

### RC-3: Variable binding in CHECK/ASSERT/RETRACT (Low)
The existing system supports variables like `$u`, `$p` in rules (EES-00009). The design does not address whether the new grammar supports variables. The YAML example uses `$u` but there is no mention of binding semantics.

**Recommendation**: Carry forward the variable binding from the existing evaluator. Variables in CHECK bind on first match; subsequent references in ASSERT/RETRACT within the same DECIDE block use the bound value. Document this in the design.

### RC-4: Rule ordering and priority (Low)
The design says "execute all rules sequentially" but does not specify what "sequentially" means when rules are loaded from separate YAML files. Is it alphabetical by rule_id? Load order?

**Recommendation**: Rules execute in rule_id sort order (lexicographic). This is deterministic and matches the current behavior.

### RC-5: Interaction with existing EES-00016/17/18 code (Low)
The design says "remove old Rule/RuleConditions/RuleOutput" but these classes are used in 14+ test files and across multiple capabilities. The design should clarify what happens to the old test infrastructure.

**Recommendation**: Old test files for rule evaluation, rule generation, and model serialization are rewritten for the new AST. Tests for Fact, Incident, Ontology, YamlStore (incidents/ontology) are untouched.

### RC-6: GUI multi-line display in Treeview (Low)
The design says the Proposed Rules table shows "indented keyword trees." Tkinter Treeview rows are single-line. Multi-line display requires either: (a) one row per statement with indentation, or (b) a separate detail panel.

**Recommendation**: Use one Treeview row per rule with a summary column (e.g., "CHECK User.adminRole DECIDE [2 stmts] [1 stmt]"), and a detail panel or tooltip for the full tree.

## Capability Coverage Check
All 9 capabilities are affected. The test strategy covers data-models, rule-evaluation, fact-extraction, and gui adapters. Missing explicit coverage for:
- **yaml-persistence**: Rule serialization is covered by round-trip tests, but ontology/incident persistence regression needs explicit mention.
- **cli-orchestration**: `main.py` uses old `Rule` and `RuleEvaluator`. Needs update or the CLI path becomes broken.

## Summary
No blocking issues. RC-1 (DECIDE semantics) and RC-2 (RETRACT matching) should be resolved before implementation. The rest are low-risk and can be handled during development.

---

## Architect Notes

### AN-1: Module boundary - keep AST in models.py or new file?
**Decision**: Add AST classes to `models.py` alongside `Fact`, `Incident`, etc. The file is already 570 lines; the new classes add ~200 lines. If it exceeds 1000 lines, split into `ast_models.py` with re-exports from `models.py` for backward compat.

### AN-2: EvaluationResult contract preservation
The `EvaluationResult` dataclass is kept intact. Its `fired_rules` field changes type from `list[Rule]` to `list[RuleBlock]`. The `outputs` field is replaced by the trace (list of trace entries). The `goal_status` field is unchanged. The backward-compat properties (`root_causes`, `ruled_out`, `gap_rules`) are removed since the old output model is gone.

### AN-3: Error handling contract
`parse_rule()` raises a new `ParseError` (subclass of `EESError`) with a descriptive message. The evaluator does not raise on invalid AST - it trusts the parser. If somehow an invalid node reaches the evaluator, it logs a warning and skips the statement.

### AN-4: Security review
No new attack surface. The parser only accepts dict input from YAML deserialization or LLM tool calls (which are already JSON-parsed). No eval(), no exec(), no dynamic code generation. Working memory is in-process only.

### AN-5: Blast radius
6 of 9 capabilities have BREAKING changes. This is expected for a grammar replacement. Rollback is git revert. The blast radius is contained to the rule subsystem - incident loading, ontology management, and fact/incident persistence are unaffected.
