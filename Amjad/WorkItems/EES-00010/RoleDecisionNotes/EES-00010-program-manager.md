# EES-00010 — Program Manager Decision Notes

## Key Design Choices
- `RuleOutput` with `kind` + `description` is the simplest model that covers all three entity types
- Outputs map to `Fact` for working-set matching — reuses existing infrastructure
- GAP is terminal (not added to working set) to prevent nonsensical chaining
- ELSE is `None` by default — backward compatible for rules that don't need it
- AND-only conditions — OR was already decomposed in v1

## Operational Impact
- Breaking change to YAML format — existing rules need re-extraction (EES-00011)
- No on-call or runtime impact (dev tool)

## Open Questions
- None — grammar was fully designed in brainstorm session
