# GCP-0059 Capability Impact Analysis

## Scope
Bootstrap output-path contract update only:
- Spine target: `.github/agents/golazo-copilot/orchestrator.md`
- Roles target: `.github/agents/golazo-copilot/roles/...`

No production behavior change beyond output path/name contract alignment.

## Inputs Used for Impact Query
- `golazo-copilot/src/golazo_copilot/tools/golazo_bootstrap.py`
- `golazo-copilot/src/golazo_copilot/server.py`
- `golazo-copilot/tests/test_gcp_bootstrap.py`
- `golazo-copilot/src/golazo_copilot/bootstrap-instructions.md`

## Capability Registry Result
Impact query returned 3 affected capabilities.

### Directly Affected Capabilities
1. **tool-bootstrap**
   - Description: Scaffold workspace and write bootstrap artifacts.
   - Contract relevance: Owns filesystem destination logic for orchestrator/roles outputs.
   - Key files:
     - `golazo-copilot/src/golazo_copilot/tools/golazo_bootstrap.py`
     - `golazo-copilot/src/golazo_copilot/bootstrap-instructions.md`
     - `golazo-copilot/src/golazo_copilot/capabilities-template.yaml`

2. **mcp-server**
   - Description: Registers and routes tool invocations.
   - Contract relevance: Tool metadata/formatting may expose output-path expectations in messages.
   - Key files:
     - `golazo-copilot/src/golazo_copilot/server.py`
     - `golazo-copilot/src/golazo_copilot/__init__.py`

### Transitively Affected Capabilities
1. **tool-golazo-update**
   - Dependency chain: `tool-golazo-update -> mcp-server -> tool-bootstrap`
   - Contract relevance: Update flow messaging references bootstrap invocation; stale path text must not persist.

## Contract Implications
### Public Interfaces
- No new MCP tool introduced.
- No existing MCP tool removed.
- No argument-schema changes required for `golazo_bootstrap(workspace_path, force, include_roles)`.

### Behavioral Contract Changes (Authoritative)
- Bootstrap output contract must be treated as:
  - `.github/agents/golazo-copilot/orchestrator.md`
  - `.github/agents/golazo-copilot/roles/...`
- Legacy path references are considered stale and must be removed from docs/messages/tests in this scope.

## Compatibility and Risk Notes
- Backward compatibility for existing bootstrap flags/defaults remains required.
- Main risk is contract drift (tests/docs/messages using stale paths/filenames).
- Mitigation: centralize path constants and assert both:
  - expected new path exists
  - legacy path is not written in the same successful run

## Security/Operability Notes
- Change does not add network or auth surface.
- Filesystem write/copy failure handling remains security-relevant for deterministic error reporting and avoiding partial artifacts.

## Architect Conclusion
Capability impact is contained and acceptable for implementation under bootstrap-path-only scope. Primary architectural requirement is strict contract consistency across tool implementation, tool metadata/messages, and tests/documentation.