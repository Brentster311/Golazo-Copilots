# GCP-0060 Capability Impact Analysis

## Scope and Method
- Role: Architect
- Work item: `GCP-0060`
- Registry source: root `capabilities.yaml`
- Required command executed: `golazo_capabilities(action="impact", files=[...])`
- Files assessed for impact (from design references and implementation surface):
  - `golazo-copilot/src/golazo_copilot/core/types.py`
  - `golazo-copilot/src/golazo_copilot/core/persistence.py`
  - `golazo-copilot/src/golazo_copilot/server.py`
  - `golazo-copilot/src/golazo_copilot/tools/golazo_create_workitem.py`
  - `golazo-copilot/src/golazo_copilot/tools/golazo_transition.py`
  - `golazo-copilot/src/golazo_copilot/tools/golazo_status.py`
  - `golazo-copilot/src/golazo_copilot/tools/golazo_git_propose.py` (new tool target)

## Directly Affected Capabilities and Contracts
1. **state-model**
   - Contract impact: `WorkItemState` evolves to include backward-compatible `git_actions` list defaulting to `[]`.
   - Compatibility: additive field; existing readers remain valid when defaults are applied.

2. **persistence**
   - Contract impact: `load_state`/`save_state` must preserve `git_actions` across round-trips without mutation of prior entries.
   - Compatibility: unchanged method signatures; stronger behavioral guarantee (append-only history integrity).

3. **tool-create-workitem**
   - Contract impact: initialization path should produce schema-valid state inclusive of `git_actions` default.
   - Compatibility: no API shape change; state baseline becomes richer.

4. **tool-transition**
   - Contract impact: reads/writes of state must remain compatible with additional `git_actions` field.
   - Compatibility: no transition semantics change expected.

5. **tool-status**
   - Contract impact: status loading/serialization should tolerate and preserve `git_actions`; no required status payload extension in this item.
   - Compatibility: no API shape change required.

6. **mcp-server**
   - Contract impact: tool registry expands with `golazo_git_propose` and deterministic response envelope for proposal validation failures.
   - Compatibility: additive tool registration; existing tools unchanged.

## Transitively Affected Capabilities (Downstream Dependents)
1. **tool-golazo-update** (depends on `mcp-server`)
   - Transitive impact: none functionally expected; verify server registration changes do not affect update routing.

2. **tool-consent** (depends on state/persistence)
   - Transitive impact: state schema expansion should remain non-breaking for deviation consent flows.

3. **tool-role-context** (depends on persistence/transitions)
   - Transitive impact: context assembly should continue reading state successfully with additive `git_actions` field present.

## Contract Implications Summary
- **New public interface**:
  - MCP tool contract: `golazo_git_propose(action, work_item_id, files?, message?, branch?, workspace_path) -> dict`
- **Changed public interface**:
  - `WorkItemState` data contract becomes explicitly additive with `git_actions: list` default semantics.
- **Removed public interface**:
  - None.

## Compatibility and Risk Notes
- Additive schema update is backward-compatible only if defaults are consistently applied on all load paths.
- Error contract must be stable and machine-assertable (`parameter_required` + missing field name) to protect QA assertions.
- Timestamp must be normalized as UTC ISO-8601 with trailing `Z` to avoid cross-platform audit drift.
- Persistence must hard-fail on write errors; no partial success responses.

## Architect Decision
- Capability impact is acceptable with additive, non-breaking contracts.
- No architectural gate failure detected.
- No separate scope-expansion user story is required for this pass.
