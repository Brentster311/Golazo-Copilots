# EES-00010 — Architect Decision Notes

## Impact Analysis
- 3 directly affected capabilities: data-models, rule-evaluation, rule-generation
- 5 transitively affected: yaml-persistence, fact-extraction, ontology-management, cli-orchestration, gui
- EES-00010 covers direct impacts only. Transitive impacts deferred to EES-00011 (extraction) and EES-00012 (GUI).

## Architecture Decisions
- `RuleOutput` as simple `kind` + `description` value object — minimal coupling
- Derived facts use fixed `Fact(noun=kind, ...)` schema — known contract for chaining
- `else` (not `else_`) in YAML serialization — Python keyword workaround stays internal
- `RootCause` dataclass left in place (unused by v2) — cleanup deferred

## Approved
No architectural concerns. Design proceeds as-is.
