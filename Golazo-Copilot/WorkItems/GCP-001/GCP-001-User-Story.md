# GCP-001: Copy Golazo Copilot Instructions Locally

**Status**: IMPLEMENTED

## User Story

- **Title**: Copy Golazo Copilot Instructions into Repository
- **As a**: Developer using GitHub Copilot with this repository
- **I want**: The Golazo Copilot Instructions (spine and all role files) to exist locally in this repository
- **So that**: Copilot can load and follow the Golazo workflow when working in this project

## Out of Scope
- Modifying or improving the instructions content
- Creating a CLI tool to manage instructions (future work)
- Validation or linting of instruction files
- Any Python code changes

## Assumptions
- **Assumption (explicit)**: The instruction content provided in the initial Copilot context is the authoritative source to copy from.
- **Assumption (explicit)**: Standard `.github/` directory structure is acceptable for storing instructions.
- **Assumption (explicit)**: All 10 role files referenced in the spine need placeholder files created if full content is not available.

## Acceptance Criteria (bulleted, testable)
- [ ] `.github/copilot-instructions.md` exists with the full Golazo spine content
- [ ] `.github/roles/project-owner-assistant.md` exists with full role instructions
- [ ] `.github/roles/program-manager.md` exists (with content or placeholder)
- [ ] `.github/roles/reviewer.md` exists (with content or placeholder)
- [ ] `.github/roles/architect.md` exists (with content or placeholder)
- [ ] `.github/roles/tester.md` exists (with content or placeholder)
- [ ] `.github/roles/developer.md` exists (with content or placeholder)
- [ ] `.github/roles/refactor-expert.md` exists (with content or placeholder)
- [ ] `.github/roles/builder.md` exists (with content or placeholder)
- [ ] `.github/roles/documentor.md` exists (with content or placeholder)
- [ ] `.github/roles/retrospective.md` exists (with content or placeholder)

## Non-functional Requirements
- Files must be valid Markdown
- Files must be UTF-8 encoded
- Directory structure must match paths referenced in the spine document

## Telemetry / Metrics Expected
- None for this work item (file creation only)

## Rollout / Rollback Notes
- Rollout: Commit all files in a single commit for atomic deployment
- Rollback: Revert the commit if issues are found
