# GCP-0076 Domain Expert Decision Notes

## Assessment

No specialized domain expertise is required. This is internal Python tooling involving filesystem path resolution, YAML registry data, and existing MCP workflow contracts.

## Guidance

- Treat each supplied workspace root as an independent registry boundary.
- Preserve canonical data when canonical and legacy files coexist.
- Keep read-only status resolution non-mutating.
- Preserve nested AgentLoop and test-workspace registries because they belong to distinct workspace roots.
