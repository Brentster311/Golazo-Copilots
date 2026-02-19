# EES-00019: Structured Expert System Language — Full Grammar Implementation

**Status**: IMPLEMENTED

**User Story**

- **Title**: Replace free-text rule grammar with a minimal, deterministic expert system language
- **As a**: knowledge engineer processing incidents in the EES GUI
- **I want**: the extraction pipeline, rule engine, and GUI to use a formal language with keywords `RULE`, `BEGIN`/`END`, `CHECK`, `DECIDE`, `ASSERT`, `RETRACT`, `ACT`, `NOOP`, and `GAP` — so that extracted rules are structurally valid, reasoning is explicit and traceable, and forward-chaining evaluation converges to a stable working memory
- **So that**: the system produces deterministic diagnostic results instead of free-text descriptions that never converge, and every step of reasoning is explainable via a trace

- **Out of scope**:
  - Multi-language support or custom keyword aliases
  - Visual rule editor (drag-and-drop) — the GUI displays rules, it doesn't graphically author them
  - Backward compatibility with old IF/THEN/ELSE rule format (old rules will be deleted)
  - Ontology typed values / goal termination wiring (EES-00016/17/18 engine features remain, but the new language replaces the grammar layer above them)

- **Assumptions**:
  - **Assumption (explicit)**: The language spec provided is the canonical grammar. No keywords beyond `RULE`, `BEGIN`, `END`, `CHECK`, `DECIDE`, `ASSERT`, `RETRACT`, `ACT`, `NOOP`, `GAP` are introduced.
  - **Assumption (explicit)**: Existing rules (R-001 through R-004) in `data/rules/` will be deleted. The knowledge base starts fresh — rules will be re-extracted from incidents using the new language.
  - **Assumption (explicit)**: The AST is serialized to YAML for persistence (same `data/rules/` directory, new schema). The YAML structure mirrors the grammar tree.
  - **Assumption (explicit)**: The LLM system prompt and tool schema in `FactExtractor` are updated so the model emits rules conforming to this grammar. The `submit_rule` tool enforces structural validity.
  - **Assumption (explicit)**: `CHECK` reads a fact from working memory (a Noun(instance).Property expression) and produces a boolean. `DECIDE` branches on that boolean: first block = condition met, second block = condition not met.
  - **Assumption (explicit)**: `ASSERT` adds a fact to working memory. `RETRACT` removes a fact. These are the only memory-modifying statements.
  - **Assumption (explicit)**: `ACT` represents an external side-effect (e.g., "escalate to Exchange team"). At evaluation time, ACT is recorded in the trace but does not modify working memory.
  - **Assumption (explicit)**: `GAP` marks unknown or implicit reasoning — "we don't know why, but we need to investigate." It is a terminal signal in a branch.
  - **Assumption (explicit)**: Forward chaining iterates: evaluate all rules → apply ASSERT/RETRACT → repeat until working memory is stable (fixed-point). This replaces the current per-rule firing model.
  - **Assumption (explicit)**: The GUI already has Proposed Facts and Proposed Rules tables. The Proposed Rules table will display the new language structure (keywords, nested blocks) instead of flat Conditions/Then/Else columns.

- **Acceptance Criteria (bulleted, testable)**:
  - Given a YAML-serialized rule using the new grammar, the parser produces a valid AST with `RULE`, `Block`, `StmtList`, and `Stmt` nodes — and rejects input with unknown keywords or structurally invalid nesting
  - The forward-chaining evaluator accepts an AST rule base and a working memory (list of Facts), executes CHECK/DECIDE/ASSERT/RETRACT/ACT/NOOP/GAP, and terminates when working memory stabilizes (no new ASSERT/RETRACT changes)
  - Evaluation produces an ordered reasoning trace: each step records the rule, the statement type, the CHECK result (if applicable), and any ASSERT/RETRACT applied
  - The `FactExtractor` system prompt and `submit_rule` tool schema are updated so the LLM emits rules in the new grammar; `submit_rule` validates structural conformance before accepting
  - The GUI Proposed Rules table displays rules in the new structure, showing keywords (`CHECK`, `DECIDE`, `ASSERT`, etc.) and nested block structure
  - Rules serialize to YAML and deserialize back to an identical AST (round-trip fidelity)
  - All existing tests pass or are updated; new tests cover: parsing valid/invalid input, evaluation convergence, trace correctness, YAML round-trip, and LLM tool validation

- **Non-functional requirements**: No new external dependencies beyond what's already in `pyproject.toml`. Parser and evaluator must be pure Python (no grammar toolkits like PLY/ANTLR). Evaluation must terminate (fixed-point or max-iteration guard).
- **Telemetry / metrics expected**: Extraction logs include: number of rules emitted, number rejected by structural validation, iteration count to convergence.
- **Rollout / rollback notes**: Breaking change — deletes `data/rules/R-001.yaml` through `R-004.yaml`. The `data/incidents/INC-001.yaml` is retained. Old `Rule`, `RuleConditions`, `RuleOutput` model classes are replaced or wrapped by the new AST. Rollback = git revert.
