# GCP-008: Extract Technical Guides from Spine for Improved Copilot Interop

**Status**: IMPLEMENTED

## User Story

- **Title**: Extract PowerShell and Golazo Update content into separate technical guide files
- **As a**: Golazo workflow user
- **I want**: Context-specific technical instructions extracted into dedicated guide files
- **So that**: GitHub Copilot loads only relevant instructions when needed, reducing context window usage and improving response quality

## Out of Scope

- Creating new workflow roles (PowerShell and Update are guides, not roles)
- Changing the sequential role workflow (Project Owner ? PM ? Reviewer ? etc.)
- Modifying DoR/DoD gate enforcement
- Changing artifact paths or naming conventions
- Changing role responsibilities
- Creating a shared-definitions file for common rules
- Implementing keyword-based automatic loading

## Assumptions

- **Assumption (explicit)**: Extracting ~130 lines from the spine into separate files will improve Copilot's context efficiency
- **Assumption (explicit)**: Explicit references in the spine (e.g., "consult `.github/guides/powershell-terminal.md`") are sufficient for Copilot to load guides when relevant
- **Assumption (explicit)**: Version bump to 1.1.0 is appropriate for this structural refactor (minor version = backward-compatible change)

## Acceptance Criteria (bulleted, testable)

- [ ] New file `.github/guides/powershell-terminal.md` exists containing all PowerShell/encoding rules currently in spine
- [ ] New file `.github/guides/golazo-update.md` exists containing all Golazo update logic currently in spine
- [ ] Both guide files include version header `<!-- Golazo Version: 1.1.0 -->`
- [ ] Spine (`copilot-instructions.md`) is reduced by ~130 lines with references to the new guides
- [ ] Spine includes a "Context-Specific Guides" section listing when to load each guide
- [ ] All existing Golazo workflow behavior remains unchanged (roles, gates, artifact paths)
- [ ] VERSION file updated to `1.1.0`
- [ ] CHANGELOG.md updated with GCP-008 entry

## Non-functional Requirements

- Guide files should be self-contained (usable without reading the spine first)
- Guide files should include clear "when to use" headers
- Extraction should be clean cut (no partial duplication between spine and guides)

## Telemetry / Metrics Expected

- Manual verification: Golazo workflow still functions correctly after extraction
- Manual verification: Copilot can reference guides when terminal operations or updates are discussed

## Rollout / Rollback Notes

- **Rollout**: Update all files in single commit; include guides in upgrade file list
- **Rollback**: Revert commit; guides are additive so rollback is clean
- **Upgrade impact**: GCP-007 upgrade logic must be updated to include new guide files in download list
