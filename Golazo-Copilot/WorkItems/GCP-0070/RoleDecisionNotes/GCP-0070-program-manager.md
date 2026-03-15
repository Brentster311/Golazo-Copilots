# GCP-0070 Program Manager Notes

## Planning decisions
- Chosen approach: full removal of `golazo_update` from the MCP surface, not deprecation-only.
- Install guidance will move to the bootstrap spine and README, using the repository's existing Azure Artifacts package location.

## Scope controls
- The work item covers removal of the tool implementation references, public docs, and tests in one slice.
- No replacement MCP tool will be introduced.

## Review focus requested
- Check for hidden legacy references and stale formatter/help text.
- Confirm the new install guidance points to the canonical package location already used by the repo.