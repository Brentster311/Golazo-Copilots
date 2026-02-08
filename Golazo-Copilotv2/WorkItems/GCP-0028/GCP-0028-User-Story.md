# GCP-0028: TechBestPractices.md for Technical Roles

**Status**: IN PROGRESS

## User Story

**Title:** Add TechBestPractices.md Reference File for Technical Roles  
**As a:** Developer, Architect, or Refactor Expert using Golazo Copilot  
**I want:** Access to a TechBestPractices.md file containing accumulated technical knowledge  
**So that:** I can avoid known pitfalls and prevent redesigns by following established best practices

## Out of Scope
- Automatic validation/enforcement of best practices
- Best practices for non-technical roles

## Assumptions
- **Assumption (explicit):** The file will be stored in `.github/roles/TechBestPractices.md` alongside other role files
- **Assumption (explicit):** Bootstrap will copy this file like other role files when `include_roles=True`
- **Assumption (explicit):** Users can edit the file after bootstrap to add project-specific practices

## Acceptance Criteria
1. [x] `TechBestPractices.md` exists in default roles with initial content
2. [x] `gcp_bootstrap` copies `TechBestPractices.md` when `include_roles=True`
3. [x] Architect role file references TechBestPractices.md
4. [x] Developer role file references TechBestPractices.md
5. [x] Refactor Expert role file references TechBestPractices.md
6. [x] Initial content includes: "Never use DefaultCredentials from Azure Identity library; instead chain CLI and MSI creds"

## Non-Functional Requirements
- File should be human-readable markdown
- Best practices should be actionable and specific

## Telemetry / Metrics
- N/A

## Rollout / Rollback Notes
- New file, no migration needed
- Existing workspaces can get it by running `gcp_bootstrap(include_roles=True, force=True)`
