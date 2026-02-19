# EES-00018 Program Manager Notes

## Key Design Decisions
1. **Goal on OntologyProperty, not Incident**: Goals are domain-level (ontology) not incident-level. `Incident($inc).rootCause` is a goal for all incidents of that type.
2. **Optional goal parameter**: `evaluate(input_facts, goal=None)` — fully backward compatible. No goal = today's behavior.
3. **Three-valued goal_status**: `resolved` / `escalated` / `in_progress` covers all outcomes. `None` when no goal declared.
4. **Separate Goal dataclass**: Decouples the evaluator from the ontology lookup — the evaluator receives a simple `Goal` object, doesn't need to know about `OntologyProperty`.
5. **Termination after full iteration**: Don't stop mid-iteration — let all rules in the current pass fire, *then* check goal status. This prevents order-dependent termination.

## Scope Boundary
- Goal declaration in ontology YAML — yes
- Goal checking in evaluator — yes
- GUI goal display — out of scope (follow-up)
- Multi-goal evaluation — out of scope
