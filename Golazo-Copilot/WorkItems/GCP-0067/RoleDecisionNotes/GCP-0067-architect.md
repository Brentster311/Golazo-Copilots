# GCP-0067 Architect Decision Notes

## Architectural verdict
- Approved to proceed to implementation with explicit contract-first handling for update target selection.

## Key architecture constraints
- Maintain strict separation of responsibilities:
  - `golazo_status` remains read-only/reporting.
  - `golazo_update` remains state-changing/install action.
- Keep target-resolution logic centralized to avoid divergence between schema validation, runtime execution, and docs.
- Preserve backward compatibility when `target` is not provided.

## Security and resilience review
- No new auth boundary or secret-handling concerns introduced.
- Failure isolation required: invalid target must fail before any install operation is attempted.
- Rollback safety is high: changes are concentrated in tool contract and messaging surfaces.

## Naming and contract notes
- Target vocabulary should be limited and explicit (for example, `active` and `global`) and reused verbatim across code/tests/docs.
- Response payload/message should always include selected target and resulting action path.

## Escalation decision
- No new user story required; current story scope is sufficient for proposed architecture updates.
