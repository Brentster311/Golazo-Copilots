# GCP-0073 Program Manager Decision Notes

## Decisions

- Treat MCP 2.x migration and dependency bounding as one release unit; separating them could produce another unstartable package.
- Preserve the existing Golazo tool contract exactly unless MCP 2.x makes a representation impossible, in which case return to POA rather than silently changing behavior.
- Require protocol startup from the built wheel, not only source-tree imports.
- Test both the minimum supported and latest available MCP 2.x versions.
- Reserve MCP 3.x for a separately validated compatibility release.

## Operational Boundary

This change affects local MCP server startup and package compatibility only. It does not alter work-item state, role transitions, tool semantics, authentication, or external services.

## Rollback Boundary

Rollback must restore a matched Golazo/MCP 1.x package pair. Dependency metadata and server integration must never be rolled back independently.