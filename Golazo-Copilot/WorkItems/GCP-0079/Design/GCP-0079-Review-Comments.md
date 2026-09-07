# GCP-0079 Review Comments

## Decision

Approved with explicit boundary tests. The design preserves default POA initialization and makes Planner an opt-in first-item role rather than changing Complete-profile behavior globally.

## Required Clarifications Applied

- Existing project detection means any other direct child under `WorkItems` with `state.json`.
- A failed Planner request must write no state for the requested item.
- Existing non-state artifacts and `capabilities.yaml` do not make a project established.
- Invalid `initial_role` values should be rejected by the MCP schema and defensively by the tool.
- The response and persisted first role-history entry must both identify Planner.

## Risks

- Dispatch forwarding can be missed in either modular or compatibility paths.
- Bootstrap fallback instructions can drift from packaged instructions.
- Existing-item errors currently mention nonexistent `golazo_switch`; this adjacent defect should be corrected while touching creation guidance and covered by a test.

## Architect Notes

Approved. `initial_role` is an additive public input with POA as the stable default. Planner eligibility must be validated before capability-registry creation or state persistence so invalid requests have no workspace side effects. Direct child `state.json` detection is an appropriate local ownership boundary; recursive detection would incorrectly couple nested fixtures or unrelated project data.

No security, privacy, dependency, scalability, or on-call concerns are introduced. The only new attack surface is a constrained enum value already recognized by workflow state and role loading.

