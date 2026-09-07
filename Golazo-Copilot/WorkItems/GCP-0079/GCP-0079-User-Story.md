# GCP-0079: Offer Planner for New Projects

**Status**: IN PROGRESS

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
