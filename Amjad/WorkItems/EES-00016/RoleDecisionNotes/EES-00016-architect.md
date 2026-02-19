# EES-00016 — Architect Decision Notes

## Capability Impact
Impact analysis shows 8 capabilities affected (2 direct, 6 transitive). All changes are additive — no existing contracts broken. Transitive consumers are unaffected until EES-00017 explicitly introduces structured CHANGE_STATE targets.

## Architectural Decision
Approved extension of `OntologyProperty` dataclass. No new models, no new modules, no new coupling.

## Key Contracts
- `OntologyProperty.validate_value(v: str) -> bool` — pure function, no side effects
- `OntologyManager.validate_fact(fact: Fact) -> list[str]` — returns error list, never raises
- Both are opt-in: callers that don't use them are unaffected
