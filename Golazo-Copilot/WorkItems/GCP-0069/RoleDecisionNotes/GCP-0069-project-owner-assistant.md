# GCP-0069 Project Owner Assistant Decision Notes

## Inputs Confirmed
- Request: add a new `scope` parameter to bootstrap with `User` and `Workspace` options.
- Existing interface type: MCP tool/API surface in the Golazo Copilot server.
- Existing persistence target: file-system instruction files under workspace or user Copilot directory.
- Existing user problem: workflow preflight fails when the running agent is installed from a user directory such as `C:\Users\brentj\.copilot`.

## Scope Decisions
- Chosen scope: one backward-compatible work item covering bootstrap parameter addition plus workflow instruction resolution needed to make user-scope installs actually work.
- Rationale: parameter-only support would be incomplete unless the create-workitem preflight also recognizes user-scope instructions.
- Preserved default: workspace remains the default scope when `scope` is omitted or empty.

## Assumptions Made (Explicit)
- The correct user-scope destination is the active Copilot user directory used by the running agent environment.
- Only orchestrator instruction placement and lookup required for workflow operations are in scope.
- Existing role files and broader bootstrap structure should remain unchanged unless needed by the new destination handling.

## Acceptance Criteria Design Notes
- Kept to 5 criteria and made each directly testable.
- Included both bootstrap output behavior and downstream workflow validation behavior because the user-reported failure happens during workflow operations, not just bootstrap.

## Tech Best Practices and Capability Context Review
- Reviewed `.github/agents/golazo-copilot/roles/TechBestPractices.md`.
- No cloud, identity, or Kusto-specific practices apply to this file-system and workflow-routing change.
- Capability registry currently contains only a placeholder capability, so no existing capability contracts constrain the story.

## Decomposition Check
- Decomposition not required: the feature is one user-visible outcome, enabling agent bootstrap and workflow use from either workspace or user scope without changing default behavior.