# GCP-0079 Architect Notes

## Decision

Approved as an additive MCP contract. Keep offer presentation in instructions, validation in the creation tool, and state construction in `core.state`.

## Constraints

- Validate before any mutation.
- Scan only direct work-item child directories for `state.json`.
- Preserve POA defaults and state-schema compatibility.
- Test every dispatch adapter and both instruction sources.

## Security and Operations

No secrets, identity, network, dependency, or data-retention behavior changes. Error messages should identify the invalid profile or established-project condition without exposing file contents.