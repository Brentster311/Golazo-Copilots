# GCP-0069 Capability Impact

## Capability Registry Status
- Capability registry exists, but current project registry only contains a placeholder example capability.

## Files Reviewed
- `golazo-copilot/src/golazo_copilot/tools/golazo_bootstrap.py`
- `golazo-copilot/src/golazo_copilot/dispatch/paths.py`
- `golazo-copilot/src/golazo_copilot/dispatch/router.py`
- `golazo-copilot/src/golazo_copilot/handlers/tools.py`
- `golazo-copilot/src/golazo_copilot/formatters/results.py`
- `golazo-copilot/src/golazo_copilot/server.py`

## Directly Affected Capabilities
- None reported by `golazo_capabilities(action="impact")`.

## Transitively Affected Capabilities
- None reported by `golazo_capabilities(action="impact")`.

## Contract Implications
- The effective public contract change is the addition of a new optional `scope` input on `golazo_bootstrap`.
- No registered capability contract currently references the affected bootstrap or dispatch files.
- Existing callers remain compatible because omitted or empty `scope` continues to behave as workspace scope.

## Architect Assessment
- The lack of affected capabilities is consistent with the placeholder registry state, not proof that the change is operationally irrelevant.
- Regression protection therefore depends on direct test coverage, especially around dispatcher preflight and bootstrap result formatting.