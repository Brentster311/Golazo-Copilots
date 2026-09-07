# GCP-0074 Project Owner Assistant Decision Notes

## Origin

Created from the GCP-0072 retrospective after `golazo_transition_workitem` rejected completed GCP-0071 because its current role was POA closure rather than retrospective, despite version 5.0.2 guidance requiring POA to close every profile.

## Scope

- Align the existing project-level finalization tool with POA closure semantics.
- Preserve retrospective completion and closure artifacts as mandatory evidence.
- Cover success, premature finalization, missing closure, and retry behavior.
- Keep profile role sequences unchanged.

## Backlog State

This work item is defined at Project Owner Assistant only. No design, state migration, implementation, test, or documentation change has been started.

## Closure Validation

- AC1 PASS: valid completed POA closure finalizes and computes the next work-item ID.
- AC2 PASS: premature roles, forged closure state, missing evidence, and non-implemented status are rejected before global-state mutation.
- AC3 PASS: retry remains idempotent and records the completed item once.
- AC4 PASS: MCP registry, README, tests, and closure guidance consistently describe POA closure finalization.
- Release 6.0.1 built successfully; full tests, coverage, Ruff, and capability validation passed.
- No UI/UX acceptance criteria required Project Owner runtime sign-off.