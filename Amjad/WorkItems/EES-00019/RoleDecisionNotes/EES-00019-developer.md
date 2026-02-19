# EES-00019 Developer Decision Notes

## Summary
Implemented the structured expert system language (10 keywords: RULE, BEGIN, END, CHECK, DECIDE, ASSERT, RETRACT, ACT, NOOP, GAP) in 4 TDD phases. All 372 tests pass (28 new + 344 existing unchanged).

## Implementation Decisions

### D-1: AST classes appended to `models.py`
**Decision**: Added 9 new dataclasses (`CheckExpr`, `AssertStmt`, `RetractStmt`, `ActStmt`, `NoopStmt`, `GapStmt`, `DecideStmt`, `Block`, `RuleBlock`) and `parse_rule()` to the existing `models.py` rather than creating a new file.
**Rationale**: Design doc proposed either approach. Keeping in `models.py` maintains the single-import convention used by all other modules.

### D-2: `ASTEvaluator` added to `rule_evaluator.py` alongside `RuleEvaluator`
**Decision**: Legacy `RuleEvaluator` kept intact; new `ASTEvaluator` added below it.
**Rationale**: Existing tests depend on `RuleEvaluator`. Clean break for new code while maintaining backward compatibility. Old class can be removed in a future cleanup work item.

### D-3: `_handle_submit_rule_ast` as separate static method
**Decision**: Added `_handle_submit_rule_ast()` as a new static method on `FactExtractor` instead of modifying `_handle_submit_rule()`.
**Rationale**: The old method handles legacy `Rule` objects; the new one handles `RuleBlock` AST objects. Both can coexist until the extraction pipeline is fully wired to the new grammar.

### D-4: `_handle_get_ontology` updated in-place
**Decision**: Modified the existing `_handle_get_ontology()` to serialize full property details (type, values, default, is_goal, initial, terminal) instead of just property names.
**Rationale**: This directly fixes the convergence root cause (LLM got no type/value info). The change is backward-compatible — the JSON now has richer objects where it previously had strings.

### D-5: `ast_rules_to_rows` produces summary column (RC-6)
**Decision**: GUI adapter uses a single `summary` string per rule instead of multi-column conditions/then/else layout.
**Rationale**: Per QA Review Comment RC-6, the nested DECIDE structure doesn't map well to flat columns. A keyword summary (CHECK ... | THEN: ... | ELSE: ...) provides readable overview.

### D-6: Deterministic rule execution order
**Decision**: `ASTEvaluator` sorts rules by `rule_id` before execution (RC-4 requirement).
**Rationale**: Ensures reproducible evaluation traces regardless of rule insertion order.

### D-7: Working memory as `dict[tuple, Fact]`
**Decision**: Changed from set-of-keys to dict-of-keys→Fact for working memory in `ASTEvaluator`.
**Rationale**: RETRACT needs to find and remove facts by (noun, instance, property) prefix. Using a dict allows O(n) scan with removal, and ASSERT can overwrite in-place.

### D-8: Deleted old data rules
**Decision**: Deleted `data/rules/R-001.yaml` through `R-004.yaml`.
**Rationale**: Per user directive and design doc — clean break, these used description-string pseudo-facts that can't be auto-migrated.

## Files Changed
| File | Change |
|------|--------|
| `src/ees/models.py` | Added 9 AST dataclasses, `parse_rule()`, imported `ParseError` |
| `src/ees/exceptions.py` | Added `ParseError` class |
| `src/ees/rule_evaluator.py` | Added `ASTEvaluator` class (230 lines), expanded imports |
| `src/ees/fact_extractor.py` | Added `_handle_submit_rule_ast()`, updated `_handle_get_ontology()`, imported `parse_rule`/`ParseError`/`RuleBlock` |
| `src/ees/gui/adapters.py` | Added `ast_rules_to_rows()`, `_summarize_stmt()`, expanded imports |
| `data/rules/R-001..R-004.yaml` | Deleted |

## Test Files Created
| File | Tests | Phase |
|------|-------|-------|
| `tests/test_ast_models.py` | 10 tests (TC-01 through TC-07, TC-23, TC-24) | Phase 1 |
| `tests/test_ast_evaluator.py` | 10 tests (TC-08 through TC-16) | Phase 2 |
| `tests/test_ast_llm.py` | 5 tests (TC-17 through TC-20) | Phase 3 |
| `tests/test_ast_gui.py` | 3 tests (TC-21, TC-22) | Phase 4 |

## Test Results
- **372 total tests passed** (28 new + 344 existing)
- **0 failures, 0 errors**
- Full regression clean — no existing test was modified

## What's NOT Wired Yet
The following are implemented and tested but not yet wired into the main extraction/evaluation flow:
1. System prompt update (still uses old IF/THEN/ELSE grammar) — separate work item
2. `submit_rule` tool schema in `_TOOLS` list — still uses old format
3. `main.py` CLI still instantiates `RuleEvaluator` with old `Rule` objects
4. GUI `app.py` still calls `rules_to_rows()` not `ast_rules_to_rows()`

These integrations should be done in focused follow-up work items to keep changes auditable and reversible.
