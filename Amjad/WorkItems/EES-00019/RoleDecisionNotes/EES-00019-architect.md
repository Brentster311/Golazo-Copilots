# EES-00019 - Architect Decision Notes

## Architectural Alignment
The new grammar replaces the rule subsystem while preserving the fact/ontology/incident subsystem. This is a clean vertical cut through the architecture:
- **Unchanged**: Fact model, Incident model, OntologyNoun/Property, YamlStore (incident/ontology paths), OntologyManager, IncidentLoader
- **Replaced**: Rule model -> AST model, RuleEvaluator -> ASTEvaluator, RuleGenerator -> simplified or removed
- **Updated**: FactExtractor (prompt + tool schema), GUI adapters, CLI main.py

## Key Architectural Decisions

### 1. AST dataclasses vs. visitor pattern
**Decision**: Plain dataclasses with `to_dict()`/`from_dict()`. No visitor pattern.
**Rationale**: The AST has ~8 node types with simple dispatch (match on `kind` field). A visitor adds complexity without benefit at this scale. If the grammar grows beyond 15 node types, revisit.

### 2. Evaluator architecture
**Decision**: Single `ASTEvaluator` class with recursive `_execute_block()` and `_execute_stmt()` methods.
**Rationale**: Blocks contain statements, statements can contain blocks (DECIDE). Recursive execution naturally follows the grammar. Working memory is passed by reference.

### 3. Working memory representation
**Decision**: `set[tuple]` of match keys (same pattern as current evaluator) + `list[Fact]` for ordered access.
**Rationale**: O(1) lookup for CHECK, O(n) scan for RETRACT pattern matching. This is the same dual-structure approach used in the current `RuleEvaluator`.

### 4. parse_rule() placement
**Decision**: In `models.py` alongside the AST classes.
**Rationale**: The parser is tightly coupled to the AST types. Keeping them together makes imports simple. If the file gets too large, extract to `parser.py`.

### 5. LLMResponse.rules type change
**Decision**: Change `rules: list[Rule]` to `rules: list[RuleBlock]` directly, no Union type.
**Rationale**: Clean break. No old code should be producing `Rule` objects after this change.

## Contract Compatibility
See EES-00019-Capability-Impact.md for full analysis. 6 breaking changes, 3 compatible. All breaking changes are in the rule subsystem which is being replaced by design.

## Security Review
No concerns. No new external inputs, no code execution, no network calls beyond existing Azure OpenAI integration. Parser validates structural correctness only - no injection vectors.
