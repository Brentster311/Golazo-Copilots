# EES-00017 Architect Notes

## Architectural Review
- Flat optional fields on `RuleOutput` — approved. Consistent with project pattern. No inner class needed.
- `to_fact()` polymorphism (structured vs. legacy) is transparent to consumers.
- `validate()` reuses `OntologyManager` — no new validation framework.

## Capability Impact
- 8 capabilities transitively affected via `models.py`
- All changes additive (new optional fields, default None)
- No existing contracts broken

## No New User Stories Needed
- Design is architecturally sound. No scope/behavior changes beyond user story.
