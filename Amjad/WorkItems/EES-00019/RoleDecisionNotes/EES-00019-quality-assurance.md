# EES-00019 - Quality Assurance Decision Notes

## Review Summary
Design is implementable with 2 medium-priority clarifications needed (RC-1: DECIDE semantics, RC-2: RETRACT matching). No blocking issues.

## Design Review Decisions
- RC-1 (DECIDE/CHECK coupling): Recommended that DecideStmt contains the check expression directly. A bare CHECK without DECIDE is valid but acts as a trace-only observation.
- RC-2 (RETRACT matching): Recommended match on (noun, instance, property) only, removing all matching facts regardless of operator/value. No-match is a no-op.
- RC-3 (Variables): Carry forward from EES-00009. Not a new requirement, just needs to be accounted for.
- RC-4 (Rule ordering): Lexicographic by rule_id. Deterministic.
- RC-5 (Old test cleanup): Old rule tests rewritten, non-rule tests untouched.
- RC-6 (GUI display): Summary column + detail panel rather than multi-line Treeview rows.

## Test Strategy Decisions
- 25 test cases across 4 phases, mapped to all 7 acceptance criteria
- Phase 1 (parsing): 7 tests covering valid structures, nesting, and rejection of invalid input
- Phase 2 (evaluation): 9 tests covering branching, memory mutation, convergence, traces, and goal termination
- Phase 3 (LLM): 4 tests covering tool validation and ontology enrichment
- Phase 4 (GUI): 2 tests covering adapter output
- Regression: 2 round-trip tests + 1 suite-wide regression check

## Capability Coverage
All 9 capabilities have test coverage:
- data-models: TC-01 through TC-07 (parsing), TC-23/TC-24 (round-trip)
- rule-evaluation: TC-08 through TC-16
- fact-extraction: TC-17 through TC-20
- gui: TC-21, TC-22
- yaml-persistence: TC-23, TC-24
- ontology-management: TC-20 (get_ontology enrichment)
- cli-orchestration: Covered by TC-25 (regression) - main.py must be updated
- rule-generation: Affected but old dedup logic may not apply to AST rules. Flagged as potential gap - if rule deduplication is needed for new format, it should be a separate work item.
- incident-loading: Not affected by this change. Covered by TC-25 regression.
