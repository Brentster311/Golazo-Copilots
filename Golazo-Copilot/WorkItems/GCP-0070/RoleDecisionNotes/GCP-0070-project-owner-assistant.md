# GCP-0070 Project Owner Assistant Notes

## Scope decision
- This is one work item because the user-visible outcome is singular: remove `golazo_update` and replace it with documented install guidance in the orchestrator spine.

## Explicit assumptions
- The interface type is the existing MCP server tool surface and bootstrap-generated instruction files.
- Target platform remains the repository's existing cross-platform Python package behavior, with Windows-sensitive tests preserved where already present.
- Data persistence is file-based in this repository.

## Capability context
- The current capability registry contains only the placeholder `example-capability`, so it does not constrain this scope.

## Scope boundaries
- Included: tool removal, dispatch/registry cleanup, bootstrap spine guidance, related documentation, and tests.
- Excluded: replacing `golazo_update` with another MCP tool, changing the package feed, or broader bootstrap redesign.