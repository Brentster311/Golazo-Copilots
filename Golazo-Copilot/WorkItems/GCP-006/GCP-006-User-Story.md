# GCP-006: Add Versioning to Golazo Instruction Files

**Status**: IN PROGRESS

## User Story

- **Title**: Add Version Metadata to Golazo Spine and Role Files
- **As a**: Developer using Golazo Copilot
- **I want**: Version numbers embedded in the spine file and role files
- **So that**: I can easily identify which version of Golazo instructions I have installed, enabling future update detection

## Out of Scope
- Update detection logic (covered by GCP-007)
- Automated upgrade functionality (covered by GCP-007)
- Version history beyond the current release

## Assumptions
- **Assumption (explicit)**: Semantic versioning (MAJOR.MINOR.PATCH) will be used
- **Assumption (explicit)**: Initial version will be `1.0.0`
- **Assumption (explicit)**: Version metadata will be in a structured format that can be parsed programmatically

## Acceptance Criteria (bulleted, testable)
- [ ] `.github/copilot-instructions.md` contains a version header in format `<!-- Golazo Version: X.Y.Z -->`
- [ ] Each role file in `.github/roles/` contains a matching version comment
- [ ] A `VERSION` file exists at repository root containing only the version string (e.g., `1.0.0`)
- [ ] A `CHANGELOG.md` file exists at repository root documenting changes per version
- [ ] `Golazo_Copilot.py --package` includes `VERSION` and `CHANGELOG.md` in the distribution zip
- [ ] Version format follows semantic versioning (MAJOR.MINOR.PATCH)

## Non-functional Requirements
- Version metadata must not interfere with Copilot's parsing of instructions
- Version must be in a consistent, grep-able format across all files

## Telemetry / Metrics Expected
- None (documentation-only change)

## Rollout / Rollback Notes
- Rollout: Update all MD files with version header, create VERSION and CHANGELOG.md
- Rollback: Remove version comments (non-breaking, comments are ignored)
