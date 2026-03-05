# GCP-0057 Capability Impact

## Inputs Analyzed
- `golazo-copilot/src/golazo_copilot/tools/golazo_bootstrap.py`
- `golazo-copilot/src/golazo_copilot/server.py`
- `golazo-copilot/tests/test_gcp_bootstrap.py`
- `golazo-copilot/tests/test_server_formatters.py`

## Directly Affected Capabilities
1. **tool-bootstrap**
   - Description: Scaffold workspace instructions, role files, and capability template.
   - Impact: Adds/extends bootstrap mode semantics to support `orchestrator-only` behavior and explicit overwrite semantics.

2. **mcp-server**
   - Description: Tool registration, dispatch, and response formatting.
   - Impact: Adds preflight gating behavior for workflow tools when orchestrator instructions are missing.

## Transitively Affected Capabilities
1. **tool-golazo-update** (dependent)
   - Potential impact: update/install post-actions and guidance may need mode-language alignment.

## Contract Implications
- `golazo_bootstrap` input contract changes are additive:
  - new mode enum includes `orchestrator-only` (default remains existing full behavior for compatibility).
- Workflow tools gain deterministic preflight failure behavior when orchestrator instructions are absent.
- No changes to persisted work-item schema are required for this design.

## Compatibility Assessment
- Backward compatibility is preserved if:
  - mode defaults to full behavior,
  - existing callers without mode parameter continue to work,
  - failure messaging is actionable for newly gated workflow calls.

