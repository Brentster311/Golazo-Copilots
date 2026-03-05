# GCP-0065 Capability Impact

## Scope
Architectural impact analysis for path migration of `capabilities.yaml` to canonical `WorkItems/capabilities.yaml`.

## Files Evaluated
- `golazo-copilot/src/golazo_copilot/tools/golazo_capabilities.py`
- `golazo-copilot/tests/test_gcp_capabilities.py`
- `golazo-copilot/src/golazo_copilot/server.py`
- `golazo-copilot/src/golazo_copilot/handlers/tools.py`

## Directly Affected Capabilities
- `tool-capabilities`: capability registry listing, lookup, impact, and validation
- `mcp-server`: MCP registration/dispatch and formatter-facing behavior

## Transitively Affected Capabilities
- Any capability that depends on accurate `tool-capabilities` impact analysis results may observe changed behavior due to canonical-path enforcement.

## Contract Implications
- Public contract shifts to canonical path: `WorkItems/capabilities.yaml`.
- Backward compatibility is preserved by migration behavior when legacy root `capabilities.yaml` is found and canonical is absent.
- When both canonical and legacy files exist, canonical file remains source of truth.

## Architectural Risk Notes
- File move operations can fail on permission-locked filesystems.
- Conflict handling must be deterministic to avoid non-repeatable outcomes.

## Conclusion
Impact is contained and low-to-moderate risk, with primary sensitivity in filesystem edge cases and deterministic conflict policy.
