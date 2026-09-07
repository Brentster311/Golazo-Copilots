# GCP-0079 Product Vision

## Mission

Let new Golazo projects establish product direction before implementation stories without forcing planning on users who already have a well-defined request.

## Vision

When a workspace has no work-item state, the orchestrator offers a clear choice: begin with Planner for broad or strategic work, or begin with Project Owner Assistant for an already-scoped request. The selected role becomes the work item's true initial state rather than a backward transition.

## Goals

- Make Planner discoverable at the moment it is useful.
- Preserve explicit human choice.
- Keep existing creation calls and later work items unchanged.
- Ensure role history accurately starts with the selected role.

## In-Scope Themes

- First-work-item detection.
- Orchestrator guidance for presenting the choice.
- MCP creation support for Planner initialization.
- Clear validation and documentation.

## Out-of-Scope Themes

- Automatic role selection based on request text.
- Planner support in Express or Spike.
- Retrofitting existing work items.
- Multi-story initiative management.

## High-Level Architecture Direction

Keep presentation policy in orchestrator instructions and eligibility enforcement in the creation tool. Reuse the existing persisted role and role-history model so no state schema migration is needed.

## Risks and Assumptions

- Filesystem detection must ignore non-work-item files such as `capabilities.yaml` and `global_state.json`.
- Concurrent first-item creation remains governed by existing filesystem behavior.
- The offer depends on the orchestrator following deployed instructions.

## Open Questions

None. The Project Owner selected the pre-creation offer with POA as the default decline path.

## Suggested POA Handoff Slice

Implement one backward-compatible creation option and the corresponding orchestrator offer, validation, tests, and user documentation.
