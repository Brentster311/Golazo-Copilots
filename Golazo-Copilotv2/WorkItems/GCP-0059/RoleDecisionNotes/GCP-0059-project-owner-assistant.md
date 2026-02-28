# GCP-0059 — Project Owner Assistant Notes

## Decision Summary
- Created one focused story for deterministic workflow setup after install.
- Final direction: require bootstrap before workflow operations and provide minimal mode `orchestrator-only`.

## Rationale
- The reported flaw is high impact because install-only users can invoke workflow tools without orchestrator instructions in workspace context.
- Required preflight with explicit remediation is simpler and less token-heavy than runtime fallback text injection.

## Scope Boundaries
- In scope: bootstrap requirement enforcement for workflow tools, `golazo_bootstrap(mode="orchestrator-only")`, docs, and regression tests.
- Out of scope: changing role semantics/required outputs, adding new tools, or auto-bootstrapping on unrelated calls.

## Risks
- Potential friction for first-time users if preflight blocks without clear guidance.
- Backward-compatibility risk if default bootstrap behavior regresses.

## Mitigations
- Return a precise remediation command that uses `golazo_bootstrap(..., mode="orchestrator-only")`.
- Preserve and test existing full/default bootstrap behavior.
