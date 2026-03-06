# GCP-0067 Capability Impact

## Scope
Impact analysis for clarifying `golazo_status` vs `golazo_update` semantics and adding deterministic update target-selection behavior.

## Files Evaluated
- `golazo-copilot/src/golazo_copilot/tools/golazo_update.py`
- `golazo-copilot/src/golazo_copilot/server.py`
- `golazo-copilot/src/golazo_copilot/dispatch/registry.py`
- `golazo-copilot/README.md`
- `golazo-copilot/tests/test_golazo_update.py`
- `golazo-copilot/tests/test_gcp_status.py`
- `golazo-copilot/tests/test_gcp_status_parallel.py`
- `golazo-copilot/tests/test_server_dispatch.py`
- `golazo-copilot/tests/test_server_formatters.py`

## Directly Affected Capabilities
- `tool-update`
  - Contract area: update action semantics, argument schema, install target resolution, and response messaging.
- `mcp-server`
  - Contract area: tool descriptions/registration metadata and formatter output clarity for status/update tools.

## Transitively Affected Capabilities
- No additional transitive capabilities reported by capability registry for this file set.

## Contract Implications
- Public behavior contract changes are additive and clarifying:
  - `golazo_status`: clarified to reporting/read-only semantics.
  - `golazo_update`: clarified to action semantics with explicit/validated target selection behavior.
- Backward compatibility requirement: omitted target must preserve existing caller behavior.
- Error contract addition: invalid/unsupported target must return deterministic, actionable error output.

## Security and Operability Notes
- No new secrets or external trust boundary changes introduced.
- Primary operational risk is user confusion from terminology drift; mitigated by single enum contract and consistent wording across schema/runtime/docs.

## Conclusion
Change set affects `tool-update` and `mcp-server` capabilities directly, with bounded blast radius and no registry-indicated transitive capability impact.
