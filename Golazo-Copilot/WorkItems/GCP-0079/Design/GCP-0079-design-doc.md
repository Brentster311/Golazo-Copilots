# GCP-0079 Design

## Summary

Add an optional `initial_role` input to `golazo_create_workitem`. The default remains `project-owner-assistant`; `planner` is accepted only for a Complete-profile work item when no other `WorkItems/*/state.json` exists. Packaged orchestrator instructions offer this choice before the first creation call.

## Problem Statement

Planner is positioned before POA but all work items currently initialize at POA. Reaching Planner requires a backward transition after POA notes and User Story outputs exist, contradicting Planner's pre-story purpose.

## Business Case

New initiatives need product direction before story decomposition. The change makes the existing Planner role usable without disrupting established projects or callers. Success is measured by first-item Planner initialization and unchanged default creation behavior.

## Stakeholders

- Users starting new Golazo projects.
- Maintainers of MCP tool schemas, handlers, and bootstrap instructions.
- Existing users relying on POA initialization.

## Requirements

- Expose `initial_role` with values `project-owner-assistant` and `planner`.
- Default to POA.
- Reject Planner unless profile is Complete and no other work-item state exists.
- Initialize current role and first role-history entry consistently.
- Offer the choice in packaged and fallback orchestrator instructions.
- Document the public input and first-project behavior.

## Proposed Approach

1. Extend `create_initial_state` with a validated initial-role argument.
2. Add first-work-item detection in `golazo_create_workitem` using direct child work-item directories containing `state.json`; exclude the requested item before creation and ignore non-directory registry files.
3. Add and forward `initial_role` through `dispatch/registry.py`, `handlers/tools.py`, and the compatibility dispatcher in `server.py`.
4. Update packaged `bootstrap-instructions.md`, bootstrap fallback text, and README.
5. Add focused tests at state, tool, schema/dispatch, bootstrap, and documentation boundaries.

## Alternatives Considered

- Always start Complete in Planner: rejected because the Project Owner requested an offer, not mandatory planning.
- Offer after POA initialization: rejected because it preserves the backward-transition/output-gate defect.
- Infer broad requests automatically: rejected because role selection is a human product decision.

## Risks and Mitigations

- Race between two first creations: existing filesystem persistence is not transactional; validation still narrows accidental misuse without changing concurrency architecture.
- Schema/handler drift: add registry and dispatch tests.
- Existing tests assuming POA: preserve the default argument.
- False positives from `capabilities.yaml`: inspect only child `state.json` files.

## Dependencies

No new dependencies or state migration. Uses `pathlib` and existing state persistence.

## Rollout and Rollback

Release as a backward-compatible minor version. Roll back by removing the optional input and offer guidance; existing Planner-initialized state remains readable because Planner is already a valid role.

## Observability

Creation responses and persisted role history expose the selected initial role. Validation errors explain profile and existing-project restrictions.

## Test Strategy

Test Planner success for the first Complete item; reject Planner for Express, Spike, and an existing state; preserve default POA; verify role history; verify registry/handler forwarding; and assert generated instructions plus README describe the offer.
