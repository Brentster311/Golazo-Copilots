# GCP-0030: Bootstrap Should Target Provided workspace_path, Not Walk Up to .git

**Status**: BACKLOG

## User Story

- **Title:** Fix Bootstrap Workspace Detection to Respect Provided Path
- **As a:** Golazo Copilot user
- **I want:** `gcp_bootstrap(workspace_path=...)` to deploy files into the specified directory
- **So that:** Bootstrap works correctly when the workspace folder is a subfolder of the git repo (e.g., monorepo layouts where `.git` is above the workspace)

## Out of Scope
- Changing how bootstrap detects workspace when no `workspace_path` is provided (auto-detection)
- Changing the bootstrap file structure or content

## Assumptions
- **Assumption (explicit):** Interface type is MCP server (Python library), cross-platform, file-based persistence, technical users (developers)
- **Assumption (explicit):** When `workspace_path` is explicitly provided, bootstrap should use it directly instead of walking up the directory tree looking for `.git`
- **Assumption (explicit):** The current behavior of walking up to find `.git` is correct only when `workspace_path` is NOT provided

## Acceptance Criteria
1. [ ] When `workspace_path` is explicitly provided, bootstrap deploys `.github/` into that exact directory
2. [ ] When `workspace_path` is provided, workspace marker validation (`.git`, `pyproject.toml`, etc.) checks the provided path OR is skipped
3. [ ] When `workspace_path` is NOT provided, existing auto-detection behavior is preserved
4. [ ] Existing bootstrap tests still pass
5. [ ] New test: bootstrap with explicit `workspace_path` to a subfolder that lacks `.git` succeeds

## Non-Functional Requirements
- No breaking changes to existing bootstrap behavior when `workspace_path` is omitted
- Clear error message if provided path doesn't exist

## Telemetry / Metrics Expected
- N/A (local MCP server)

## Rollout / Rollback Notes
- Bug fix, backward compatible
- Existing workspaces unaffected
