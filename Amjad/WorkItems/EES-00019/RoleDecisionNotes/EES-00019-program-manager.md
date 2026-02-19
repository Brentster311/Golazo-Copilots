# EES-00019 - Program Manager Decision Notes

## Design Approach
Chose a 4-phase implementation (AST Model, Evaluator, LLM Integration, GUI) that mirrors the data flow: define the grammar first, make it executable, then wire it into extraction and display. Each phase is independently testable.

## Key Decisions

### 1. New AST classes vs. extending existing Rule/RuleConditions/RuleOutput
**Decision**: New classes, remove old ones.
**Rationale**: The old grammar uses `RuleConditions` (flat AND/OR of facts) and `RuleOutput` (kind + description). The new grammar has nested blocks with CHECK/DECIDE/ASSERT/RETRACT. These are fundamentally different structures - wrapping one in the other creates confusion. Clean break matches user's "delete and re-extract" directive.

### 2. Single evaluator vs. keeping both old and new
**Decision**: New `ASTEvaluator` replaces `RuleEvaluator`.
**Rationale**: The old evaluator's forward-chaining loop assumes flat conditions and single-output branches. The new grammar has nested DECIDE blocks and multiple statements per block. The evaluation logic is different enough to warrant a new class. The old class can be removed since there are no old-format rules to evaluate.

### 3. Reuse Fact as working memory unit
**Decision**: Yes, reuse `Fact`.
**Rationale**: `Fact` already has noun/instance/property/operator/value and `match_key()` for O(1) lookup. CHECK needs to test against these fields. ASSERT/RETRACT add/remove these. No benefit to a new class.

### 4. YAML AST schema design
**Decision**: Each statement is a dict keyed by its keyword. Blocks are lists.
**Rationale**: This maps directly to the grammar. The LLM produces JSON via tool calls, which converts 1:1 to YAML. No ambiguity in parsing.

### 5. Phased delivery within single work item
**Decision**: 4 phases but shipped as one work item (user's explicit request).
**Rationale**: The phases are a sequencing aid for implementation, not separate deliveries. All 4 phases must land together for the system to function end-to-end.

## Capability Impact
All 9 capabilities are affected (8 directly, 1 transitively). This is expected for a grammar replacement. The highest-risk capabilities are:
- **data-models**: New AST classes replace Rule/RuleConditions/RuleOutput
- **rule-evaluation**: New evaluator with block-based execution
- **fact-extraction**: New system prompt and tool schema
- **gui**: New rule display format

## Risk Assessment
Primary risk is LLM compliance - will it produce structurally valid AST? Mitigated by:
1. Concrete examples in system prompt
2. Structural validation with descriptive error messages returned to LLM
3. Max 20 turns for self-correction
4. The grammar is simpler than the old one (no free-text descriptions to get wrong)
