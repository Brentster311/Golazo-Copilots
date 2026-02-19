# EES-00019 - Project Owner Assistant Decision Notes

## Request Summary
The user provided a formal language specification for a minimal explainable expert system. The current rule grammar (IF/THEN/ELSE with CHANGE_STATE/RULED_OUT/GAP) is not converging because:
1. No ontology with typed values exists - the LLM invents free-text values
2. CHANGE_STATE rules produce pseudo-facts from description strings, not real state transitions
3. No goal declared - the engine does not know when to stop

Rather than patching these gaps incrementally (as EES-00016/17/18 attempted at the engine layer), the user wants to replace the entire rule grammar with a structurally sound language that enforces deterministic evaluation.

## Clarification Answers (from user)
| Question | Answer |
|----------|--------|
| Interface | Engine changes + GUI updates |
| Scope | Full spec in one work item |
| Data persistence | Keep YAML |
| Migration | Delete existing rules, re-extract |

## Scope Decision
The user explicitly requested the full language spec in a single work item despite the role guidance preferring smaller scope. This is respected because:
- The language is small (10 keywords, ~10 grammar productions)
- The parser, evaluator, and serializer are tightly coupled - shipping one without the others is not useful
- The LLM prompt must match the grammar for extraction to work
- The GUI display of rules depends on the AST structure

Acceptance criteria are at the 7-item maximum. If implementation reveals the need to split, that will be escalated.

## Key Design Choices Made
1. **Clean break** - No backward compatibility with old IF/THEN/ELSE format. Rules R-001 through R-004 deleted.
2. **YAML AST** - Rules stored as YAML that mirrors the grammar tree, not as raw text files.
3. **No grammar toolkit** - Parser is pure Python to avoid new dependencies.
4. **Working memory = Facts** - CHECK reads facts, ASSERT/RETRACT modify facts. The existing Fact model is reused as the working memory representation.
5. **ACT = trace only** - Side effects are recorded but do not change working memory.
6. **Fixed-point termination** - Same model as current evaluator but driven by the new grammar ASSERT/RETRACT semantics.

## Relationship to Prior Work Items
- EES-00016 (typed ontology): Properties with validate_value() still exist and can be used by CHECK/ASSERT. Not replaced.
- EES-00017 (structured RuleOutput): Replaced by ASSERT/RETRACT/ACT. The RuleOutput class becomes unnecessary for new rules.
- EES-00018 (goal termination): Goal fields on OntologyProperty remain. The new evaluator can check goal convergence after each iteration.
- EES-00013 (agentic extraction): The FactExtractor is updated with new system prompt and tool schema, not replaced.
