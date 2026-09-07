# GCP-0072 Domain Expert Decision Notes

## Domain Assessment

GitHub Copilot Agent Skills expertise is required because discovery locations, directory structure, and frontmatter validity determine whether the installed artifact works. The VS Code bundled Agent Skills reference was consulted.

Azure DevOps expertise is not required for this work item. The ADO values are configuration defaults only, and bootstrap performs no Azure DevOps API, authentication, board, or work-item operations.

## Guidance Summary

- Use `.github/skills/golazo-ado-sync/` for workspace scope.
- Use `~/.copilot/skills/golazo-ado-sync/` for user scope.
- Preserve `golazo-ado-sync` as both directory and frontmatter name.
- Copy the complete packaged skill resource tree.
- Preserve valid frontmatter, invocation flags, discovery description, and relative resource links.
- Render into a destination copy and validate before exposing the final installation.
- Keep `orchestrator-only` mode free of skill installation to preserve its stated contract.

## Outcome

No fundamental design flaw or missing user-story requirement was found. Guidance has been added to the shared review comments for Quality Assurance and Architect review.