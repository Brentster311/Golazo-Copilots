# GCP-0076 Project Owner Assistant Decision Notes

## Scope Decision

This is one user-observable outcome: all Golazo capability reporting uses one trustworthy workspace registry. Path alignment, stale-file cleanup, registry population, and regression tests are inseparable parts of that outcome.

## Boundaries

- Preserve AgentLoop's independent canonical registry.
- Preserve test-local fixtures that represent isolated workspaces.
- Remove only obsolete duplicate registries belonging to the top-level Golazo workspace.
- Do not add automatic source-code inference or a registry mutation MCP API.

## Acceptance Strategy

Validate canonical path behavior through focused tool tests, validate populated key files through the MCP tool, and assert stale same-project registries are absent from the repository layout.
