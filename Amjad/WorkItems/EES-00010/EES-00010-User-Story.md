# EES-00010 — V2 Rule Grammar: Data Model & Engine

**Status**: BACKLOG

**User Story**
- **Title:** V2 Rule Grammar — Data Model & Engine (CHANGE_STATE / RULED_OUT / GAP with optional ELSE)
- **As a:** knowledge engineer
- **I want:** the data model and rule engine to support the v2 rule grammar (`IF <conditions> THEN CHANGE_STATE|RULED_OUT|GAP [ELSE CHANGE_STATE|RULED_OUT|GAP]`)
- **So that:** rules can express diagnostic branching with state mutations, eliminations, and knowledge gaps — and the engine evaluates both THEN and ELSE branches during forward chaining
- **Out of scope:**
  - LLM prompt changes (EES-00011)
  - GUI changes (EES-00012)
  - BECAUSE clause (deferred)
  - OR logic (decomposed into multiple rules)
  - Variable binding (existing feature, not changed)
- **Assumptions:**
  - **Assumption (explicit):** The existing `Fact`, `Rule`, `RuleConditions`, `RuleThen` models will be refactored in place rather than creating parallel types. Existing tests will be rewritten to match the new grammar.
  - **Assumption (explicit):** RULED_OUT and CHANGE_STATE outputs enter the working set as derived facts that downstream rules can match against.
  - **Assumption (explicit):** GAP is terminal — it does not enter the working set for chaining.
  - **Assumption (explicit):** ELSE is optional — when absent, no output is produced if conditions are not met.
- **Acceptance Criteria (bulleted, testable):**
  - A `Rule` can be constructed with `then` being one of CHANGE_STATE, RULED_OUT, or GAP, each carrying a descriptive string
  - A `Rule` can optionally have an `else_` branch of the same types
  - The rule evaluator fires the THEN branch when all conditions are met
  - The rule evaluator fires the ELSE branch when conditions are NOT met (and ELSE is present)
  - RULED_OUT outputs appear in the working set and can be matched by conditions of other rules
  - CHANGE_STATE outputs appear in the working set and can be matched by conditions of other rules
  - Rules serialize to/from YAML in the new format
- **Non-functional requirements:** All existing tests updated or replaced; no regressions
- **Telemetry / metrics expected:** N/A
- **Rollout / rollback notes:** This is a breaking change to the data model. Existing YAML rule files will need migration or re-extraction.
