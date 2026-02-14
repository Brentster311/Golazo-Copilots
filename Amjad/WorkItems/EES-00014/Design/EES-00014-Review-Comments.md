# EES-00014 — Review Comments

## Design Critique

1. **Approved** — scope is well-bounded: remove two redundant items.
2. **Backward compat**: Design correctly calls for `from_dict` to silently ignore `because`. Confirm `Rule.from_dict` uses `d.get("because", "")` pattern — just remove the kwarg, don't add explicit error on the key.
3. **Impact**: 8 capabilities affected (per registry). The test cases below cover the main paths. `cli-orchestration` and `rule-evaluation` are transitively affected — verify their tests still pass.
4. **Root cause in GUI**: The `_pending_root_cause` flow in `app.py` auto-saves LLM-identified root causes. Removing this means the LLM can no longer auto-populate root causes. Root causes will only come from `CHANGE_STATE` rule outputs or manual entry. This is the intended behavior per the user story.

## Risks Accepted
- Old YAML files with `because` fields: silently dropped on load — acceptable.
- `_confirm_root_cause` in `main.py` references `root_cause` on `LLMResponse` — must be updated.

## Architect Notes

### Architectural Alignment
- Pure removal — no new interfaces or contracts. Blast radius is contained to existing modules.
- All affected capabilities (8) are covered by existing test suites.

### Data Contract
- `Rule.to_dict()` will no longer emit `"because"`. Consumers reading Rule dicts should not depend on this key.
- `LLMResponse` will no longer carry `root_cause`. Any code using `llm_response.root_cause` must be updated.

### Backward Compatibility
- `Rule.from_dict`: The existing `d.get("because", "")` call will simply be removed from the kwargs. Old dicts with `"because"` keys are harmless — `from_dict` uses explicit `d.get()` for each field, so unknown keys are naturally ignored.
- `Incident.root_cause_identified`: Remains untouched (out of scope). Incidents can still record a root cause.

### Security / Privacy
- No impact. No new inputs, no new network calls.

### Rollback
- Git revert to prior commit. No data migration needed.
