# GCP-0061 Capability Impact Analysis

## Scope and Method
- Role: Architect
- Work item: `GCP-0061`
- Registry source: root `capabilities.yaml`
- Required command executed: `golazo_capabilities(action="impact", files=[...])`
- Files assessed for impact (from design references and intended refactor surface):
  - `golazo-copilot/src/golazo_copilot/server.py`
  - `golazo-copilot/src/golazo_copilot/dispatch/router.py`
  - `golazo-copilot/src/golazo_copilot/dispatch/registry.py`
  - `golazo-copilot/src/golazo_copilot/handlers/workflow_handlers.py`
  - `golazo-copilot/src/golazo_copilot/handlers/git_handlers.py`
  - `golazo-copilot/src/golazo_copilot/formatters/responses.py`
  - `golazo-copilot/src/golazo_copilot/core/output_validator.py`
  - `golazo-copilot/tests/test_server_dispatch.py`
  - `golazo-copilot/tests/test_server_formatters.py`

## Directly Affected Capabilities and Contracts
1. **mcp-server**
   - Contract impact: internal dispatch/registration/formatting responsibilities are split across modules while preserving existing MCP tool names and response contracts.
   - Compatibility: external behavior remains stable if registration set, required parameters, and response envelopes are kept identical.

2. **output-validation**
   - Contract impact: deterministic output-shape expectations remain relevant to ensuring no contract drift in tool responses and workflow artifact checks.
   - Compatibility: no interface change expected; parity assertions remain mandatory.

## Transitively Affected Capabilities (Downstream Dependents)
1. **tool-transition** (depends on `mcp-server`)
   - Transitive impact: dispatch routing changes must not alter transition invocation semantics or error envelopes.

2. **tool-status** (depends on `mcp-server`)
   - Transitive impact: status tool registration and parameter validation behavior must remain unchanged.

3. **tool-role-context** (depends on `mcp-server`)
   - Transitive impact: role-context invocation path must preserve deterministic success/error shaping.

4. **tool-golazo-update** (depends on `mcp-server`)
   - Transitive impact: update-tool registration and dispatch should remain unaffected by internal decomposition.

## Contract Implications Summary
- **New public interface**: None required for this work item.
- **Changed public interface**: None intended; this is behavior-preserving refactor only.
- **Removed public interface**: None.
- **Internal contract clarifications required**:
  - Dispatch table assembly must map each existing tool name to exactly one handler target.
  - Formatter utilities must preserve current response envelope keys and deterministic error category intent.
  - Validation flow must preserve required-parameter semantics and stable error messaging intent.

## Compatibility and Risk Notes
- Highest contract risk remains registration/required-parameter drift during extraction.
- Validation-order drift can alter user-visible error category/message intent even without schema changes.
- Additional dispatch indirection can introduce latency regression if helper boundaries are over-layered.
- Large refactor slices increase rollback complexity; enforce small reversible slices.

## Architect Decision
- Capability impact is acceptable with non-breaking, parity-constrained implementation.
- No architectural gate failure detected.
- No separate scope-expansion user story is required in this architect pass.
