# EES-00016 — Project Owner Assistant Decision Notes

## Origin
This work item originated from a brainstorming session critiquing the Proposed Facts and Proposed Rules output of the expert system. Four key observations were identified:

1. Rules only rule out — no clear resolution/stopping mechanism
2. No explicit goal declaration (solution to what problem?)
3. Noun/Property syntax inconsistencies in the display layer
4. CHANGE_STATE uses past-tense narrative text instead of typed values

This work item (EES-00016) addresses **observation 4** — the foundational layer. The ontology must declare typed properties with legal values before rules can use structured state transitions (EES-00017) or goals can be declared (EES-00018).

## Decomposition Rationale
The original discussion covered a full schema overhaul (typed ontology + structured rule outputs + goal declaration + termination). This was decomposed into three work items because:

- **EES-00016** (this item): Typed ontology — foundation layer, no dependencies
- **EES-00017**: Structured RuleOutput — depends on EES-00016 (needs typed properties to validate targets)
- **EES-00018**: Goal declaration & evaluation termination — depends on EES-00017 (goals use structured CHANGE_STATE)

Each is independently shippable and testable.

## Scope Decisions
- **Validation is advisory during LLM extraction**: The LLM may propose facts with values not yet in the ontology. We warn but don't block. Enforcement happens at confirm time.
- **Four types only**: `string`, `enum`, `bool`, `long`. No `float`, `date`, or complex types for now — YAGNI.
- **No GUI changes scoped here**: The ontology editor and fact table will adapt naturally since they read from `OntologyProperty.to_dict()`.
