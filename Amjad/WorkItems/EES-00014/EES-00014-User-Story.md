# EES-00014: Remove `because` and `set_root_cause` from v2 Grammar

**Status**: IMPLEMENTED

**User Story**

- **Title**: Remove `because` field and `set_root_cause` tool from the codebase
- **As a**: developer maintaining the expert system
- **I want**: the `because` field removed from `Rule` and the `set_root_cause` tool removed from the LLM extractor
- **So that**: the v2 grammar is clean and consistent — root cause identification flows through `CHANGE_STATE` rule outputs, and rules are self-explanatory through their conditions and outputs without a separate `because` field

- **Out of scope**:
  - Removing the Root Causes management tab from the GUI (users can still manage root causes manually)
  - Removing the `RootCause` model or `save/load_root_causes` from the store
  - Changing the `CHANGE_STATE | RULED_OUT | GAP` output kinds

- **Assumptions**:
  - **Assumption (explicit)**: Root cause identification is now fully handled by `CHANGE_STATE` outputs on rules. The separate `set_root_cause` tool is redundant.
  - **Assumption (explicit)**: The `because` field is redundant — a rule's conditions + then/else outputs are self-documenting. Removing it simplifies the schema and reduces LLM token usage.
  - **Assumption (explicit)**: Existing serialized data files may contain `because` and `root_cause` fields. `from_dict` methods should silently ignore these for backward compatibility.

- **Acceptance Criteria** (bulleted, testable):
  - `Rule` dataclass no longer has a `because` field; `to_dict` does not emit it; `from_dict` silently ignores it if present in old data
  - The `set_root_cause` tool definition is removed from `_TOOLS` in `fact_extractor.py`
  - The `_handle_set_root_cause` method is removed from `FactExtractor`
  - `LLMResponse` no longer has a `root_cause` field
  - The system prompt no longer mentions `set_root_cause()` or `because`
  - The `submit_rule` tool schema no longer includes `because` as a parameter
  - GUI KB rules treeview no longer has a "because" column
  - Rule detail dialog no longer shows "Because:" line
  - All existing tests pass (updated to remove `because`/`root_cause` references)

- **Non-functional requirements**:
  - Backward compat: `Rule.from_dict` and `LLMResponse.from_dict` must not crash on old data containing these fields

- **Telemetry / metrics expected**: N/A

- **Rollout / rollback notes**: Existing KB YAML files with `because` fields will continue to load; the field is simply ignored.
