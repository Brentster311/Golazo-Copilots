# EES-00019 Capability Impact Analysis

## Impact Summary
**7 files -> 8 capabilities directly affected, 1 transitively affected**

## Directly Affected Capabilities

### 1. data-models
- **Files**: `src/ees/models.py`
- **Current contract**: Exports `Fact`, `Rule`, `RuleConditions`, `RuleOutput`, `RuleThen`, `Incident`, `OntologyNoun`, `OntologyProperty`, `Goal`, `EvaluationResult`, `LLMResponse`
- **Change**: `Rule`, `RuleConditions`, `RuleOutput`, `RuleThen` removed. New AST classes added: `Block`, `RuleBlock`, `CheckExpr`, `DecideStmt`, `AssertStmt`, `RetractStmt`, `ActStmt`, `NoopStmt`, `GapStmt`
- **Contract impact**: BREAKING - all consumers of Rule/RuleConditions/RuleOutput must migrate. `Fact`, `Incident`, `OntologyNoun`, `OntologyProperty`, `Goal`, `EvaluationResult` unchanged.

### 2. rule-evaluation
- **Files**: `src/ees/rule_evaluator.py`
- **Current contract**: `RuleEvaluator(rules: list[Rule]).evaluate(input_facts, goal) -> EvaluationResult`
- **Change**: Replaced with `ASTEvaluator(rules: list[RuleBlock]).evaluate(facts, goal) -> EvaluationResult`
- **Contract impact**: BREAKING - new input type. `EvaluationResult` output is preserved (same fields including `goal_status`).

### 3. fact-extraction
- **Files**: `src/ees/fact_extractor.py`
- **Current contract**: `FactExtractor.extract(text, ontology) -> LLMResponse` where `LLMResponse.rules: list[Rule]`
- **Change**: `LLMResponse.rules` becomes `list[RuleBlock]`. System prompt updated. `submit_rule` tool schema changed. `_handle_get_ontology()` enriched with types/values.
- **Contract impact**: BREAKING on rules type. `LLMResponse.facts` unchanged.

### 4. rule-generation
- **Files**: `src/ees/rule_generator.py`
- **Current contract**: `RuleGenerator.filter_rules(rules, facts) -> list[Rule]` with dedup
- **Change**: Dedup logic needs rewrite for AST-based rules or removal.
- **Contract impact**: BREAKING - input/output types change. May be simplified since AST structural equality is straightforward.

### 5. yaml-persistence
- **Files**: `src/ees/yaml_store.py`
- **Current contract**: `save_rule(rule) / load_rules() -> list[Rule]`
- **Change**: `save_rule(rule: RuleBlock) / load_rules() -> list[RuleBlock]`
- **Contract impact**: BREAKING on rule I/O. Incident/ontology/root-cause methods unchanged.

### 6. gui
- **Files**: `src/ees/gui/app.py`, `src/ees/gui/adapters.py`
- **Current contract**: `rules_to_rows(rules: list[Rule]) -> list[dict]`
- **Change**: `rules_to_rows(rules: list[RuleBlock]) -> list[dict]` with new display format
- **Contract impact**: BREAKING on input type. Output dict keys may change.

## Transitively Affected Capabilities

### 7. ontology-management
- **Files**: `src/ees/ontology_manager.py`
- **Current contract**: `OntologyManager.validate_fact(fact)`, `update_from_facts(facts)`
- **Change**: No direct changes. `validate_fact` is still called (by CHECK validation). `update_from_facts` still called for confirmed facts.
- **Contract impact**: COMPATIBLE - no interface changes needed.

### 8. cli-orchestration
- **Files**: `src/ees/main.py`
- **Current contract**: Uses `Rule`, `RuleEvaluator`, `RuleGenerator` throughout
- **Change**: Must update to use new AST types. All rule-related functions need rewrite.
- **Contract impact**: BREAKING - internal rewiring required.

### 9. incident-loading
- **Files**: `src/ees/incident_loader.py`
- **Current contract**: Loads incident text files, no rule dependency
- **Change**: None
- **Contract impact**: COMPATIBLE - no changes needed.

## New Public Interfaces
| Interface | Module | Description |
|-----------|--------|------------|
| `RuleBlock` | models.py | Top-level rule AST node |
| `Block` | models.py | List of statements |
| `DecideStmt` | models.py | CHECK + two blocks (then/else) |
| `AssertStmt` | models.py | Adds fact to working memory |
| `RetractStmt` | models.py | Removes fact from working memory |
| `ActStmt` | models.py | External side-effect (trace only) |
| `NoopStmt` | models.py | Explicit no-op |
| `GapStmt` | models.py | Unknown reasoning marker |
| `CheckExpr` | models.py | Fact expression producing boolean |
| `parse_rule(d: dict) -> RuleBlock` | models.py or parser.py | Validates and parses YAML dict to AST |
| `ASTEvaluator` | rule_evaluator.py | New evaluator for AST rules |

## Removed Public Interfaces
| Interface | Module | Replacement |
|-----------|--------|------------|
| `Rule` | models.py | `RuleBlock` |
| `RuleConditions` | models.py | `Block` + `DecideStmt` |
| `RuleOutput` | models.py | `AssertStmt` / `RetractStmt` / `ActStmt` / `GapStmt` |
| `RuleThen` | models.py | Removed (was already deprecated) |
| `RuleEvaluator` | rule_evaluator.py | `ASTEvaluator` |
