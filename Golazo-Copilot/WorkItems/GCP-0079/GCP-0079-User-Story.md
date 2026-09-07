# GCP-0079: Offer Planner for New Projects

**Status**: IMPLEMENTED

**User Story**
- **Title:** Offer Planner before the first work item
- **As a:** Golazo Copilot user starting a new project
- **I want:** The orchestrator to offer Planner before creating the first work item
- **So that:** Broad product direction can be established before POA writes implementation stories
- **Out of scope:** Automatically invoking Planner, changing subsequent work-item defaults, adding Planner to Express or Spike, or changing existing work-item state
- **Assumptions:** **Assumption (explicit):** A brand-new project has no `WorkItems/*/state.json` files. The interface is the existing cross-platform MCP/orchestrator chat flow, and acceptance persists through the new work item's `state.json`.
- **Acceptance Criteria:**
  - Orchestrator instructions require offering Planner or POA before the first work item in a workspace is created.
  - `golazo_create_workitem` accepts an optional initial role and can create the first Complete-profile work item directly in Planner.
  - Planner initialization is rejected for non-Complete profiles and workspaces that already contain another work-item state file.
  - Omitting the initial role preserves the existing POA default for all profiles and later work items.
  - Focused tests and the full Golazo Copilot suite pass, and user-facing documentation explains the behavior.
- **Non-functional requirements:** Preserve backward compatibility, return actionable validation errors, and use filesystem-based detection consistently across Windows, macOS, and Linux.
- **Telemetry / metrics expected:** Existing role history records the selected initial role; no new telemetry.
- **Rollout / rollback notes:** Release as a backward-compatible minor version; revert the creation schema, orchestration guidance, tests, and documentation to roll back.

## Closure

### Delivered

Golazo Copilot now offers Planner or Project Owner Assistant before the first work item in a brand-new project. The optional `initial_role` contract starts an eligible Complete item directly in Planner while preserving POA defaults and rejecting ineligible requests before mutation. Version 6.1.0 artifacts were built and validated.

### Acceptance Criteria

- **PASS:** Packaged and fallback orchestrator instructions require the first-item Planner/POA offer.
- **PASS:** `golazo_create_workitem` accepts `initial_role="planner"` and persists Planner as current role and initial history for the first Complete item.
- **PASS:** Planner is rejected for Express, Spike, and established direct-child work-item state, with no state or registry side effects.
- **PASS:** Omitted and explicit POA behavior preserve the existing default.
- **PASS:** Focused tests passed 12/12, documentation contracts passed 53/53, and the final full suite passed 569/569.

### Future Work

- Isolate legacy server source-loading tests so collection order cannot affect modern module imports.

**Final Status:** IMPLEMENTED
