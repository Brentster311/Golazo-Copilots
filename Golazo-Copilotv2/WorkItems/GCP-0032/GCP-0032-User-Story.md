# GCP-0032: Bootstrap Version Sync Check

**Status**: BACKLOG

## User Story

- **Title:** Detect and Warn on Stale Bootstrap Instructions
- **As a:** Golazo Copilot workflow user
- **I want:** `gcp_status` to warn when the deployed `.github/copilot-instructions.md` version doesn't match the running package version
- **So that:** I know when my workspace instructions are outdated and need a re-bootstrap

## Out of Scope
- Auto-updating instructions (just warn)
- Checking role file versions
- Changing how gcp_bootstrap deploys files

## Assumptions
- **Assumption (explicit):** Interface type is MCP server (Python library), cross-platform, file-based persistence, technical users
- **Assumption (explicit):** The version is embedded as an HTML comment `<!-- Golazo Copilot Version: X.Y.Z -->` in the instructions file
- **Assumption (explicit):** A simple string comparison of versions is sufficient (no semver range matching)

## Acceptance Criteria
1. [ ] `gcp_status` reads the version from `.github/copilot-instructions.md` if it exists
2. [ ] When the file version doesn't match package `__version__`, status output includes a warning line
3. [ ] When the file version matches or file doesn't exist, no warning is shown
4. [ ] Warning text includes the stale version, current version, and suggests running `gcp_bootstrap`
5. [ ] New tests cover version match, mismatch, and missing file scenarios

## Non-Functional Requirements
- Warning should not block any operations
- No new dependencies

## Telemetry / Metrics Expected
- N/A

## Rollout / Rollback Notes
- Additive change, no breaking impact
