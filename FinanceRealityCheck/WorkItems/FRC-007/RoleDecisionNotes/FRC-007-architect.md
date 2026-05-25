# FRC-007 Architect Notes

## Architecture decision
- Introduce connector protocol abstraction implemented by fixture and direct connectors.
- Keep planner run_sync orchestration unchanged; behavior varies by injected connector implementation.

## Constraints
- Preserve encrypted credential storage path.
- Keep failure categories stable and actionable.
- Avoid coupling direct connector internals to planner persistence schema.
