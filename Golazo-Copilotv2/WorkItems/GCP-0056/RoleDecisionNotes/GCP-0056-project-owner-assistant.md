# GCP-0056 — Project Owner Assistant Notes

## Decisions
- **Single work item**: The request describes one user-observable outcome (check for and install a Golazo update), so it stays as a single story.
- **MCP tool interface**: Golazo is an MCP server; adding a new MCP tool is the natural interface. No need to ask about interface type.
- **No persistence needed**: Version info is fetched live from Azure Artifacts each time. No database or file storage required.
- **Two version tiers**: Users see both the latest stable release and the latest pre-release, and can choose which to install. This addresses the user's requirement of "latest version and latest released version."

## Key Parameters Captured
- **Feed URL**: `https://msazure.pkgs.visualstudio.com/One/_packaging/azinsights_accia_pkgs/pypi/simple/`
- **Auth dependencies**: `keyring`, `artifacts-keyring`
- **Auth prerequisite**: `az login`

## Scope Rationale
- Kept to a single tool invocation flow: check → display → (optionally) install.
- Auto-update, scheduling, and downgrade are explicitly out of scope to keep the story small and shippable.
