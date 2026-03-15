# GCP-0070 Capability Impact

## Capability Registry Result
- Impact analysis completed for:
  - `golazo-copilot/src/golazo_copilot/dispatch/registry.py`
  - `golazo-copilot/src/golazo_copilot/handlers/tools.py`
  - `golazo-copilot/src/golazo_copilot/formatters/results.py`
  - `golazo-copilot/src/golazo_copilot/server.py`
  - `golazo-copilot/src/golazo_copilot/tools/golazo_update.py`
  - `golazo-copilot/README.md`

## Directly Affected Capabilities
- None reported by the current capability registry.

## Transitively Affected Capabilities
- None reported by the current capability registry.

## Contract Implications
- The public MCP tool contract removes `golazo_update`.
- No capability-registry contracts were reported as affected because the current registry contains only a placeholder entry.

## Notes
- Capability analysis was still performed and recorded even though the registry did not map the touched files to any real capabilities.
