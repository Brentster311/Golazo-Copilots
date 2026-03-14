# GCP-0069 Architect Decision Notes

## Summary
- Architecture review passed with no need for a new work item.
- The design is sound if instruction lookup is centralized and the bootstrap `scope` contract is validated explicitly.

## Key Architectural Decisions
- Use one shared path-resolution helper for workspace and user instruction lookup.
- Keep the new `scope` parameter optional and backward compatible.
- Update both modular and legacy dispatch/preflight paths to avoid split behavior.

## Security and Risk Notes
- No new network, auth, secret, or dependency risks are introduced.
- Main regression risk is partial implementation across duplicated dispatch paths.
- Main operability risk is unclear bootstrap output; expose effective target path in the result.

## Capability Registry Result
- `golazo_capabilities(action="impact")` reported no affected capabilities for the planned file set.