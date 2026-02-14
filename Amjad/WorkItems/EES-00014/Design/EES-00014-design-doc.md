# EES-00014 Design Doc — Remove `because` and `set_root_cause`

## Summary
Remove the `because` field from the `Rule` dataclass and the `set_root_cause` tool from the LLM extractor. Both are redundant with the v2 grammar where root cause identification is expressed through `CHANGE_STATE` rule outputs.

## Problem Statement
The codebase still contains two v1 holdovers:
1. `Rule.because` — a free-text explanation field on every rule
2. `set_root_cause` — a separate LLM tool for naming a root cause

These conflict with the v2 grammar design where rules are self-documenting via `IF <conditions> THEN CHANGE_STATE|RULED_OUT|GAP [ELSE ...]`. The `because` field is semantically redundant (the THEN/ELSE outputs describe what the rule concludes), and `set_root_cause` is redundant with `CHANGE_STATE` outputs.

## Business Case
- Simplifies the tool schema sent to the LLM (fewer tokens, clearer contract)
- Eliminates confusing dual paths for root cause identification
- Cleans up GUI (removes a column that duplicates information already in the THEN output)

## Stakeholders
- Developer (Brent) — sole user

## Functional Requirements
1. Remove `because` field from `Rule` dataclass
2. Remove `because` from `submit_rule` tool schema
3. Remove `set_root_cause` tool definition, handler, and dispatch
4. Remove `root_cause` field from `LLMResponse`
5. Update system prompt to not reference `set_root_cause()` or `because`
6. Remove "because" column from KB rules treeview
7. Remove "Because:" from rule detail dialog
8. Remove `_pending_root_cause` logic from `app.py` extraction flow

## Non-functional Requirements
- `Rule.from_dict` silently ignores `because` key in old data
- `LLMResponse` construction tolerates missing `root_cause` kwarg

## Proposed Approach
1. **models.py**: Remove `because` from `Rule`, drop from `to_dict`/`from_dict`. Remove `root_cause` from `LLMResponse`.
2. **fact_extractor.py**: Remove tool from `_TOOLS` list, remove `_handle_set_root_cause`, remove dispatch branch, remove `root_cause` variable from extract loop, update system prompt, remove `because` from `submit_rule` schema + `_handle_submit_rule`, remove status label.
3. **adapters.py**: Remove `because` from `rules_to_rows`.
4. **app.py**: Remove "because" column from KB treeview, remove from detail dialog, remove `_pending_root_cause` logic.
5. **tests**: Update all tests that reference `because`, `set_root_cause`, or `root_cause` on `LLMResponse`.

## Alternatives Considered
- Keep `because` as optional — rejected because it's truly redundant with v2 outputs.
- Keep `set_root_cause` but make it optional — rejected because CHANGE_STATE covers it.

## Risks & Mitigations
- **Old data files**: Mitigated by `from_dict` silently ignoring removed fields.
- **Large test change surface**: Mitigated by systematic find-and-remove approach.

## Dependencies
None. Pure internal cleanup.

## Migration / Rollback
- Existing YAML files with `because` fields will load without error (field is ignored).
- Git revert to prior commit if needed.

## Test Strategy
- Update all existing tests to remove `because`/`root_cause` references
- Verify all 268 tests still pass
- No new tests needed (this is removal, not addition)
