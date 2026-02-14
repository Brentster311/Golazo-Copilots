# EES-00014 — Capability Impact

## Directly Affected
- **data-models**: Remove `because` from Rule, `root_cause` from LLMResponse
- **fact-extraction**: Remove `set_root_cause` tool, update system prompt, remove `because` from submit_rule
- **gui**: Remove "because" column, remove `_pending_root_cause` flow

## Transitively Affected
- **yaml-persistence**: Rule serialization changes (no `because` key emitted)
- **rule-generation**: No direct changes needed
- **ontology-management**: No direct changes needed
- **cli-orchestration**: Remove `_confirm_root_cause` usage
- **rule-evaluation**: No direct changes needed
