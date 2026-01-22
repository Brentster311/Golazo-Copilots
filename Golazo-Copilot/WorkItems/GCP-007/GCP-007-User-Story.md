# GCP-007: Golazo Copilot Update Detection and Upgrade

**Status**: BACKLOG

## User Story

- **Title**: Detect Golazo Updates and Offer Upgrade via Copilot
- **As a**: Developer using Golazo Copilot in Visual Studio
- **I want**: Copilot to detect when a newer version of Golazo is available and offer to upgrade
- **So that**: I can keep my Golazo instructions current without manually checking the repository

## Out of Scope
- Automatic updates without user consent
- Version checking for non-GitHub sources (Azure Artifacts, etc.)
- Downgrade functionality
- Offline update detection

## Assumptions
- **Assumption (explicit)**: GCP-006 is complete (version metadata exists in files)
- **Assumption (explicit)**: Users have internet access to reach raw.githubusercontent.com
- **Assumption (explicit)**: PowerShell is available on Windows (for Invoke-WebRequest)
- **Assumption (explicit)**: Copilot has access to `run_command_in_terminal` tool

## Acceptance Criteria (bulleted, testable)
- [ ] Copilot instructions include a section defining update check behavior
- [ ] On session start, Copilot can fetch remote VERSION file from GitHub
- [ ] Copilot compares remote version to local version (from spine file comment)
- [ ] If remote version is newer, Copilot displays: current version, new version, and changelog summary
- [ ] Copilot asks user for confirmation before upgrading
- [ ] If user confirms, Copilot downloads updated MD files to `.github/` directory
- [ ] After upgrade, Copilot reports success and new version number
- [ ] If upgrade fails, Copilot reports error and suggests manual steps

## Non-functional Requirements
- Update check should not block the user's workflow (informational, not mandatory)
- Update check should timeout gracefully if network is unavailable
- Upgrade process must not corrupt existing files (atomic replacement)
- Backup existing files before overwriting (to `.github/backup/`)
- Track "last checked" timestamp to avoid repeated checks every session

## Telemetry / Metrics Expected
- None (runs locally in user's IDE)

## Rollout / Rollback Notes
- Rollout: Add update-check instructions to spine file
- Rollback: Remove update-check section from spine (Copilot returns to previous behavior)

## Confirmed Design Decisions
- Update source branch: `main`
- Backup before upgrade: Yes (to `.github/backup/`)
- Track last checked: Yes (timestamp in local file)
