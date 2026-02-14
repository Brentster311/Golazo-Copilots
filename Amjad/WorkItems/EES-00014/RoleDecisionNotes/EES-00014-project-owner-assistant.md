# EES-00014 — Project Owner Assistant Notes

## Decisions

1. **Scope**: Remove two specific items — `because` (Rule field + tool schema) and `set_root_cause` (tool + LLMResponse field). The broader Root Causes management (GUI tab, store, RootCause model) remains.

2. **Backward compat**: `from_dict` methods silently drop unknown/removed fields rather than raising errors, so old data files still load.

3. **Must-Ask checklist**: All carryover from prior work items (Tkinter GUI, Windows, JSON/YAML files, technical users). No new interface decisions.

## Rationale

- `set_root_cause` is redundant with `CHANGE_STATE` rule outputs. The v2 grammar already captures root cause identification through rule outputs.
- `because` adds token overhead for the LLM and is semantically redundant — the rule's conditions + THEN/ELSE outputs express the reasoning.
- Removing both simplifies the tool schema, system prompt, and GUI display.
